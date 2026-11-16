import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as automatico from '../web/automatico.mjs';
import {criarRascunho} from '../web/mobile.mjs';

const gps={getCurrentPosition(resolve){resolve({coords:{latitude:-23.55,longitude:-46.63,accuracy:18}});}};

test('localiza somente o GPS atual, busca região no aparelho e não inventa rua',async()=>{
  let chamadas=0;
  const resultado=await automatico.localizarAtual(gps,new AbortController().signal,async(url,opcoes)=>{
    chamadas++;
    assert.equal(new URL(url).origin,'https://api.bigdatacloud.net');
    assert.equal(new URL(url).searchParams.get('latitude'),'-23.55');
    assert.equal(opcoes.credentials,'omit');
    return new Response(JSON.stringify({locality:'Sé',city:'São Paulo',principalSubdivision:'São Paulo',countryName:'Brasil'}));
  });
  assert.equal(chamadas,1);
  assert.equal(resultado.bairro,'Sé');
  assert.match(resultado.local,/São Paulo/);
  assert.match(resultado.local,/-23\.55/);
  assert.equal(resultado.posicao.origem,'gps');
  assert.equal(resultado.posicao.confirmado,undefined);
  assert.equal(resultado.posicao.precisao_m,18);
});

test('GPS negado não chama geocodificador nem inventa localização por IP',async()=>{
  const negado={getCurrentPosition(_ok,erro){erro({code:1});}};
  await assert.rejects(automatico.localizarAtual(negado,new AbortController().signal,async()=>{
    assert.fail('consulta sem GPS autorizado');
  }),/permissão/i);
});

test('queda da consulta de região preserva o GPS e pede bairro, sem endereço falso',async()=>{
  const resultado=await automatico.localizarAtual(gps,new AbortController().signal,async()=>{throw new Error('offline');});
  assert.equal(resultado.posicao.latitude,-23.55);
  assert.equal(resultado.bairro,'');
  assert.match(resultado.aviso,/região/i);
  assert.match(resultado.local,/Ponto GPS/);
});

test('cancelamento descarta foto e GPS tardios',async()=>{
  const controller=new AbortController();
  let concluir;
  const foto=new Promise(resolve=>{concluir=resolve;});
  const pendente=automatico.prepararAutomatico(()=>foto,async()=>({bairro:'Sé'}),controller.signal);
  controller.abort();concluir({descricao:'Resposta atrasada'});
  assert.equal(await pendente,null);
});

test('falha de imagem preserva a localização sem inventar relato ou gravar pedido',async()=>{
  const r=await automatico.prepararAutomatico(async()=>{throw new Error('Cota atingida');},
    async()=>({bairro:'Sé'}),new AbortController().signal);
  assert.equal(r.foto,null);
  assert.equal(r.localizacao.bairro,'Sé');
  assert.deepEqual(r.avisos,['Cota atingida']);
});

test('rascunho conserva prévia assinada sem confirmar automaticamente',()=>{
  const previaFoto={previa:'assinatura-sintetica',descricao:'Descrição original',modelo:'modelo'};
  const regiaoAuto={bairro:'Sé',local:'Ponto GPS: -23.55, -46.63'};
  const r=criarRascunho({descricao:'Texto corrigido',confirmado:'on'},{previaFoto,rascunhoId:'teste',regiaoAuto});
  assert.deepEqual(r.previaFoto,previaFoto);
  assert.deepEqual(r.regiaoAuto,regiaoAuto);
  assert.equal(r.campos.confirmado,undefined);
});
