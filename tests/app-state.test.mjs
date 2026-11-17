import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const codigo=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');

function funcao(nome) {
  const trecho=codigo.match(new RegExp('(?:async )?function '+nome+'\\([^]*?\\n\\}'))?.[0];
  assert.ok(trecho,'A função '+nome+' deve continuar disponível para o teste de estado.');
  return trecho;
}

function contexto() {
  const pedidos=new Map(),nos=new Map();
  let rolagens=0;
  function el(tag,texto) {
    return {tag,textContent:texto,children:[],hidden:false,dataset:{},
      get firstElementChild(){return this.children[0]||null;},
      append(...filhos){this.children.push(...filhos);},
      replaceChildren(...filhos){this.children=filhos;},
      addEventListener(){},focus(){},
      scrollIntoView(){rolagens++;}};
  }
  const $=id=>{if(!nos.has(id))nos.set(id,el('div'));return nos.get(id);};
  const paineis=['pedido','acompanhar','mapa','evidencias'].map(view=>{
    const painel=el('section');painel.dataset.panel=view;painel.hidden=view!=='acompanhar';return painel;
  });
  const location={hash:'#acompanhar'};
  const ambiente={state:{selecionado:null,etapa:0,ativos:true},$,el,
    api:url=>new Promise((resolve,reject)=>pedidos.set(url.split('/').at(-1),{resolve,reject})),
    badge:texto=>el('span',texto),botao:texto=>el('button',texto),link:texto=>el('a',texto),
    evidenciaVisual:()=>el('div'),atendimento:()=>el('div'),historico:()=>el('div'),
    enviar(){},durante(){},aviso(){},reduzirFoto(){},data(){},editar(){},
    fecharCamera(){},cancelarGeo(){},cancelarAutomatico(){},mostrarEtapa(){},
    atualizar:async()=>{},ativos:async()=>{},planejamento:{atualizar:async()=>{}},
    titulos:{pedido:'Novo pedido',acompanhar:'Meus pedidos',mapa:'Mapa',evidencias:'Materiais'},
    location,history:{replaceState(_estado,_titulo,hash){location.hash=hash;}},window:{scrollTo(){}},
    document:{querySelectorAll:seletor=>seletor==='[data-panel]'?paineis:[]}};
  runInNewContext(funcao('detalhe')+'\n'+funcao('navegar'),ambiente);
  return {...ambiente,responder:(id)=>pedidos.get(id).resolve({id,atualizado_em:'2026-11-17',
    descricao:'Pedido '+id,bairro:'Teste',situacao:'Aberto',preparacao:{faltantes:[]},
    triagem_original:{category:'Teste',priority:'Alta'}}),rejeitar:id=>pedidos.get(id).reject(new Error('Falha da requisição anterior')),pedidos,rolagens:()=>rolagens};
}

test('a seleção mais recente vence quando os detalhes chegam fora de ordem',async()=>{
  const app=contexto();
  const anterior=app.detalhe('AAAA'),atual=app.detalhe('BBBB');
  app.responder('BBBB');await atual;
  const exibido=app.$('detalhe-caso').children[0];
  app.responder('AAAA');await anterior;
  assert.equal(app.state.selecionado.id,'BBBB');
  assert.equal(app.$('detalhe-caso').children[0],exibido);
  assert.equal(app.rolagens(),1);
});

test('sair de Meus pedidos invalida um detalhe pendente sem renderizar ou rolar',async()=>{
  const app=contexto();
  const pendente=app.detalhe('AAAA');
  const anterior=app.$('detalhe-caso').children[0];
  await app.navegar('mapa',false);
  app.responder('AAAA');await pendente;
  assert.equal(app.$('detalhe-caso').children[0],anterior);
  assert.equal(app.rolagens(),0);
});

test('atualização do pedido anterior não cancela a seleção nova em carregamento',async()=>{
  const app=contexto();
  const inicial=app.detalhe('AAAA');app.responder('AAAA');await inicial;
  const exibido=app.$('detalhe-caso').firstElementChild;
  const atualizar=app.detalhe('AAAA',false);app.responder('AAAA');await atualizar;
  assert.equal(app.$('detalhe-caso').firstElementChild,exibido);
  const novo=app.detalhe('BBBB'),resolverAnterior=app.pedidos.get('AAAA');
  await app.detalhe('AAAA',false);
  assert.equal(app.pedidos.get('AAAA'),resolverAnterior);
  app.responder('BBBB');await novo;
  assert.equal(app.state.selecionado.id,'BBBB');
});

test('erro de uma requisição abandonada não substitui o pedido atual por erro',async()=>{
  const app=contexto();const anterior=app.detalhe('AAAA'),atual=app.detalhe('BBBB');
  app.responder('BBBB');await atual;
  const exibido=app.$('detalhe-caso').children[0];
  app.rejeitar('AAAA');await assert.doesNotReject(anterior);
  assert.equal(app.$('detalhe-caso').children[0],exibido);
  assert.equal(app.state.selecionado.id,'BBBB');
});

test('voltar após abandonar outra seleção restaura o pedido sem manter o carregamento',async()=>{
  const app=contexto();
  const inicial=app.detalhe('AAAA');app.responder('AAAA');await inicial;
  const pendente=app.detalhe('BBBB');
  await app.navegar('mapa',false);
  await app.navegar('acompanhar',false);
  const retorno=app.detalhe('AAAA',false);app.responder('AAAA');await retorno;
  assert.equal(app.$('detalhe-caso').firstElementChild.tag,'article');
  app.responder('BBBB');await pendente;
  assert.equal(app.state.selecionado.id,'AAAA');
});
