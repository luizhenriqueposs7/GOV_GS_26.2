import {test} from 'node:test';
import assert from 'node:assert/strict';
import {pontoValido, proximos, filtrarCasos, criarMapa} from '../web/mapa.mjs';

const caso=(id,lat,lon,extra={})=>({id,descricao:'Calçada danificada',bairro:'República',local:'Rua Aurora',localizacao:{latitude:lat,longitude:lon,confirmado:true},...extra});
test('somente pontos finitos confirmados entram no mapa',()=>{
  assert.equal(pontoValido(caso('a',-23.55,-46.63)),true);
  for(const c of [caso('a',91,0),caso('a',0,181),caso('a',NaN,0),caso('a','',0),caso('a',null,0),{localizacao:null},caso('a',0,0,{localizacao:{latitude:0,longitude:0,confirmado:false}})])assert.equal(pontoValido(c),false);
  assert.equal(pontoValido(caso('zero',0,0)),true);
});
test('vizinhos excluem o próprio caso e pontos inválidos, com distância ordenada',()=>{
  const a=caso('a',0,0), b=caso('b',0,.0004), c=caso('c',0,.0008), d=caso('d',0,.002);
  const r=proximos(a,[a,c,d,b,{id:'sem'}]);
  assert.deepEqual(r.map(x=>x.caso.id),['b','c']);
  assert.ok(r[0].metros>44 && r[0].metros<45);
  assert.deepEqual(proximos({id:'sem'},[a]),[]);
  assert.deepEqual(proximos(a,[c],80),[]);
});
test('busca ignora acentos e preserva registros sem GPS; filtros usam o estado atual',()=>{
  const a=caso('a',0,0), b=caso('b',0,0,{revisao:{},descricao:'Poste apagado'}), c={id:'c',descricao:'Rampa de acesso',bairro:'Sé',frontend:{id:'z'},revisao:{}};
  assert.deepEqual(filtrarCasos([a,b,c],'republica','todos').map(x=>x.id),['a','b']);
  assert.deepEqual(filtrarCasos([a,b,c],'','revisado').map(x=>x.id),['b']);
  assert.deepEqual(filtrarCasos([a,b,c],'','confirmado').map(x=>x.id),['c']);
  assert.deepEqual(filtrarCasos([a,b,c],'','pendente').map(x=>x.id),['a']);
  assert.deepEqual(filtrarCasos([c],'rampa','todos').map(x=>x.id),['c']);
});

test('biblioteca de mapa indisponível informa a alternativa manual',()=>{
  const anterior=globalThis.document, leaflet=globalThis.L, status={textContent:''};
  try {
    globalThis.document={getElementById:()=>status};delete globalThis.L;
    assert.equal(criarMapa('mapa','status'),null);
    assert.match(status.textContent,/campos de localização ou a lista/);
  } finally {if(anterior===undefined)delete globalThis.document;else globalThis.document=anterior;if(leaflet!==undefined)globalThis.L=leaflet;}
});
