import {test} from 'node:test';
import assert from 'node:assert/strict';
import {estadoInicial, simularSom, conectar} from '../web/ouviai.mjs';

test('campainha e batida geram alertas explicitamente simulados, sem probabilidade inventada',()=>{
  for(const classe of ['som_campainha','batida_porta']) {
    const anterior=estadoInicial(), novo=simularSom(anterior,classe,'2026-11-16T12:00:00Z');
    assert.equal(anterior.eventos.length,0);
    assert.equal(novo.eventos[0].classe,classe);
    assert.equal(novo.eventos[0].simulacao,true);
    assert.equal(novo.eventos[0].alerta,true);
    assert.equal(novo.eventos[0].exibido,true);
    assert.equal(novo.eventos[0].confianca,undefined);
  }
});

test('som ambiente fica no registro sem gerar aviso de campainha ou porta',()=>{
  const novo=simularSom(estadoInicial(),'som_ambiente','2026-11-16T12:00:00Z');
  assert.equal(novo.eventos[0].alerta,false);
  assert.equal(novo.eventos[0].simulacao,true);
  assert.throws(()=>simularSom(novo,'alarme','agora'));
});

test('conexão simulada interrompida conserva evento e reconectar atualiza sua exibição',()=>{
  const offline=conectar(estadoInicial(),false);
  const capturado=simularSom(offline,'batida_porta','2026-11-16T12:00:00Z');
  assert.equal(capturado.eventos[0].exibido,false);
  const reconectado=conectar(capturado,true);
  assert.equal(reconectado.eventos[0].exibido,true);
  assert.equal(capturado.eventos[0].exibido,false);
  assert.equal(reconectado.eventos[0].simulacao,true);
});

test('somente os oito eventos recentes ficam na demonstração desta aba',()=>{
  let estado=estadoInicial();
  for(let i=0;i<10;i++)estado=simularSom(estado,'som_ambiente',String(i));
  assert.equal(estado.eventos.length,8);
  assert.equal(estado.eventos[0].data,'9');
  assert.equal(estado.eventos.at(-1).data,'2');
  assert.equal(estadoInicial().eventos.length,0);
});
