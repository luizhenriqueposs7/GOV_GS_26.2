import {test} from 'node:test';
import assert from 'node:assert/strict';
import {coordenadas, dadosRascunho, criarRascunho, mesmoRascunho, bloquearDurante} from '../web/mobile.mjs';
import * as mobile from '../web/mobile.mjs';

test('a assinatura de um pedido sem vínculo é compatível com rascunhos anteriores à atualização',()=>{
  assert.equal(typeof mobile.assinaturaPedido,'function');
  const antes={descricao:'Pedido de teste',bairro:'Exemplo',localizacao:null,confirmado:true};
  assert.equal(mobile.assinaturaPedido({...antes,passagem:null}),JSON.stringify(antes));
  assert.notEqual(mobile.assinaturaPedido({...antes,passagem:{trecho_id:'calcada'}}),JSON.stringify(antes));
});

test('vínculo do percurso é opcional e conservado no rascunho sem guardar confirmação',()=>{
  assert.equal(typeof mobile.vinculoPassagem,'function');
  assert.equal(mobile.vinculoPassagem('', 'bloqueado'),null);
  assert.deepEqual(mobile.vinculoPassagem('calcada','dificultado'),{
    percurso_id:'ponto-ubs-demo',trecho_id:'calcada',condicao:'dificultado'
  });
  assert.throws(()=>mobile.vinculoPassagem('inexistente','bloqueado'),/trecho/i);
  assert.throws(()=>mobile.vinculoPassagem('calcada','livre'),/condição/i);
  const r=dadosRascunho({'passagem-trecho':'rampa','passagem-condicao':'nao_verificado',confirmado:'on'});
  assert.equal(r['passagem-trecho'],'rampa');
  assert.equal(r['passagem-condicao'],'nao_verificado');
  assert.equal(r.confirmado,undefined);
});

test('coordenadas são opcionais, mas pares incompletos e sem confirmação são rejeitados', () => {
  assert.equal(coordenadas('', '', false), null);
  assert.throws(() => coordenadas('-23.55', '', true), /duas coordenadas/);
  assert.throws(() => coordenadas('-23.55', '-46.63', false), /confirme/i);
  assert.throws(() => coordenadas('NaN', '-46.63', true), /válidas/);
  assert.throws(() => coordenadas('91', '0', true), /válidas/);
  assert.deepEqual(coordenadas('-23,55', '-46,63', true), {
    latitude: -23.55, longitude: -46.63, origem: 'manual', precisao_m: null, confirmado: true
  });
});

test('o rascunho guarda somente campos permitidos, sem confirmar envio ou guardar chave', () => {
  const r = dadosRascunho({descricao:'Caso fictício', bairro:'Teste', local:'Exemplo', contexto:'asfalto_comum',
    latitude:'-23.55', longitude:'-46.63', confirmado:'on', chave:'segredo', revisor:'Pessoa'});
  assert.equal(r.descricao, 'Caso fictício');
  assert.equal(r.latitude, '-23.55');
  assert.equal(r.chave, undefined);
  assert.equal(r.revisor, undefined);
  assert.equal(r.confirmado, undefined);
});

test('o rascunho conserva a posição GPS e o envio para repetir a mesma tentativa após recuperar', () => {
  const foto = new Blob(['foto fictícia'], {type:'image/jpeg'});
  const estado = {foto, origemGeo:'gps', precisaoGeo:15, envioId:'tentativa-1', assinatura:'entrada-1', chave:'nao salvar'};
  const r = criarRascunho({descricao:'Ocorrência fictícia',latitude:'-23.55',longitude:'-46.63'}, estado);
  assert.equal(r.origemGeo,'gps');
  assert.equal(r.precisaoGeo,15);
  assert.equal(r.envioId,'tentativa-1');
  assert.equal(r.assinatura,'entrada-1');
  assert.equal(r.foto,foto);
  assert.equal(r.chave,undefined);
});

test('um rascunho novo ou de outra aba não pertence ao envio que acabou de terminar',()=>{
  assert.equal(mesmoRascunho({id:'outro'},'enviado'),false);
  assert.equal(mesmoRascunho({id:'salvo'},null),false);
  assert.equal(mesmoRascunho({id:'enviado'},'enviado'),true);
});

test('seleção, remoção e envio ficam bloqueados até a preparação assíncrona terminar',async()=>{
  const controles=[{disabled:false},{disabled:true},{disabled:false}];
  let liberar;
  const espera=new Promise(resolve=>{liberar=resolve;});
  const tarefa=bloquearDurante(controles,async()=>{await espera; return 'foto pronta';});
  assert.deepEqual(controles.map(n=>n.disabled),[true,true,true]);
  liberar();
  assert.equal(await tarefa,'foto pronta');
  assert.deepEqual(controles.map(n=>n.disabled),[false,true,false]);
  await assert.rejects(()=>bloquearDurante(controles,async()=>{throw new Error('foto ilegível');}),/ilegível/);
  assert.deepEqual(controles.map(n=>n.disabled),[false,true,false]);
});

test('cancelar câmera libera a espera e fecha um stream que chega depois',async()=>{
  assert.equal(typeof mobile.abrirCamera,'function');
  let liberar,paradas=0;
  const pendente=new Promise(resolve=>{liberar=resolve;});
  const controle=new AbortController();
  const tarefa=mobile.abrirCamera({getUserMedia:()=>pendente},controle.signal);
  controle.abort();
  assert.equal(await tarefa,null);
  liberar({getTracks:()=>[{stop:()=>{paradas++;}}]});
  await pendente; await Promise.resolve();
  assert.equal(paradas,1);
});

test('câmera negada informa erro sem retornar uma captura falsa',async()=>{
  assert.equal(typeof mobile.abrirCamera,'function');
  await assert.rejects(()=>mobile.abrirCamera({getUserMedia:async()=>{throw new Error('negada');}},new AbortController().signal),/negada/);
});

test('GPS cancelado ignora resultado tardio e sucesso conserva precisão e opções',async()=>{
  assert.equal(typeof mobile.obterPosicao,'function');
  let responder,opcoes;
  const geo={getCurrentPosition:(ok,erro,opts)=>{responder=ok;opcoes=opts;}};
  const controle=new AbortController(),tarefa=mobile.obterPosicao(geo,controle.signal);
  controle.abort();assert.equal(await tarefa,null);
  responder({coords:{latitude:1,longitude:2,accuracy:3}});
  const nova=mobile.obterPosicao(geo,new AbortController().signal);
  const pos={coords:{latitude:-23.55,longitude:-46.63,accuracy:15}};
  responder(pos);assert.equal(await nova,pos);
  assert.deepEqual(opcoes,{enableHighAccuracy:true,timeout:20000,maximumAge:0});
});

test('falhas de localização distinguem permissão, sinal e tempo de espera',()=>{
  assert.equal(typeof mobile.erroLocalizacao,'function');
  assert.match(mobile.erroLocalizacao(1),/permissão/i);
  assert.match(mobile.erroLocalizacao(2),/posição/i);
  assert.match(mobile.erroLocalizacao(3),/demorou/i);
  assert.match(mobile.erroLocalizacao(99),/mapa/i);
});

test('bloqueios sobrepostos mantêm controles ocupados e restauram o estado original',async()=>{
  for(const primeiro of [0,1]) {
    const camera={disabled:false},galeria={disabled:false},jaBloqueado={disabled:true};
    let liberarCamera,liberarFoto;
    const esperaCamera=new Promise(resolve=>{liberarCamera=resolve;});
    const esperaFoto=new Promise(resolve=>{liberarFoto=resolve;});
    const tarefas=[bloquearDurante([camera],()=>esperaCamera),bloquearDurante([camera,galeria,jaBloqueado],()=>esperaFoto)];
    const liberar=[liberarCamera,liberarFoto];
    liberar[primeiro]();await tarefas[primeiro];
    assert.equal(camera.disabled,true,'a câmera ainda pertence à outra operação');
    liberar[1-primeiro]();await tarefas[1-primeiro];
    assert.deepEqual([camera.disabled,galeria.disabled,jaBloqueado.disabled],[false,false,true]);
  }
});
