import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


class PlanejamentoAPITest(unittest.TestCase):
    def setUp(self):
        from central.app import criar_app
        self.pasta = tempfile.TemporaryDirectory(); self.addCleanup(self.pasta.cleanup)
        ambiente=patch.dict('os.environ',{'GOV_MANAGER_KEY':'chave-planejamento-teste'})
        ambiente.start(); self.addCleanup(ambiente.stop)
        self.app=criar_app(Path(self.pasta.name)); self.client=TestClient(self.app); self.addCleanup(self.client.close)
        self.chave={'X-Manager-Key':'chave-planejamento-teste'}
        self.casos=[self.client.post('/api/atendimentos',json=dict(descricao='Cenário de teste: calçada com barreira '+str(i),
                   bairro='Bairro de demonstração',local='Praça fictícia',contexto='area_publica',confirmado=True)).json() for i in range(3)]
        self.entrada=dict(capacidade=20,itens=[dict(id=c['id'],minutos=10,prioridade=p,obrigatorio=False)
                           for c,p in zip(self.casos,['Alta','Média','Baixa'])])

    def test_planejamento_protegido_persiste_decisao_sem_decidir_casos(self):
        self.assertEqual(self.client.post('/api/planejamento/simular',json=self.entrada).status_code,401)
        r=self.client.post('/api/planejamento/simular',json=self.entrada,headers=self.chave)
        self.assertEqual(r.status_code,200,r.text); sim=r.json()
        aprovar={**self.entrada,'base':sim['base'],'metodo':'classico','revisor':'Gestor do cenário',
                 'justificativa':'Pesos e estimativas conferidos para organizar a revisão.','confirmado':True}
        r=self.client.post('/api/planejamento/planos',json=aprovar,headers=self.chave)
        self.assertEqual(r.status_code,201,r.text)
        for c in self.casos:
            caso=self.client.get('/api/atendimentos/'+c['id']).json()
            self.assertIsNone(caso['revisao']); self.assertNotIn('frontend',caso)
            self.assertEqual(caso['historico'][-1]['acao'],'Planejamento de revisão registrado')
            self.assertEqual(caso['evidencias'][-1]['modulo'],'planejamento_revisao')
        self.assertEqual(self.client.post('/api/planejamento/planos',json=aprovar,headers=self.chave).status_code,409)
        self.assertEqual(len(self.client.get('/api/planejamento').json()['planos']),1)

    def test_alteracao_ou_revisao_exige_recalcular(self):
        sim=self.client.post('/api/planejamento/simular',json=self.entrada,headers=self.chave)
        self.assertEqual(sim.status_code,200,sim.text)
        self.client.post('/api/atendimentos/'+self.casos[0]['id']+'/contestacao',json={'motivo':'Conferir novamente a condição declarada.'})
        r=self.client.post('/api/planejamento/planos',headers=self.chave,json={**self.entrada,'base':sim.json()['base'],
            'metodo':'qaoa','revisor':'Gestor','justificativa':'Decisão anterior à atualização do pedido.','confirmado':True})
        self.assertEqual(r.status_code,409,r.text)

    def test_nao_aceita_resultado_forjado_ou_obrigatorios_sem_capacidade(self):
        self.assertEqual(self.client.post('/api/planejamento/simular',headers=self.chave,
            json={**self.entrada,'selecionados':[self.casos[0]['id']]}).status_code,422)
        dados={**self.entrada,'capacidade':5,'itens':[{**self.entrada['itens'][0],'obrigatorio':True}]}
        self.assertEqual(self.client.post('/api/planejamento/simular',headers=self.chave,json=dados).status_code,422)

    def test_lote_atomico_desfaz_primeiro_registro_se_o_segundo_falhar(self):
        repo=self.app.state.repo
        inicial=len(repo.listar()); criar=repo.criar; chamadas=[]
        def falhar(dados):
            chamadas.append(dados)
            if len(chamadas)==2:raise RuntimeError('Falha controlada de persistência')
            return criar(dados)
        dados={k:self.casos[0][k] for k in ('descricao','bairro','local','contexto','triagem_original','preparacao')}
        with patch.object(repo,'criar',side_effect=falhar),self.assertRaises(RuntimeError):
            repo.criar_em_lote([dados,{**dados,'descricao':'Outro registro do lote temporário.'}])
        self.assertEqual(len(repo.listar()),inicial)

    def test_worker_e_cluster_exigem_chave(self):
        self.assertEqual(self.client.post('/api/cluster/worker',json=dict(worker=1,lote_id='00000000-0000-0000-0000-000000000000',csv='x')).status_code,401)
        csv=b'case_id,description,neighborhood\n001,Calcada danificada no teste,Bairro ficticio\n'
        r=self.client.post('/api/cluster/lotes',files={'arquivo':('lote.csv',csv,'text/csv')},data={'workers':'2'})
        self.assertEqual(r.status_code,401,r.text)

    def test_cluster_grava_analise_do_worker_e_preserva_reaplicacao(self):
        from central import modulos
        csv=b'case_id,description,neighborhood\n001,Calcada danificada no teste,Bairro ficticio\n002,Poste com lampada apagada,Bairro ficticio\n'
        with patch.object(modulos,'triagem',side_effect=AssertionError('Triagem serial não deve substituir a dos workers')):
            r=self.client.post('/api/cluster/lotes',headers=self.chave,files={'arquivo':('lote.csv',csv,'text/csv')},data={'workers':'4'})
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()['workers_executados'],2)
        self.assertEqual(r.json()['workers_solicitados'],4)
        id=r.json()['atendimentos'][0]
        caso=self.client.get('/api/atendimentos/'+id).json()
        self.assertEqual(caso['origem_id'],'rpa:001')
        self.assertIsInstance(caso['triagem_original']['review_required'],bool)
        self.assertEqual(caso['evidencias'][-1]['modulo'],'cluster')
        self.client.post('/api/atendimentos/'+id+'/revisao',headers=self.chave,json=dict(
            prioridade='Alta',revisor='Gestor',justificativa='Conferida a barreira do exemplo.'))
        r=self.client.post('/api/cluster/lotes',headers=self.chave,files={'arquivo':('lote.csv',csv,'text/csv')},data={'workers':'2'})
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()['atendimentos'][0],id)
        self.assertEqual(self.client.get('/api/atendimentos/'+id).json()['revisao']['prioridade'],'Alta')
        worker=self.client.post('/api/cluster/worker',headers=self.chave,json=dict(worker=4,
            lote_id='00000000-0000-0000-0000-000000000000',csv=csv.decode()))
        self.assertEqual(worker.status_code,200,worker.text)

    def test_falha_de_worker_nao_grava_casos(self):
        from central import cluster
        antes=len(self.app.state.repo.listar())
        csv=b'case_id,description,neighborhood\n001,Calcada danificada no teste,Bairro ficticio\n'
        with patch.object(cluster,'processar_worker',side_effect=RuntimeError('Falha controlada')):
            r=self.client.post('/api/cluster/lotes',headers=self.chave,files={'arquivo':('lote.csv',csv,'text/csv')},data={'workers':'2'})
        self.assertEqual(r.status_code,503,r.text)
        self.assertEqual(len(self.app.state.repo.listar()),antes)
