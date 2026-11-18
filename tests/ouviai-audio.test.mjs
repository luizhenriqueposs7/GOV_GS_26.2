import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as audio from '../web/ouviai.mjs';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import {criarEscuta} from '../web/ouviai-audio.mjs';

test('a tela informa preparação enquanto aguarda áudio e volta a desligado quando a escuta é cancelada',()=>{
  const chaves=['isSecureContext','navigator','AudioWorkletNode','AudioContext','document','window'];
  const originais=new Map(chaves.map(k=>[k,Object.getOwnPropertyDescriptor(globalThis,k)]));
  const nos=new Map();
  const node=id=>{
    if(!nos.has(id))nos.set(id,{textContent:'',dataset:{},eventos:{},replaceChildren(){},setAttribute(){},scrollIntoView(){},
      addEventListener(tipo,fn){this.eventos[tipo]=fn;}});
    return nos.get(id);
  };
  let escuta;
  try {
    const definir=(k,v)=>Object.defineProperty(globalThis,k,{configurable:true,writable:true,value:v});
    definir('isSecureContext',true);definir('navigator',{mediaDevices:{getUserMedia:async()=>{throw new Error('Não deve chegar ao microfone nesta etapa.');}}});
    definir('AudioWorkletNode',class {});
    definir('AudioContext',class {resume(){return new Promise(()=>{});}async close(){}});
    definir('document',{getElementById:node,querySelectorAll:()=>[],addEventListener(){}});
    definir('window',{addEventListener(){}});
    escuta=audio.iniciarOuviAi();node('ouviai-iniciar').eventos.click();
    assert.match(node('ouviai-display').textContent,/preparando/i);
    assert.match(node('ouviai-status').textContent,/preparando/i);
    node('ouviai-conexao').eventos.click();
    assert.match(node('ouviai-display').textContent,/preparando/i);
    assert.match(node('ouviai-status').textContent,/preparando/i);
    escuta.parar();
    assert.match(node('ouviai-display').textContent,/desligado/i);
  } finally {
    escuta?.parar();
    for(const [k,descritor] of originais){if(descritor)Object.defineProperty(globalThis,k,descritor);else delete globalThis[k];}
  }
});

test('campainha ou batida dominante com score suficiente vira possível aviso real',()=>{
  for (const [categoryName,classe] of [['Doorbell','som_campainha'],['Ding-dong','som_campainha'],['Knock','batida_porta']]) {
    const r=audio.interpretarAudio([{categoryName,score:0.8},{categoryName:'Speech',score:0.1}]);
    assert.equal(r.classe,classe); assert.equal(r.pontuacao,0.8); assert.equal(r.alerta,true);
  }
});

test('captura conserva a janela de dois segundos e sobreposição sem reproduzir o microfone',async()=>{
  const mensagens=[], registro={};
  const contexto={sampleRate:16000,Float32Array,AudioWorkletProcessor:class {port={postMessage:a=>mensagens.push(a)};},
    registerProcessor:(nome,classe)=>{registro.Classe=classe;}};
  vm.runInNewContext(await readFile(new URL('../web/ouviai-captura.js',import.meta.url),'utf8'),contexto);
  const captura=new registro.Classe();
  for(let i=0;i<375;i++) {const bloco=new Float32Array(128).fill(i);captura.process([[bloco]]);}
  assert.equal(mensagens.length,2);
  assert.equal(mensagens[0].length,32000);
  assert.equal(mensagens[1][0],125);
  assert.equal(mensagens[1][31999],374);
  assert.equal(mensagens[0][0],0);
});

test('som parecido, score baixo ou disputa entre dois avisos não confirma campainha',()=>{
  for (const categorias of [
    [{categoryName:'Doorbell',score:0.4}],
    [{categoryName:'Doorbell',score:0.65},{categoryName:'Knock',score:0.62}],
    [{categoryName:'Doorbell',score:0.61},{categoryName:'Knock',score:0.59}],
    [{categoryName:'Bell',score:0.99}],
  ]) assert.equal(audio.interpretarAudio(categorias).alerta,false);
});

test('rótulos simultâneos do YAMNet não anulam um aviso, inclusive Door e Knock',()=>{
  for (const categorias of [
    [{categoryName:'Door',score:0.85},{categoryName:'Knock',score:0.74}],
    [{categoryName:'Knock',score:0.969},{categoryName:'Door',score:0.852}],
    [{categoryName:'Speech',score:0.9},{categoryName:'Doorbell',score:0.65}],
    [{categoryName:'Doorbell',score:0.98},{categoryName:'Ding-dong',score:0.85}],
  ]) assert.equal(audio.interpretarAudio(categorias).alerta,true);
});

test('silêncio é ambiente; entrada inválida não produz certeza nem alerta',()=>{
  assert.equal(audio.interpretarAudio([{categoryName:'Silence',score:0.98}]).classe,'som_ambiente');
  for(const categorias of [[],[{categoryName:'Knock',score:NaN}],[{categoryName:'Doorbell',score:1.5}],null]) {
    const r=audio.interpretarAudio(categorias); assert.equal(r.classe,'inconclusivo'); assert.equal(r.alerta,false);
  }
});

test('negar a permissão encerra o contexto e uma autorização tardia não deixa o microfone ativo',async()=>{
  const originais=new Map(['isSecureContext','navigator','AudioWorkletNode','AudioContext'].map(k=>[k,Object.getOwnPropertyDescriptor(globalThis,k)]));
  const contextos=[], estados=[];
  let resolver, encerrar=0;
  try {
    const definir=(k,v)=>Object.defineProperty(globalThis,k,{configurable:true,writable:true,value:v});
    definir('isSecureContext',true);definir('AudioWorkletNode',class {});
    definir('AudioContext',class {constructor(){this.state='running';contextos.push(this);}async resume(){} async close(){this.state='closed';}});
    definir('navigator',{mediaDevices:{getUserMedia:async()=>{throw new DOMException('Negado','NotAllowedError');}}});
    const escuta=criarEscuta(()=>assert.fail('Não deve classificar sem microfone'),(ativo,mensagem)=>estados.push({ativo,mensagem}));
    await escuta.iniciar();
    assert.equal(contextos[0].state,'closed');assert.equal(estados.at(-1).ativo,false);
    assert.match(estados.at(-1).mensagem,/não autorizado/);
    navigator.mediaDevices.getUserMedia=()=>new Promise(r=>{resolver=r;});
    const pendente=escuta.iniciar();await new Promise(r=>setImmediate(r));
    escuta.parar();resolver({getTracks:()=>[{stop:()=>encerrar++}]});await pendente;
    assert.equal(encerrar,1);assert.equal(contextos[1].state,'closed');assert.equal(estados.at(-1).ativo,false);
  } finally {
    for(const [k,descritor] of originais) {if(descritor)Object.defineProperty(globalThis,k,descritor);else delete globalThis[k];}
  }
});

test('falha do processador de áudio encerra microfone, worker e contexto antes da primeira janela',async()=>{
  const originais=new Map(['isSecureContext','navigator','AudioWorkletNode','AudioContext','Worker'].map(k=>[k,Object.getOwnPropertyDescriptor(globalThis,k)]));
  let captura, trackParada=false, contextoFechado=false, workerEncerrado=false, estadoAtivo=true;
  try {
    const definir=(k,v)=>Object.defineProperty(globalThis,k,{configurable:true,writable:true,value:v});
    const node=()=>({gain:{value:1},connect(){return this;},disconnect(){}});
    definir('isSecureContext',true);
    definir('navigator',{mediaDevices:{getUserMedia:async()=>({getTracks:()=>[{stop:()=>trackParada=true}],getAudioTracks:()=>[]})}});
    definir('AudioContext',class {
      audioWorklet={addModule:async()=>{}};destination={};
      async resume(){} async close(){contextoFechado=true;}
      createMediaStreamSource(){return node();} createGain(){return node();}
    });
    definir('AudioWorkletNode',class {constructor(){Object.assign(this,node(),{port:{}});captura=this;}});
    definir('Worker',class {postMessage(){queueMicrotask(()=>this.onmessage({data:{tipo:'pronto'}}));}terminate(){workerEncerrado=true;}});
    const escuta=criarEscuta(()=>assert.fail('Sem áudio não pode haver resultado'),ativo=>estadoAtivo=ativo);
    await escuta.iniciar();assert.equal(estadoAtivo,true);
    captura.onprocessorerror?.();
    assert.equal(trackParada,true);assert.equal(contextoFechado,true);assert.equal(workerEncerrado,true);assert.equal(estadoAtivo,false);
  } finally {
    for(const [k,descritor] of originais) {if(descritor)Object.defineProperty(globalThis,k,descritor);else delete globalThis[k];}
  }
});
