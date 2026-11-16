import {criarMapa} from './mapa.mjs';

const estados={barreira:'Barreira informada',nao_verificado:'Condição desconhecida',
  reparo_hipotetico:'Reparo hipotético',livre_no_cenario:'Livre apenas no cenário'};
const resultados={interrompido:'Passagem interrompida',incerto:'Ainda falta verificar',
  sem_barreiras_informadas:'Continuidade no cenário'};

export function iniciarPassagem({api,enviar,el,botao,badge,data,aviso,durante,abrir,revisar,evidencias,novo}) {
  const $=id=>document.getElementById(id), selecionados=new Set();
  let mapa, dados, rodada=0;
  async function atualizar() {
    const atual=++rodada;dados=null;$('passagem-salvar').disabled=true;
    try {
      const percurso=await api('/api/passagem');
      if(atual!==rodada)return;
      for(const id of selecionados)if(!percurso.trechos.some(t=>t.id===id&&t.atual==='barreira'))selecionados.delete(id);
      const simulado=await enviar('/api/passagem/simular',{reparos:[...selecionados]});
      if(atual!==rodada)return;
      dados={...simulado,planos:percurso.planos.map(p=>({...p,desatualizado:p.base!==simulado.base}))};
      renderizar();
    } catch(erro){if(atual===rodada)aviso(erro.message,true);}
  }
  function comparar(resumo,titulo,classe) {
    const box=el('div',null,'passage-outcome '+classe);
    box.append(el('p',titulo,'tool-kind'),el('h2',resultados[resumo.estado]),
      el('p',resumo.barreiras+' de '+resumo.total_trechos+' trechos com barreira informada'),
      el('p',resumo.desconhecidos+' com condição desconhecida','fine'));
    return box;
  }
  function renderizar() {
    const foco=document.activeElement?.dataset.reparo;
    if(!mapa)mapa=criarMapa('mapa-passagem','mapa-passagem-status',null,'Cenário do mapa: condições informadas e reparos hipotéticos selecionados. As mesmas condições estão na lista.');
    mapa?.resize();mapa?.trechos(dados.trechos);
    const lista=$('passagem-trechos');lista.replaceChildren();
    dados.trechos.forEach(t=>{
      const card=el('article',null,'passage-segment'),cabecalho=el('div',null,'passage-segment-title');
      cabecalho.append(el('h3',t.nome),badge(estados[t.atual],t.atual==='barreira'?'orange':''));card.append(cabecalho);
      card.append(el('p','Agora: '+estados[t.atual]+' → Na hipótese: '+estados[t.simulado],'fine'));
      if(t.tem_condicao_desconhecida)card.append(el('p','Há condição não verificada neste trecho. O reparo simulado não resolve essa falta de informação.','inset warning'));
      if(t.atual==='livre_no_cenario')card.append(el('p','Condição suposta pelo cenário didático; sem observação em campo.','fine'));
      if(!t.pedidos.length&&t.atual==='nao_verificado')card.append(el('p','Não há relato sobre a condição. Selecionar um reparo não preenche essa informação.','fine'));
      t.pedidos.forEach(c=>{
        const pedido=el('div',null,'passage-report');
        if(c.foto){const img=el('img',null,'passage-thumb');img.src='/api/atendimentos/'+encodeURIComponent(c.id)+'/foto?v='+c.foto.sha256;img.alt='Foto do pedido associado';img.loading='lazy';pedido.append(img);}
        const condicao={bloqueado:'Passagem interrompida',dificultado:'Passagem dificultada',nao_verificado:'Condição não verificada'}[c.passagem.condicao];
        pedido.append(el('p',c.descricao),el('small',condicao+' · Registro '+c.id.slice(0,8)+' · '+(c.revisao?'Revisão atual registrada':'Revisão pendente')));
        if(c.atendimento?.etapa==='correcao_verificada')pedido.append(el('p','Barreira deste pedido desconsiderada após conferência humana '+(c.atendimento.demonstracao?'de demonstração':'do protótipo')+'. Outras barreiras e condições desconhecidas permanecem.','inset'));
        const acoes=el('div',null,'actions');
        acoes.append(botao('Pedido e contestação',()=>abrir(c.id),'quiet'),botao('Revisar',()=>revisar(c.id),'quiet'),botao('Consultar evidências',()=>evidencias(c.id),'quiet'));pedido.append(acoes);card.append(pedido);
      });
      if(t.atual==='barreira') {
        const label=el('label',null,'check passage-repair'),check=el('input');check.type='checkbox';check.checked=selecionados.has(t.id);check.dataset.reparo=t.id;
        check.setAttribute('aria-label','Simular reparo: '+t.nome);
        check.addEventListener('change',()=>{if(check.checked)selecionados.add(t.id);else selecionados.delete(t.id);atualizar();});
        label.append(check,el('span','Simular remoção das barreiras deste trecho'));card.append(label);
      }
      card.append(botao('Registrar observação neste trecho',()=>novo(t.id),'secondary'));lista.append(card);
    });
    const comparacao=$('passagem-comparacao');comparacao.replaceChildren(
      comparar(dados.atual,'Condições informadas agora','current'),
      comparar(dados.simulado,'Hipótese com '+dados.reparos.length+' trecho(s) reparado(s)','proposed'));
    if(dados.reparos.length)comparacao.append(el('p',dados.simulado.estado==='sem_barreiras_informadas'
      ?'O conjunto removeria as barreiras informadas neste cenário. A execução e a passagem real ainda precisariam ser verificadas.'
      :dados.simulado.estado==='incerto'?'A hipótese ainda depende de verificar condições desconhecidas.'
      :'Ainda há barreira informada em outro trecho. O reparo selecionado não completa a ligação.','passage-explanation'));
    else comparacao.append(el('p','Selecione uma barreira e depois combine os reparos para comparar o efeito no percurso.','passage-explanation'));
    const pendencias=$('passagem-pendencias');pendencias.replaceChildren();
    if(dados.pendentes_revisao.length)pendencias.append(el('p',dados.pendentes_revisao.length+' pedido(s) precisam de revisão antes de registrar um plano. Use “Revisar” na lista de trechos.','inset warning'));
    $('passagem-salvar').disabled=!dados.reparos.length||Boolean(dados.pendentes_revisao.length);
    const planos=$('passagem-planos');planos.replaceChildren();
    if(!dados.planos.length)planos.append(el('p','Nenhum plano registrado. A comparação acima não salva uma decisão.','empty'));
    dados.planos.forEach(p=>{
      const card=el('article',null,'passage-plan');
      card.append(badge(p.desatualizado?'Desatualizado · exige nova decisão':'Base atual dos pedidos',p.desatualizado?'orange':''),
        el('h3',p.reparos.map(id=>p.resultado.trechos.find(t=>t.id===id).nome).join(' + ')),el('p',p.justificativa),
        el('p',p.revisor+' · '+data(p.data),'fine'),el('p','Resultado registrado: '+resultados[p.resultado.simulado.estado]+'. Hipótese de planejamento, sem confirmação de reparo.','fine'));
      if(p.desatualizado)card.append(el('p','As entradas ou revisões mudaram desde a decisão. O cenário anterior permanece preservado.','inset warning'));
      const detalhes=el('details');detalhes.append(el('summary','Pedidos e condições usados nesta versão'));
      p.resultado.trechos.forEach(t=>{
        detalhes.append(el('p',t.nome+' · '+estados[t.atual]+' → '+estados[t.simulado],'fine'));
        t.pedidos.forEach(c=>detalhes.append(botao(c.id.slice(0,8)+' · '+c.descricao,()=>abrir(c.id),'quiet')));
      });card.append(detalhes);planos.append(card);
    });
    if(foco)lista.querySelector('[data-reparo="'+foco+'"]')?.focus({preventScroll:true});
  }
  $('passagem-atualizar').addEventListener('click',e=>durante(e.currentTarget,atualizar));
  $('passagem-demo').addEventListener('click',e=>durante(e.currentTarget,async()=>{
    const chave=$('passagem-chave').value;if(!chave)throw new Error('Preencha a chave local de revisão no campo acima.');
    await enviar('/api/passagem/demonstracao',{},chave);await atualizar();aviso('Dois pedidos fictícios preparados. Revise cada pedido antes de registrar o plano.');
  }));
  $('passagem-plano').addEventListener('submit',async e=>{
    e.preventDefault();const form=e.currentTarget;$('passagem-salvar').disabled=true;
    try {
      if(!dados)throw new Error('Atualize o percurso e confira o cenário antes de decidir.');
      const entrada={base:dados.base,reparos:dados.reparos,revisor:$('passagem-revisor').value,justificativa:$('passagem-justificativa').value};
      form.inert=true;
      try {await enviar('/api/passagem/planos',entrada,$('passagem-chave').value);await atualizar();aviso('Plano registrado com as condições e revisões desta versão.');}
      finally {form.inert=false;}
    } catch(erro){aviso(erro.message,true);}
    finally {$('passagem-salvar').disabled=!dados?.reparos.length||Boolean(dados?.pendentes_revisao.length);}
  });
  return {atualizar};
}
