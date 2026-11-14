import {test} from 'node:test';
import assert from 'node:assert/strict';
import {coordenadas, dadosRascunho, criarRascunho, mesmoRascunho, bloquearDurante} from '../web/mobile.mjs';

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
