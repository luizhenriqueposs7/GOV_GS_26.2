import unittest
from unittest.mock import MagicMock, patch
import httpx

try:
    import verificar_prontidao as prontidao
except ImportError:
    prontidao=None

class ProntidaoTest(unittest.TestCase):
    def preparar(self, falha=None, historico=False):
        self.assertIsNotNone(prontidao,'O diagnóstico operacional ainda não existe.')
        respostas={
            '/api/status':{'status':'ok','servico':'Central CitizenTech'},
            '/api/fontes':[{'text':'Ações comunitárias de prevenção.','url':'https://www.gov.br/exemplo','paginas':[1]}],
            '/api/ativos':[{'id':i,'modo':'Modo documentado'} for i in ['rpa','cluster','quantica','frontend','genai','iot','pln','visao','governanca']],
            '/api/visao':{'modelo':'ResNet18','escore':.2,'classe':'Sem fissura sinalizada'},
            '/api/assistente':{'status':'respondido','fonte':{'url':'https://prefeitura.sp.gov.br/exemplo'},'historico':historico},
        }
        cliente=MagicMock()
        def responder(method,path,**kwargs):
            return httpx.Response(503 if path==falha else 200,json=respostas[path],request=httpx.Request(method,'http://127.0.0.1:8840'+path))
        cliente.request.side_effect=responder
        cm=MagicMock();cm.__enter__.return_value=cliente
        return cm,cliente

    def executar(self,**kwargs):
        cm,cliente=self.preparar(**kwargs)
        with patch.object(prontidao.httpx,'Client',return_value=cm),patch.object(prontidao,'verificar_fluxo_integrado',return_value={'resultado':'passou','etapas':['registrar','revisar','contestar']}):
            resultado=prontidao.executar()
        return resultado,cliente

    def test_diagnostico_executa_integracoes_sem_vincular_a_pedidos_reais(self):
        resultado,cliente=self.executar()
        self.assertTrue(resultado['ok'])
        self.assertEqual(len(resultado['verificacoes']),7)
        self.assertEqual(resultado['teste_fisico'],'pendente')
        for chamada in cliente.request.call_args_list:
            if chamada.args[0]=='POST':
                self.assertNotIn('atendimento_id',chamada.kwargs.get('json',{}))
                self.assertNotIn('atendimento_id',chamada.kwargs.get('data',{}))

    def test_falha_da_ia_nao_e_tratada_como_plataforma_pronta(self):
        resultado,_=self.executar(falha='/api/assistente')
        self.assertFalse(resultado['ok'])
        self.assertTrue(any(not r['ok'] and r['nome']=='Generative AI' for r in resultado['verificacoes']))
        self.assertEqual(len(resultado['verificacoes']),7)

    def test_resposta_historica_nao_substitui_execucao_atual(self):
        resultado,_=self.executar(historico=True)
        self.assertFalse(resultado['ok'])

if __name__=='__main__':unittest.main()
