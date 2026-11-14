const {chromium} = require(process.env.CV_PLAYWRIGHT);
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {performance} = require("node:perf_hooks");

const raiz = path.resolve(__dirname, "../..");
const previa = process.argv.includes("--testar");
const W = 1440, H = 900, duracao = 457.0935;
const codigos = Object.fromEntries(["README.md","dados.py","visao.py","train.py","inspecao.py","static/inspecao.js","experimentos.py","artifacts/metricas.json"].map(n=>[n,fs.readFileSync(path.join(raiz,n),"utf8").split(/\r?\n/)]));
function linha(arquivo, trecho) {
  const indice = codigos[arquivo].findIndex(l=>l.includes(trecho));
  assert(indice>=0, arquivo+": "+trecho);
  return indice+1;
}

(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CV_CHROME});
 const context=await browser.newContext({viewport:{width:W,height:H},locale:"pt-BR",
   ...(previa?{}:{recordVideo:{dir:__dirname,size:{width:W,height:H}}})});
 const page=await context.newPage();
 page.setDefaultTimeout(60000);
 await page.addInitScript(()=>{
   window.contagemDuranteExecucao=[];
   new MutationObserver(()=>{
     const t=document.querySelector("#progresso")?.textContent||"";
     if(t.startsWith("Total processado ")&&window.contagemDuranteExecucao.at(-1)!==t)
       window.contagemDuranteExecucao.push(t);
   }).observe(document,{subtree:true,childList:true,characterData:true});
 });
 const inicio=performance.now(), registros=[], comandos=[], erros=[];
 page.on("pageerror",e=>erros.push(String(e)));
 async function ate(s){if(!previa){const ms=s*1000-(performance.now()-inicio);if(ms>0)await page.waitForTimeout(ms)}}
 async function evento(s,nome,acao){
   await ate(s);await acao();
   const real=(performance.now()-inicio)/1000;registros.push({nome,previsto:s,real});
   console.log(nome,real.toFixed(2));
 }
 async function fonte(arquivo,trecho,linhas=10){
   const n=trecho?linha(arquivo,trecho):1;
   await page.evaluate(async({arquivo,n,linhas})=>await abrir(arquivo,n,n+linhas),{arquivo,n,linhas});
   await page.waitForTimeout(previa?180:250);
 }
 async function verificarComando(acao){
   if(previa)return;
   await page.waitForFunction(acao=>window.execucoes[acao]&&!window.execucoes[acao].rodando,acao);
   const r=await page.evaluate(acao=>window.execucoes[acao],acao);
   assert.equal(r.codigo,0,JSON.stringify(r));
   comandos.push({acao,...r});
 }
 async function comando(acao,grande=true){
   if(previa)return;
   await page.evaluate(({acao,grande})=>{executar(acao);mostrarTerminal(grande)},{acao,grande});
 }
 async function imagem(arquivo,esperado){
   await page.locator('input[name="imagens"]').setInputFiles(path.join(raiz,"data/recortes",arquivo));
   await page.getByRole("button",{name:"Analisar",exact:true}).click();
   await page.waitForFunction(()=>document.querySelectorAll("tbody tr").length===1&&document.querySelector("#acompanhamento").hidden);
   assert.match(await page.locator("tbody").textContent(),new RegExp(esperado));
   assert.equal(await page.getByText("FPS observado",{exact:true}).count(),0);
 }
 try{
  await evento(0,"citizentech",()=>page.goto("http://127.0.0.1:8765/",{waitUntil:"load"}));
  await evento(8.0,"modulo_visual",()=>page.getByRole("link",{name:"Inspeção visual"}).click());
  await evento(18.0,"primeira_previsao",async()=>{if(!previa)await imagem("117_227_1362.jpg","Possível fissura")});
  await evento(29.4,"resultado_visual",async()=>{if(!previa)await page.locator("#resultado").evaluate(el=>el.scrollIntoView({block:"start"}))});
  await evento(35.4,"fonte_dados",async()=>{
    await page.goto("http://127.0.0.1:8767/",{waitUntil:"load"});await page.evaluate(()=>window.pronto);
    await fonte("README.md","O [Concrete Crack Segmentation",3);
  });
  await evento(43.8,"pares_rgb_mascara",()=>fonte("dados.py",'fotos = {p.stem',6));
  await evento(51.1,"amostra",()=>page.evaluate(()=>galeria("amostra")));
  await evento(60,"iniciar_auditoria",async()=>{await comando("dados");await page.evaluate(()=>galeria("amostra"))});
  await evento(67.6,"orientacao",()=>fonte("dados.py","foto = ImageOps.exif_transpose(rgb)",5));
  await evento(72,"divisao_por_foto",()=>fonte("dados.py","n_avaliacao =",10));
  await evento(78,"auditoria_dados",async()=>{await verificarComando("dados");if(!previa)await page.evaluate(()=>mostrarTerminal())});
  await evento(85.9,"manifesto",()=>page.evaluate(()=>tabela("data/manifesto.csv")));
  await evento(92,"hash_rgb",()=>fonte("dados.py","def ler_manifesto",17));
  await evento(99,"resnet18",()=>fonte("visao.py","def criar_modelo",5));
  await evento(105.8,"pesos_imagenet",()=>fonte("train.py","if args.pesos_imagenet:",16));
  await evento(113,"ajuste_parcial",()=>fonte("train.py","model.requires_grad_(False)",12));
  await evento(120.6,"treinamento",()=>fonte("train.py","for epoca in range",15));
  await evento(135.7,"preprocessamento",()=>fonte("visao.py","def preprocessamento",12));
  await evento(136.5,"avaliacao_iniciada",()=>comando("teste",false));
  await evento(144.4,"normalizacao",()=>fonte("visao.py","def preprocessamento",12));
  await evento(151.5,"limiar_validacao",()=>fonte("train.py","def choose_threshold",23));
  await evento(163.1,"configuracao_selecionada",()=>fonte("artifacts/metricas.json",'"limiar":',8));
  await evento(170.8,"teste_em_execucao",async()=>{if(!previa)await page.evaluate(()=>mostrarTerminal())});
  await evento(176.6,"metricas_recalculadas",async()=>{await verificarComando("teste");if(!previa)await page.screenshot({path:path.join(__dirname,"metricas_recalculadas.png")})});
  await evento(187.9,"matriz_confusao",async()=>{if(!previa)await page.evaluate(()=>{document.querySelector("#saida").scrollTop=100000})});
  await evento(194,"treze_erros",()=>page.evaluate(()=>tabela("artifacts/analise_erros.csv")));
  await evento(202.9,"falsos_negativos",()=>page.evaluate(()=>galeria("FN")));
  await evento(209.7,"falsos_positivos",()=>page.evaluate(()=>galeria("FP")));
  await evento(216.1,"contexto_mascara",()=>page.evaluate(()=>mascara()));
  await evento(225.4,"resolucao_160",()=>fonte("artifacts/metricas.json",'"entrada":',6));
  await evento(233,"comparacao_resolucoes",()=>page.evaluate(()=>resultados("resolucoes")));
  await evento(253.8,"medicao_video",()=>fonte("experimentos.py","def medir_video",11));
  await evento(260,"equipamento",()=>comando("ambiente"));
  await evento(274,"fps_medidos",async()=>{await verificarComando("ambiente");await page.evaluate(()=>resultados("desempenho"))});
  await evento(292.9,"pipeline_inferencia",()=>fonte("inspecao.py","def acompanhar",20));
  await evento(303.5,"execucao_citizentech",()=>page.goto("http://127.0.0.1:8765/",{waitUntil:"load"}));
  await evento(306,"abrir_inspecao",()=>page.getByRole("link",{name:"Inspeção visual"}).click());
  await evento(311.3,"imagem_com_fissura",async()=>{if(!previa)await imagem("117_227_1362.jpg","Possível fissura")});
  await evento(326.2,"imagem_sem_fissura",async()=>{
    if(!previa){await page.evaluate(()=>window.scrollTo(0,0));await imagem("223_2951_454.jpg","Sem fissura sinalizada")}
  });
  await evento(335,"selecionar_video",async()=>{
    if(!previa){await page.evaluate(()=>window.scrollTo(0,0));await page.locator('input[name="video"]').setInputFiles(path.join(raiz,"demo/monitoramento_ao_vivo.mp4"))}
  });
  await evento(345.5,"inferir_video",async()=>{
    if(previa)return;
    await page.getByRole("button",{name:"Analisar",exact:true}).click();
    await page.waitForFunction(()=>parseInt((document.querySelector("#progresso")?.textContent||"").replace("Total processado ",""),10)>=20);
    await page.locator("#acompanhamento").evaluate(el=>el.scrollIntoView({block:"start"}));
    assert.equal(await page.locator("#resultado").isVisible(),false);
    await page.screenshot({path:path.join(__dirname,"execucao_em_andamento.png")});
  });
  await evento(361.5,"resultado_video",async()=>{
    if(previa)return;
    await page.waitForFunction(()=>document.querySelectorAll("tbody tr").length===180&&document.querySelector("#acompanhamento").hidden);
    const atualizacoes=await page.evaluate(()=>window.contagemDuranteExecucao);
    assert(atualizacoes.length>=100);
    registros.push({nome:"atualizacoes_ao_vivo",quantidade:atualizacoes.length});
    await page.locator("#resultado").evaluate(el=>el.scrollIntoView({block:"start"}));
    assert.equal(await page.getByText("FPS observado",{exact:true}).count(),1);
    await page.screenshot({path:path.join(__dirname,"execucao_concluida.png")});
  });
  await evento(369,"classificacao_por_quadro",async()=>{if(!previa)await page.getByRole("heading",{name:"Classificação por quadro"}).evaluate(el=>el.scrollIntoView({block:"start"}))});
  await evento(375,"conjunto_sutil",async()=>{
    await page.goto("http://127.0.0.1:8767/",{waitUntil:"load"});await page.evaluate(()=>window.pronto);
    await comando("sutis");await page.evaluate(()=>galeria("sutis"));
  });
  await evento(390.3,"resultado_sutis",()=>page.evaluate(()=>resultados("sutis")));
  await evento(398,"sutis_confirmados",async()=>{await verificarComando("sutis");if(!previa)await page.evaluate(()=>mostrarTerminal())});
  await evento(403.6,"decisao_modelo",()=>fonte("visao.py","def classificar",14));
  await evento(412.6,"rota_integracao",()=>fonte("inspecao.py",'@inspecao.route',18));
  await evento(427.1,"limites",()=>fonte("README.md","## Limitações",8));
  await evento(439.5,"triagem_humana",()=>fonte("README.md","O módulo classifica",1));
  await evento(448.6,"encerramento",()=>page.goto("http://127.0.0.1:8765/inspecao-visual",{waitUntil:"load"}));
  if(previa){
    await page.goto("http://127.0.0.1:8767/");await page.evaluate(()=>window.pronto);
    await fonte("visao.py","def preprocessamento",12);await page.screenshot({path:path.join(__dirname,"previa_codigo.png")});
    await page.evaluate(()=>resultados("resolucoes"));await page.screenshot({path:path.join(__dirname,"previa_resultados.png")});
    await page.evaluate(()=>galeria("FN"));await page.screenshot({path:path.join(__dirname,"previa_erros.png")});
  }else{
    await ate(duracao);
  }
  assert.deepEqual(erros,[]);
  const video=page.video();await context.close();
  if(!previa)await video.saveAs(path.join(__dirname,"captura_tecnica.webm"));
  fs.writeFileSync(path.join(__dirname,previa?"verificacao_previa.json":"gravacao.json"),JSON.stringify({canvas:[W,H],fps:25,duracao_audio:duracao,eventos:registros,comandos,erros},null,2));
  console.log(previa?"Prévia conferida.":"Gravação técnica concluída.");
 }catch(e){await page.screenshot({path:path.join(__dirname,"falha.png")}).catch(()=>{});throw e}
 finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
