import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

async function ambiente() {
  const eventos = {};
  const versaoAntiga = new Map(['/', '/web/app.js', '/web/mobile.mjs'].map(p=>[p, 'versao-conjunta:'+p]));
  const contexto = {
    self:{location:{origin:'https://central.example'}, addEventListener:(nome,cb)=>{eventos[nome]=cb;}},
    URL, Response,
    caches:{open:async()=>({match:async p=>versaoAntiga.has(p)?new Response(versaoAntiga.get(p)):undefined}),
            match:async p=>versaoAntiga.has(p)?new Response(versaoAntiga.get(p)):undefined},
    fetch:async req=>{if(req.url.endsWith('mobile.mjs'))throw new Error('queda de rede');return new Response('versao-nova-incompativel');}
  };
  vm.runInNewContext(await readFile(new URL('../web/sw.js',import.meta.url),'utf8'),contexto);
  return eventos;
}

test('uma queda parcial de conexão não mistura versões do formulário instalado',async()=>{
  const eventos=await ambiente();
  for(const p of ['/', '/web/app.js', '/web/mobile.mjs']) {
    let resposta;
    eventos.fetch({request:new Request('https://central.example'+p), respondWith:r=>{resposta=r;}});
    assert.equal(await (await resposta).text(),'versao-conjunta:'+p);
  }
});

test('fotos, APIs e escrita passam direto para a rede sem cache',async()=>{
  const eventos=await ambiente();
  for(const [p,method] of [['/api/atendimentos','GET'],['/api/atendimentos/caso/foto','GET'],['/api/atendimentos','POST']]) {
    let interceptado=false;
    eventos.fetch({request:new Request('https://central.example'+p,{method}), respondWith:()=>{interceptado=true;}});
    assert.equal(interceptado,false);
  }
});
