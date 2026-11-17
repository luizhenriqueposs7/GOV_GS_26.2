export function iniciarPlanejamento({api,enviar,el,botao,aviso,durante,revisar,atualizarCentral}) {
  const $=id=>document.getElementById(id);
  let dados, simulacao, entrada, versao=0;
  function invalidar() {versao++;simulacao=null;entrada=null;$('planejamento-resultado').replaceChildren();$('planejamento-aprovacao').hidden=true;}
  async function atualizar() {
    dados=await api('/api/planejamento');invalidar();
    $('planejamento-contagem').textContent=dados.pendentes.length+' pedido(s) aguardam revisão. Selecione de 1 a 8 para este ensaio; os demais continuam na fila.';
    const lista=$('planejamento-candidatos');lista.replaceChildren();
    if(!dados.pendentes.length)lista.append(el('p','Não há pedidos pendentes. Importe um lote ou registre um pedido para planejar.','empty'));
    for(const c of dados.pendentes) {
      const row=el('fieldset',null,'planning-case');row.dataset.id=c.id;
      const legend=el('legend'),selecionar=el('input');selecionar.type='checkbox';selecionar.dataset.selecionar='';
      selecionar.setAttribute('aria-label','Incluir pedido '+c.id.slice(0,8));
      const titulo=el('label');titulo.append(selecionar,el('span','Pedido '+c.id.slice(0,8).toUpperCase()));legend.append(titulo);row.append(legend);
      row.append(el('p',c.descricao.slice(0,200)),el('p',c.bairro+' · RPA: '+c.triagem_original.priority+' (heurística). '+(c.exige_revisao?'A central exige revisão.':''),'fine'));
      const campos=el('div',null,'planning-inputs');
      const prioridade=el('select');prioridade.dataset.prioridade='';prioridade.disabled=true;prioridade.required=true;
      for(const p of ['', 'Baixa','Média','Alta']) {const o=el('option',p||'Conferir prioridade');o.value=p;prioridade.append(o);}
      const lp=el('label','Prioridade para planejar');prioridade.id='peso-'+c.id;lp.htmlFor=prioridade.id;
      const minutos=el('input');minutos.type='number';minutos.min=1;minutos.max=240;minutos.value=10;minutos.required=true;minutos.disabled=true;minutos.dataset.minutos='';minutos.id='minutos-'+c.id;
      const lm=el('label','Minutos estimados');lm.htmlFor=minutos.id;
      const obrigatorio=el('input');obrigatorio.type='checkbox';obrigatorio.disabled=true;obrigatorio.dataset.obrigatorio='';
      const lo=el('label',null,'check');lo.append(obrigatorio,el('span','Revisão obrigatória nesta rodada'));
      const cp=el('div'),cm=el('div');cp.append(lp,prioridade);cm.append(lm,minutos);campos.append(cp,cm,lo);row.append(campos);
      selecionar.addEventListener('change',()=>{
        if(selecionar.checked&&lista.querySelectorAll('[data-selecionar]:checked').length>8){selecionar.checked=false;aviso('Selecione no máximo oito pedidos para o simulador.',true);}
        for(const n of [prioridade,minutos,obrigatorio])n.disabled=!selecionar.checked;
        invalidar();
      });lista.append(row);
    }
    const historico=$('planejamento-planos');historico.replaceChildren();
    for(const p of dados.planos) {
      const d=el('details');d.append(el('summary','Plano '+p.id.slice(0,8)+' · '+p.revisor+' · '+new Date(p.data).toLocaleString('pt-BR')),
        el('p',p.justificativa),el('p','Método escolhido: '+p.metodo+'. Registro histórico; atualize e recalcule para uma nova decisão.','fine'));
      historico.append(d);
    }
  }
  function listaResultado() {
    const box=$('planejamento-selecao');box.replaceChildren();if(!simulacao)return;
    const metodo=simulacao.metodos[$('planejamento-metodo').value];
    box.append(el('h3','Revisões escolhidas nesta proposta'));
    const escolhidos=metodo.selecionados.map(id=>simulacao.itens.find(i=>i.id===id)).sort((a,b)=>b.beneficio-a.beneficio||String(a.criado_em).localeCompare(String(b.criado_em))||a.id.localeCompare(b.id));
    for(const item of escolhidos) {
      box.append(botao(item.id.slice(0,8)+' · '+item.descricao.slice(0,95),()=>revisar(item.id),'quiet'));
    }
    if(!metodo.selecionados.length)box.append(el('p','Nenhum pedido selecionado por este método. Confira outra referência ou ajuste o ensaio.'));
    box.append(el('p',metodo.adiados.length+' pedido(s) deste recorte permanecem na fila: '+metodo.adiados.map(id=>id.slice(0,8)).join(', '),'fine'),
      el('p',simulacao.fora_do_recorte_ids.length+' pedido(s) fora do recorte continuam pendentes. Não houve descarte nem decisão automática.','fine'));
  }
  function renderizar() {
    const box=$('planejamento-resultado');box.replaceChildren(el('h2','Três formas de organizar a rodada'));
    const nomes={fila:'Prioridade e antiguidade',classico:'Referência clássica exata',qaoa:'QAOA em simulador'};
    const cards=el('div',null,'planning-comparison');
    for(const [chave,nome] of Object.entries(nomes)) {
      const r=simulacao.metodos[chave],card=el('article');
      card.append(el('h3',nome),el('p',r.selecionados.length+' pedido(s) · '+r.minutos+' min estimados'),el('p','Benefício experimental: '+r.beneficio,'fine'));
      if(chave==='qaoa')card.append(el('p','Estado factível mais provável; sem garantia de ótimo.','fine'));
      cards.append(card);
    }
    box.append(cards,el('p',simulacao.execucao,'inset warning'));
    const detalhes=el('details');detalhes.append(el('summary','Como o ensaio quântico foi calculado'),
      el('p','Estado uniforme, fase de custo e rotações Rx. Profundidade p=1; cálculo do vetor de estado em CPU. Os parâmetros são ajustados por busca clássica.'),
      el('p',simulacao.metodos.qaoa.estados+' estados; energia esperada e probabilidades calculadas pelo simulador. Não são medições de uma QPU.','fine'));
    const pre=el('pre',JSON.stringify(simulacao.metodos.qaoa,null,2),'output');detalhes.append(pre);box.append(detalhes);
    $('planejamento-aprovacao').hidden=false;$('planejamento-confirmado').checked=false;$('planejamento-salvar').disabled=false;
    listaResultado();if(location.hash==='#planejamento')box.scrollIntoView({block:'start'});
  }
  $('planejamento-candidatos').addEventListener('input',invalidar);
  $('planejamento-capacidade').addEventListener('input',invalidar);
  $('planejamento-metodo').addEventListener('change',listaResultado);
  $('planejamento-atualizar').addEventListener('click',e=>durante(e.currentTarget,atualizar));
  $('planejamento-form').addEventListener('submit',e=>{e.preventDefault();durante(e.submitter,async()=>{
    const itens=[...$('planejamento-candidatos').querySelectorAll('fieldset')].filter(row=>row.querySelector('[data-selecionar]').checked).map(row=>({
      id:row.dataset.id,minutos:Number(row.querySelector('[data-minutos]').value),prioridade:row.querySelector('[data-prioridade]').value,obrigatorio:row.querySelector('[data-obrigatorio]').checked}));
    if(!itens.length)throw new Error('Selecione pelo menos um pedido.');
    const baseVersao=versao,pedido={itens,capacidade:Number($('planejamento-capacidade').value)};
    const resultado=await enviar('/api/planejamento/simular',pedido,$('planejamento-chave').value);
    if(baseVersao!==versao)return;
    entrada=pedido;simulacao=resultado;renderizar();
  });});
  $('planejamento-aprovacao').addEventListener('submit',e=>{e.preventDefault();durante(e.submitter,async()=>{
    if(!simulacao||!entrada)throw new Error('Atualize e compare os métodos antes de registrar.');
    const plano=await enviar('/api/planejamento/planos',{...entrada,base:simulacao.base,metodo:$('planejamento-metodo').value,
      revisor:$('planejamento-revisor').value,justificativa:$('planejamento-justificativa').value,confirmado:$('planejamento-confirmado').checked},$('planejamento-chave').value);
    await atualizarCentral();aviso('Plano '+plano.id.slice(0,8)+' registrado no histórico dos pedidos considerados. Cada revisão continua exigindo decisão humana.');
    $('planejamento-confirmado').checked=false;
  });});
  return {atualizar};
}
