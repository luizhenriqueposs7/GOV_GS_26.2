"use strict";
import {coordenadas, dadosRascunho, criarRascunho, reduzirFoto, rascunho, bloquearDurante, abrirCamera, obterPosicao, erroLocalizacao, vinculoPassagem, assinaturaPedido} from './mobile.mjs';
import {criarMapa, pontoValido, proximos, filtrarCasos} from './mapa.mjs';
import {iniciarPassagem} from './passagem.mjs';
const $ = (id) => document.getElementById(id);
const state = {casos: [], selecionado: null, edicao: null, ativos: false, etapa:0, mapa:null, mapaLocal:null, mapaId:null, camera:null};
Object.assign(state, {foto: null, fotoAtual: null, fotoUrl: null, removerFoto: false, origemGeo: 'manual', precisaoGeo: null, envioId: null, assinatura: null, rascunhoId:null});
const titulos = {mapa:'Mapa do bairro', passagem:'Passagem Livre', pedido: "Novo pedido", acompanhar: "Meus pedidos", revisao: "Revisão", evidencias: "Materiais e fontes"};
const data = (valor) => valor ? new Date(valor).toLocaleString("pt-BR") : "—";
function el(tag, texto, classe) {
  const node = document.createElement(tag);
  if (texto !== undefined && texto !== null) node.textContent = String(texto);
  if (classe) node.className = classe;
  return node;
}
function aviso(mensagem, erro = false) {
  const box = $("aviso");
  box.textContent = mensagem;
  box.className = "notice" + (erro ? " error" : "");
  box.hidden = false;
  box.scrollIntoView({block: "nearest"});
}
function link(texto, url) {
  const a = el("a", texto);
  const destino = new URL(url, location.origin);
  if (!["http:", "https:"].includes(destino.protocol)) return el("span", texto);
  a.href = destino.href;
  if (destino.origin !== location.origin) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
  return a;
}
function botao(texto, acao, classe = "secondary") {
  const b = el("button", texto, classe); b.type = "button"; b.addEventListener("click", acao); return b;
}
function json(dados) { return el("pre", JSON.stringify(dados, null, 2), "output"); }
function badge(texto, classe = "") { return el("span", texto, "badge " + classe); }
async function api(url, options = {}) {
  let resposta;
  try {resposta = await fetch(url, options);}
  catch {throw new Error('A central não está acessível. O formulário foi mantido. Salve um rascunho e tente novamente quando a conexão voltar.');}
  let conteudo;
  try { conteudo = await resposta.json(); } catch { throw new Error("A central não respondeu como esperado. Confira se o serviço está em execução."); }
  if (!resposta.ok) throw new Error((conteudo.erro || conteudo.detail || "Não foi possível concluir a operação.") + (conteudo.campos ? " Campos: " + conteudo.campos.join(", ") + "." : ""));
  return conteudo;
}
function enviar(url, dados, chave, method = "POST") {
  const headers = {"Content-Type": "application/json"};
  if (chave) headers["X-Manager-Key"] = chave;
  return api(url, {method, headers, body: JSON.stringify(dados)});
}
async function durante(botao, acao) {
  const anterior = botao.textContent; botao.disabled = true; botao.textContent = "Aguarde…";
  const form=botao.closest('#pedido-form'), jaInerte=form?.inert;
  if(form)form.inert=true;
  try { await acao(); } catch (erro) { aviso(erro.message || "Não foi possível concluir a operação.", true); }
  finally {if(form)form.inert=jaInerte; botao.disabled = false; botao.textContent = form && botao.type==='submit' ? (state.edicao?'Atualizar pedido':'Registrar pedido') : anterior; }
}
function formulario(id, acao) {
  $(id).addEventListener("submit", event => {
    event.preventDefault(); const form=event.currentTarget, dados=new FormData(form);
    durante(event.submitter, async()=>{if(id==='pedido-form')form.inert=true;
      try {await acao(dados);} finally {form.inert=false;}
    });
  });
}
async function navegar(view, foco = true) {
  if (!titulos[view]) view = "pedido";
  if(view!=='pedido'){fecharCamera();cancelarGeo();}
  if(view==='pedido') {$('pedido-form').hidden=false;$('request-progress').hidden=false;$('preparacao-resultado').hidden=true;mostrarEtapa(state.etapa,false);}
  $("aviso").hidden = true;
  document.querySelectorAll("[data-panel]").forEach(n => n.hidden = n.dataset.panel !== view);
  document.querySelectorAll("[data-view]").forEach(n => {n.classList.toggle("active", n.dataset.view === view); if(n.dataset.view === view) n.setAttribute("aria-current", "page"); else n.removeAttribute("aria-current");});
  $("breadcrumb").textContent = titulos[view];
  if (location.hash !== "#" + view) history.replaceState(null, "", "#" + view);
  if (foco) { $("principal").focus(); window.scrollTo(0, 0); }
  if(view==='acompanhar')$('detalhe-caso').hidden=true;
  try { await atualizar(); if (view === "evidencias" && !state.ativos) await ativos(); }
  catch (erro) { aviso(erro.message, true); }
  finally {if(view==='acompanhar')$('detalhe-caso').hidden=false;}
}
document.querySelectorAll("[data-view]").forEach(n => n.addEventListener("click", () => navegar(n.dataset.view)));
document.querySelector('.skip').addEventListener('click',e=>{e.preventDefault();$('principal').focus();});
window.addEventListener("hashchange", () => navegar(location.hash.slice(1)));
document.querySelector(".brand").addEventListener("click", () => navegar("mapa"));
async function atualizar() {
  const [casos, indicadores] = await Promise.all([api("/api/atendimentos"), api("/api/indicadores")]);
  state.casos = casos;
  lista(); metricas(indicadores);
  if(!document.querySelector('[data-panel="mapa"]').hidden)renderMapa();
  if(!document.querySelector('[data-panel="passagem"]').hidden)await passagem.atualizar();
  for (const id of ["revisao-caso", "evidencia-caso"]) {
    const select = $(id), valor = select.value;
    select.replaceChildren();
    if (id === "evidencia-caso") {const vazio = el("option", "Consultar sem vínculo"); vazio.value = ""; select.append(vazio);}
    casos.forEach(c => {const option = el("option", c.descricao.slice(0, 65) + " · " + c.id.slice(0, 8)); option.value = c.id; select.append(option);});
    if ([...select.options].some(n => n.value === valor)) select.value = valor;
  }
  await resumoRevisao();
  if (state.selecionado && !document.querySelector('[data-panel="acompanhar"]').hidden) {
    await detalhe(state.selecionado.id, false);
  }
}
function metricas(m) {
  const cards = [["Pedidos registrados", m.total, "Somente desta instalação"], ["Decisões revisadas", m.revisados, "Revisões atuais"], ["Revisões obrigatórias pendentes", m.revisoes_pendentes, "Controle de acessibilidade e RPA"], ["Prioridades alteradas", m.sugestoes_corrigidas + " / " + m.denominador_correcoes, "Entre as decisões revisadas"]];
  $("indicadores").replaceChildren(...cards.map(([nome, valor, nota]) => {const card = el("div", null, "metric");card.append(el("span", nome), el("strong", valor), el("small", nota));return card;}));
}
function lista() {
  const box = $("lista-casos"); box.replaceChildren(); box.className = "case-list";
  if (!state.casos.length) {box.append(el("div", "Nenhum pedido registrado. Prepare o primeiro pedido com dados fictícios para acompanhar as etapas.", "empty"));return;}
  state.casos.forEach(c => {
    const row = el("article", null, "case-row"), texto = el("div");
    if(c.foto){const img=el('img',null,'case-thumb');img.src='/api/atendimentos/'+encodeURIComponent(c.id)+'/foto?v='+c.foto.sha256;img.alt='';img.loading='lazy';row.append(img);}
    texto.append(badge(c.situacao, c.revisao ? "" : "orange"), el("h3", c.descricao), el("p", c.bairro + " · Registro local " + c.id.slice(0, 8) + " · " + data(c.criado_em)));
    row.append(texto, botao("Ver pedido", () => durante(row.querySelector("button"), () => detalhe(c.id)))); box.append(row);
  });
}
function preparacao(caso) {
  const p = caso.preparacao, box = el("article", null, "result");
  box.append(el('p','Pedido recebido · '+caso.id.slice(0,8).toUpperCase(),'receipt-id'),el('h2',caso.descricao),evidenciaVisual(caso));
  box.append(badge(p.faltantes.length ? "Precisa de conferência" : "Serviço para conferir", p.faltantes.length ? "orange" : ""));
  box.append(el("h2", p.servico ? p.servico.nome : "Vamos conferir o encaminhamento."));
  if(p.pergunta) box.append(el("p", p.pergunta, "lead"));
  if(p.servico) {box.append(el("p", p.servico.orientacao, "lead"), link("Consultar a orientação oficial", p.servico.url), el("p", "Canal: " + p.servico.canal, "fine"));}
  if(p.faltantes.length) box.append(el("p", "Pendências: " + p.faltantes.map(f => ({contexto:"contexto do local", local:"localização", enquadramento:"serviço para o caso da rampa"}[f] || f)).join("; ") + ".", "inset warning"));
  box.append(el("p", p.observacao, "fine"), el("p", "Registro local: " + caso.id + " · Fonte consultada em " + p.data_consulta, "fine"));
  const actions = el("div", null, "actions");
  actions.append(botao("Acompanhar este pedido", async () => {await navegar("acompanhar"); await detalhe(caso.id);}, "primary"), botao("Ver no mapa",async()=>{state.mapaId=caso.id;$('mapa-busca').value='';$('mapa-filtro').value='todos';await navegar('mapa');state.mapa?.focar(caso);},'secondary'), botao("Conferir informações", () => editar(caso), "quiet"));
  box.append(actions); return box;
}
formulario("pedido-form", async form => {
  const dados = Object.fromEntries(['descricao','bairro','local','contexto'].map(k=>[k,form.get(k)]));
  dados.confirmado = form.get("confirmado") === "on";
  dados.localizacao = coordenadas($('latitude').value, $('longitude').value, $('confirmar-localizacao').checked, state.origemGeo, state.precisaoGeo);
  dados.passagem = vinculoPassagem($('passagem-trecho').value,$('passagem-condicao').value);
  const editando = state.edicao;
  if (!editando) {
    const assinatura = assinaturaPedido(dados);
    if (state.assinatura !== assinatura || !state.envioId) {state.envioId = crypto.randomUUID(); state.assinatura = assinatura;}
    dados.envio_id = state.envioId;
  }
  const rascunhoEnviado=editando?null:state.rascunhoId;
  if(rascunhoEnviado && !await rascunho('atualizar',criarRascunho(Object.fromEntries(form),state))) {
    throw new Error('O rascunho salvo mudou em outra aba. Confira o rascunho ou salve este pedido novamente antes de enviar.');
  }
  const envio = new FormData(); envio.append('dados', JSON.stringify(dados));
  if (state.foto) envio.append('arquivo', state.foto, 'ocorrencia.jpg');
  if (editando) envio.append('remover_foto', String(state.removerFoto));
  const caso = await api('/api/atendimentos' + (editando ? '/' + editando : '') + '/com-anexo', {method:editando?'PUT':'POST', body:envio});
  if (rascunhoEnviado) {
    try {await rascunho('delete',rascunhoEnviado); $('rascunho-status').textContent = '';}
    catch {$('rascunho-status').textContent = 'Pedido registrado. Apague o rascunho salvo quando o navegador permitir.';}
  }
  cancelarEdicao();
  const resultado = $("preparacao-resultado"); resultado.replaceChildren(preparacao(caso)); resultado.hidden = false; $('pedido-form').hidden=true;$('request-progress').hidden=true;resultado.scrollIntoView({block:"start"});
  aviso(editando ? "Informações atualizadas. Se houve alteração, a decisão anterior precisa de nova revisão." : "Pedido registrado nesta demonstração. Confira a preparação abaixo.");
  try {await atualizar();} catch {aviso('Pedido '+caso.id.slice(0,8)+' registrado. A lista não pôde ser atualizada agora; confira novamente quando a central responder.');}
});
function cancelarEdicao() {state.edicao = null; $("pedido-form").reset(); limparFoto(); limparGeo(); state.envioId=null; state.assinatura=null; state.rascunhoId=null; $('salvar-rascunho').disabled=false; $("cancelar-edicao").hidden = true; $("pedido-form").querySelector("button[type=submit]").textContent = "Registrar pedido";mostrarEtapa(0,false);}
$("cancelar-edicao").addEventListener("click", cancelarEdicao);
async function editar(caso) {
  mostrarEtapa(0,false);
  await navegar("pedido"); state.edicao = caso.id;
  ["descricao", "bairro", "local", "contexto"].forEach(k => $(k).value = caso[k] || "");
  $('passagem-trecho').value=caso.passagem?.trecho_id||'';
  $('passagem-condicao').value=caso.passagem?.condicao||'nao_verificado';
  limparFoto(); limparGeo();
  if(caso.foto) {state.fotoAtual=caso.foto; mostrarFoto('/api/atendimentos/'+caso.id+'/foto?v='+caso.foto.sha256, 'Foto já registrada. Você pode manter, substituir ou remover.');}
  if(caso.localizacao) {const g=caso.localizacao; $('latitude').value=g.latitude; $('longitude').value=g.longitude; state.origemGeo=g.origem; state.precisaoGeo=g.precisao_m;sincronizarPonto();}
  $('salvar-rascunho').disabled=true;
  $("pedido-form").elements.confirmado.checked = false;
  $("pedido-form").querySelector("button[type=submit]").textContent = "Atualizar pedido";
  $("cancelar-edicao").hidden = false; $("preparacao-resultado").hidden = true;
  aviso("Editando o pedido " + caso.id.slice(0,8) + ". Alterações exigem nova revisão antes de confirmar no ZelaBairro."); $("descricao").focus();
}
async function detalhe(id, rolar = true) {
  const caso = await api("/api/atendimentos/" + encodeURIComponent(id));
  if (!rolar && state.selecionado?.id === id && state.selecionado.atualizado_em === caso.atualizado_em) return;
  state.selecionado = caso;
  const box = el("article", null, "panel detail");
  box.append(badge(caso.situacao), el("h2", caso.descricao), el("p", "Registro local " + caso.id, "fine"));
  const grid = el("div", null, "details-grid"), principal = el("div"), decisao = el("div");
  const dl = el("dl"); for(const [nome,valor] of [["Bairro",caso.bairro],["Local",caso.local || "Não informado"],["Serviço",caso.preparacao.servico?.nome || "Ainda não definido"],["Pendências",caso.preparacao.faltantes.join(", ") || "Informações disponíveis para conferência"]]) dl.append(el("dt",nome),el("dd",valor));
  principal.append(dl);
  principal.append(evidenciaVisual(caso));
  if(caso.preparacao.fonte) principal.append(link("Ver fonte do encaminhamento",caso.preparacao.fonte));
  if(caso.preparacao.pergunta) principal.append(el("p",caso.preparacao.pergunta,"inset warning"));
  principal.append(botao("Completar ou corrigir informações",()=>editar(caso),"quiet"));
  decisao.append(el("h3","Análise original do RPA"),el("p",caso.triagem_original.category+" · prioridade "+caso.triagem_original.priority,"inset"),el("p","Confiança heurística: "+caso.triagem_original.confidence+". Revisão indicada pelo RPA: "+(caso.triagem_original.review_required?"sim":"não")+".","fine"));
  decisao.append(el("p",caso.exige_revisao?"A central exige revisão deste caso.":"A confirmação no ZelaBairro também passa por conferência.","fine"));
  if(caso.revisao) {decisao.append(el("h3","Decisão revisada"),el("p",caso.revisao.prioridade+" · "+caso.revisao.justificativa,"inset"),el("p",caso.revisao.revisor+" · "+data(caso.revisao.data),"fine"));}
  if(caso.frontend) decisao.append(el("p","ZelaBairro: "+caso.frontend.id+" · protocolo local.","fine"));
  if(caso.protocolo_oficial) decisao.append(el("p","Protocolo externo informado: "+caso.protocolo_oficial.numero+". Não verificado no órgão.","inset warning"));
  grid.append(principal,decisao); box.append(grid);
  const forms = el("div",null,"details-grid divider"), contestar = el("form"), protocolo = el("form");
  contestar.append(el("h3","Pedir uma nova análise"));const motivo=el("textarea"); motivo.id="motivo-contestacao";motivo.minLength=10;motivo.maxLength=500;motivo.required=true;motivo.rows=3;const lm=el("label","Explique o que precisa ser reconsiderado");lm.htmlFor=motivo.id;
  const bc=el("button","Solicitar nova revisão","secondary");bc.type="submit";contestar.append(lm,motivo,bc);
  contestar.addEventListener("submit",e=>{e.preventDefault();durante(bc,async()=>{await enviar("/api/atendimentos/"+id+"/contestacao",{motivo:motivo.value});await atualizar();aviso("Nova análise solicitada. A revisão anterior ficou preservada no histórico.");});});
  protocolo.append(el("h3","Anotar protocolo externo"),el("p","Somente se você já abriu o chamado pelo canal oficial. Aqui o número é uma informação fornecida, sem confirmação do órgão.","fine"));const numero=el("input");numero.id="numero-protocolo";numero.required=true;numero.maxLength=80;const ln=el("label","Número informado");ln.htmlFor=numero.id;const bp=el("button","Salvar número informado","secondary");bp.type="submit";protocolo.append(ln,numero,bp);
  protocolo.addEventListener("submit",e=>{e.preventDefault();durante(bp,async()=>{await enviar("/api/atendimentos/"+id+"/protocolo",{protocolo:numero.value});await detalhe(id);aviso("Número externo anotado como informação não verificada.");});});
  forms.append(contestar,protocolo);box.append(forms,el("h3","Histórico do pedido","spaced"));
  box.append(historico(caso));
  $("detalhe-caso").replaceChildren(box);
  if (rolar) box.scrollIntoView({block:"start"});
}
$("atualizar-casos").addEventListener("click",e=>durante(e.currentTarget,atualizar));
async function resumoRevisao() {
  let caso=state.casos.find(c=>c.id===$("revisao-caso").value);const box=$("resumo-revisao");box.replaceChildren();
  $('revisao-decisao').replaceChildren();$('revisao-historico').replaceChildren();
  $('confirmar-frontend').disabled=true;$('frontend-resultado').textContent='';
  if(!caso){box.append(el("p","Nenhum pedido disponível para revisão."));return;}
  if(state.revisandoId!==caso.id){state.revisandoId=caso.id;$('justificativa').value='';$('prioridade').value=caso.revisao?.prioridade||caso.triagem_original.priority;}
  if(!document.querySelector('[data-panel="revisao"]').hidden) {
    const id=caso.id;box.append(el('p','Carregando evidências…','fine'));
    try {caso=await api('/api/atendimentos/'+encodeURIComponent(id));}
    catch(erro){aviso(erro.message,true);return;}
    if($('revisao-caso').value!==id)return;
    box.replaceChildren();
  }
  box.append(el('h3',caso.descricao),badge(caso.situacao),evidenciaVisual(caso),el('p',(caso.local||'Referência não informada')+' · '+caso.bairro),el('p','Registro '+caso.id.slice(0,8).toUpperCase(),'fine'),botao('Abrir pedido e contestação',async()=>{await navegar('acompanhar');await detalhe(caso.id);},'quiet'));
  const decisao=$('revisao-decisao');decisao.append(el('p','Sugestão original do RPA','fine'),el('p',caso.triagem_original.priority+' · '+caso.triagem_original.category,'inset'),el('p','Regra heurística; não é uma avaliação de segurança.','fine'));
  if(caso.exige_revisao)decisao.append(el('p','Revisão humana obrigatória para este pedido.','inset warning'));
  if(caso.revisao) {decisao.append(el('h3','Decisão da revisão'),el('p',caso.revisao.prioridade+' · '+caso.revisao.justificativa,'inset warning'),el('p',caso.revisao.revisor+' · '+data(caso.revisao.data),'fine'));}
  else {const anterior=caso.historico?.filter(e=>e.acao==='Decisão revisada').at(-1)?.dados;if(anterior){decisao.append(el('h3','Decisão anterior'),el('p',anterior.prioridade+' · '+anterior.justificativa,'inset'),el('p','Esta decisão está no histórico. É necessária nova revisão antes de confirmar.','fine'));}}
  decisao.append(el('p','Pendências: '+(caso.preparacao.faltantes.join(', ')||'informações preenchidas'),'fine'));
  if(caso.preparacao.fonte)decisao.append(link('Fonte do encaminhamento',caso.preparacao.fonte));
  $('revisao-historico').append(historico(caso));
  $("frontend-resultado").textContent=caso.frontend?"Registro local: "+caso.frontend.id:"";
  $("confirmar-frontend").disabled=!caso.revisao||caso.preparacao.faltantes.length>0;
}
$("revisao-caso").addEventListener("change",resumoRevisao);
formulario("revisao-form",async form=>{const id=$("revisao-caso").value;if(!id)throw new Error("Selecione um pedido.");await enviar("/api/atendimentos/"+id+"/revisao",Object.fromEntries(form),$("chave").value);await atualizar();aviso("Decisão registrada com justificativa. A análise original permanece no histórico.");});
$("confirmar-frontend").addEventListener("click",e=>durante(e.currentTarget,async()=>{if(!$("chave").value)throw new Error("Preencha a chave local de revisão.");const id=$("revisao-caso").value;const caso=await enviar("/api/atendimentos/"+id+"/zelabairro",{},$("chave").value);await atualizar();$("frontend-resultado").textContent="Registro local confirmado: "+caso.frontend.id+". Não é um protocolo municipal.";aviso("Registro confirmado na persistência do ZelaBairro.");}));
formulario("lote-form",async()=>{if(!$("chave").value)throw new Error("Preencha a chave local de revisão.");const arquivo=$("lote-arquivo").files[0];if(arquivo.size>1024*1024)throw new Error("O CSV deve ter até 1 MB.");const form=new FormData();form.append("arquivo",arquivo);const resultado=await api("/api/lotes",{method:"POST",headers:{"X-Manager-Key":$("chave").value},body:form});$("lote-resultado").textContent=JSON.stringify(resultado.resumo,null,2);$("lote-resultado").hidden=false;await atualizar();aviso("Lote processado. Registros aceitos: "+resultado.atendimentos.length+"; rejeitados pelo RPA: "+resultado.rejeitados.length+".");});
formulario("assistente-form",async()=>{const box=$("assistente-resultado");box.replaceChildren(el("p","Consultando o modelo local. A operação pode levar até um minuto…","fine"));try{const r=await enviar("/api/assistente",{pergunta:$("pergunta").value,atendimento_id:$("evidencia-caso").value||null});box.replaceChildren(el("p",r.resposta,"inset"),el("p","Status: "+r.status+" · "+r.modo,"fine"));if(r.fonte)box.append(link("Consultar a fonte da orientação",r.fonte.url));if($("evidencia-caso").value)box.append(el("p","Saída vinculada ao histórico do pedido.","fine"));}catch(erro){box.replaceChildren(el("p",erro.message,"inset warning"));throw erro;}});
formulario("visao-form",async()=>{const arquivo=$("imagem").files[0];if(arquivo.size>8*1024*1024)throw new Error("A imagem deve ter até 8 MB.");const form=new FormData();form.append("arquivo",arquivo);form.append("atendimento_id",$("evidencia-caso").value);const box=$("visao-resultado");box.replaceChildren(el("p","Executando o modelo de Visão…","fine"));try{const r=await api("/api/visao",{method:"POST",body:form});box.replaceChildren(el("p",r.rotulo||r.classe||r.resultado||"Inferência concluída","inset"),el("p",r.limite,"fine"));const details=el("details");details.append(el("summary","Ver saída e parâmetros"),json(r));box.append(details);}catch(erro){box.replaceChildren(el("p",erro.message,"inset warning"));throw erro;}});
formulario("fontes-form",async()=>{const fontes=await api("/api/fontes?q="+encodeURIComponent($("busca").value));const box=$("fontes-resultado");box.replaceChildren();if(!fontes.length)box.append(el("p","Nenhum trecho localizado. Tente outro termo do assunto.","inset"));fontes.forEach(f=>{const card=el("article",null,"source-card");card.append(badge("LINHA "+f.linha_corpus),el("p",f.text),link(f.fonte||"Consultar fonte",f.url),el("p",(f.paginas?"Páginas: "+f.paginas.join(", "):"Seção: "+f.secao)+" · "+(f.data_coleta||f.data_acesso||"Data registrada no corpus"),"fine"));card.append(botao("Vincular este trecho ao pedido",e=>durante(e.currentTarget,async()=>{const id=$("evidencia-caso").value;if(!id)throw new Error("Selecione um pedido para vincular o trecho.");await enviar("/api/atendimentos/"+id+"/evidencia-pln",{linha_corpus:f.linha_corpus});aviso("Trecho e origem vinculados ao histórico do pedido.");})));box.append(card);});});
async function ativos() {
  const materiais = await api("/api/ativos"), box = $("ativos");
  const nomes = {
    rpa_notebook: "Notebook entregue", rpa_codigo: "Pipeline de triagem",
    cluster_relatorio: "Relatório", cluster_2: "Modelo com 2 workers", cluster_4: "Modelo com 4 workers",
    quantica_relatorio: "Relatório",
    frontend_readme: "Instruções do ZelaBairro", frontend_testes: "Verificações do módulo", frontend_video: "Vídeo do ZelaBairro",
    genai_relatorio: "Relatório", genai_resultados: "Avaliações registradas", genai_corpus: "Fontes do assistente",
    iot_relatorio: "Relatório do OuviAí", iot_videos: "Links das gravações", iot_enunciado: "Enunciado de IoT",
    pln_relatorio: "Relatório da fábrica", pln_revisao: "Planilha de revisão", pln_corpus_texto: "Corpus de textos",
    pln_corpus_qa: "Perguntas e respostas", pln_corpus_chat: "Diálogos", pln_corpus_teste: "Casos de teste", pln_qualidade: "Relatório de qualidade",
    visao_relatorio: "Relatório", visao_codigo: "Rotina de inferência", visao_metricas: "Métricas do modelo",
    visao_treino: "Código de treinamento", visao_manifesto: "Relação dos recortes", visao_video: "Vídeo de demonstração"
  };
  box.replaceChildren();
  materiais.forEach(m => {
    const row = el("article", null, "asset"), identidade = el("div", null, "asset-identity"), conteudo = el("div", null, "asset-main");
    identidade.append(el("h3", m.nome), badge(m.modo, ["cluster", "quantica", "iot"].includes(m.id) ? "orange" : ""));
    conteudo.append(el("p", m.resumo), el("p", m.limite, "limit"));
    if (m.metricas) {
      const ul = el("ul", null, "mini-metrics");
      m.metricas.forEach(k => { const li = el("li"); li.append(el("span", k.nome + ":"), el("strong", k.valor)); ul.append(li); });
      conteudo.append(ul);
    }
    const links = el("div", null, "material-links");
    m.materiais.forEach(id => links.append(link(nomes[id] || "Abrir arquivo", "/api/materiais/" + encodeURIComponent(id))));
    (m.videos || []).forEach(v => links.append(link(v.nome, v.url)));
    row.append(identidade, conteudo, links); box.append(row);
  });
  state.ativos = true;
}
function evidenciaVisual(caso) {
  const box=el('div',null,'case-evidence');
  if(caso.foto) {const img=el('img'); img.src='/api/atendimentos/'+encodeURIComponent(caso.id)+'/foto?v='+caso.foto.sha256; img.alt='Foto anexada ao relato: '+caso.descricao; img.loading='lazy'; box.append(img,el('p','Foto fornecida pelo solicitante. Não constitui detecção de buraco ou laudo.','fine'));}
  if(caso.localizacao) {const g=caso.localizacao; box.append(el('p','Coordenadas confirmadas: '+g.latitude.toFixed(6)+', '+g.longitude.toFixed(6),'fine'),el('p',(g.origem==='gps'?'Posição do aparelho':'Coordenadas digitadas')+(g.precisao_m!==null?' · precisão informada pelo aparelho: '+Math.round(g.precisao_m)+' m':'')+'. Endereço não verificado.','fine'));}
  if(caso.passagem) {
    const v=caso.passagem;
    const trecho=[...$('passagem-trecho').options].find(o=>o.value===v.trecho_id)?.textContent||v.trecho_id;
    const condicao={bloqueado:'passagem interrompida',dificultado:'passagem dificultada',nao_verificado:'condição não verificada'}[v.condicao];
    box.append(el('p','Passagem Livre · '+trecho+' · '+condicao,'inset'),
      el('p','Associação declarada ao cenário didático; sem confirmação geográfica automática.','fine'),
      botao('Ver planejamento do percurso',()=>navegar('passagem'),'secondary'));
  }
  return box;
}
function mostrarFoto(url, mensagem) {
  fecharCamera();
  if(state.fotoUrl) URL.revokeObjectURL(state.fotoUrl);
  state.fotoUrl=url.startsWith('blob:')?url:null;
  $('foto-preview').src=url; $('foto-previa').hidden=false; $('foto-status').textContent=mensagem;
  $('camera-vazia').hidden=true;$('remover-foto').hidden=false;
}
function limparFoto() {
  if(state.fotoUrl) URL.revokeObjectURL(state.fotoUrl);
  Object.assign(state,{foto:null,fotoAtual:null,fotoUrl:null,removerFoto:false});
  $('foto-preview').removeAttribute('src'); $('foto-previa').hidden=true;
  $('foto-camera').value=''; $('foto-galeria').value='';
  $('camera-vazia').hidden=false;$('remover-foto').hidden=true;fecharCamera();
}
for(const id of ['foto-camera','foto-galeria']) $(id).addEventListener('change',async()=>{
  const arquivo=$(id).files[0]; if(!arquivo)return;
  try {await bloquearDurante([...$('pedido-form').querySelectorAll('button,input[type=file]')],async()=>{
    const foto=await reduzirFoto(arquivo); state.foto=foto; state.removerFoto=false; state.envioId=null; mostrarFoto(URL.createObjectURL(foto),'Foto preparada: '+Math.ceil(foto.size/1024)+' KB.');
  });} catch(erro){aviso(erro.message,true);} finally {$(id).value='';}
});
$('remover-foto').addEventListener('click',()=>{limparFoto(); state.removerFoto=true; state.envioId=null;});
function cancelarGeo() {state.leituraGeo?.abort();state.leituraGeo=null;}
function limparGeo() {cancelarGeo();for(const id of ['latitude','longitude'])$(id).value=''; $('confirmar-localizacao').checked=false; state.origemGeo='manual'; state.precisaoGeo=null; state.mapaLocal?.ponto(null);$('localizacao-status').textContent='Você pode marcar no mapa, digitar coordenadas ou continuar sem GPS.';}
$('limpar-localizacao').addEventListener('click',limparGeo);
for(const id of ['latitude','longitude'])$(id).addEventListener('input',()=>{cancelarGeo();state.origemGeo='manual';state.precisaoGeo=null;$('confirmar-localizacao').checked=false;sincronizarPonto();$('localizacao-status').textContent='Coordenadas editadas. Confira o ponto e confirme novamente.';});
$('obter-localizacao').addEventListener('click',e=>bloquearDurante([e.currentTarget],async()=>{
  if(!window.isSecureContext || !navigator.geolocation)throw new Error('O GPS precisa de HTTPS e permissão no navegador. Digite a referência ou coordenadas manualmente.');
  cancelarGeo();const leitura=new AbortController();state.leituraGeo=leitura;
  $('localizacao-status').textContent='Aguardando sua permissão e a posição do aparelho…';
  try {
    const pos=await obterPosicao(navigator.geolocation,leitura.signal);
    if(!pos||leitura.signal.aborted)return;
    $('latitude').value=pos.coords.latitude.toFixed(6); $('longitude').value=pos.coords.longitude.toFixed(6);
    state.origemGeo='gps'; state.precisaoGeo=Math.min(100000,pos.coords.accuracy); $('confirmar-localizacao').checked=false;
    sincronizarPonto();
    $('localizacao-status').textContent='Posição recebida, com precisão aproximada de '+Math.round(pos.coords.accuracy)+' m. Confira o local antes de confirmar.';
  } catch(erro) {if(leitura.signal.aborted)return;const mensagem=erroLocalizacao(erro.code);$('localizacao-status').textContent=mensagem;throw new Error(mensagem);}
  finally{if(state.leituraGeo===leitura)state.leituraGeo=null;}
}).catch(erro=>aviso(erro.message,true)));
$('salvar-rascunho').addEventListener('click',e=>durante(e.currentTarget,async()=>{
  if(state.edicao)throw new Error('Conclua a edição antes de salvar um novo rascunho.');
  const novoId=crypto.randomUUID();
  await rascunho('put',criarRascunho(Object.fromEntries(new FormData($('pedido-form'))),{...state,rascunhoId:novoId}));
  state.rascunhoId=novoId;
  $('rascunho-status').textContent='Rascunho salvo neste navegador, sem envio. Data: '+data(new Date().toISOString());
}));
$('restaurar-rascunho').addEventListener('click',e=>durante(e.currentTarget,async()=>{
  if(state.edicao)throw new Error('Cancele ou conclua a edição antes de recuperar um rascunho.');
  const salvo=await rascunho('get'); if(!salvo)throw new Error('Nenhum rascunho salvo neste navegador.');
  cancelarEdicao(); for(const [k,v] of Object.entries(dadosRascunho(salvo.campos))) $(k).value=v;
  state.envioId=salvo.envioId;
  try {state.assinatura=salvo.assinatura?assinaturaPedido(JSON.parse(salvo.assinatura)):null;} catch {state.assinatura=null;}
  state.rascunhoId=salvo.id||crypto.randomUUID(); state.origemGeo=salvo.origemGeo||'manual'; state.precisaoGeo=salvo.precisaoGeo??null;
  if(salvo.foto instanceof Blob){state.foto=salvo.foto; mostrarFoto(URL.createObjectURL(salvo.foto),'Foto recuperada do rascunho.');}
  sincronizarPonto();
  $('rascunho-status').textContent='Rascunho de '+data(salvo.salvoEm)+' recuperado. Confira os dados e confirme novamente antes de enviar.';
}));
$('apagar-rascunho').addEventListener('click',e=>durante(e.currentTarget,async()=>{await rascunho('delete');state.rascunhoId=null;$('rascunho-status').textContent='Rascunho salvo apagado deste navegador. O formulário atual foi mantido.';}));
function conexao() {$('conexao').hidden=navigator.onLine;}
window.addEventListener('online',conexao); window.addEventListener('offline',conexao); conexao();
let instalacao;
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();instalacao=e;$('instalar').hidden=false;});
$('instalar').addEventListener('click',e=>durante(e.currentTarget,async()=>{if(instalacao){await instalacao.prompt();await instalacao.userChoice;instalacao=null;$('instalar').hidden=true;}}));
if('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(()=>{$('rascunho-status').textContent='A abertura sem rede não está disponível neste navegador. O rascunho pode ser salvo separadamente.';});

function historico(caso) {
  const timeline=el('ol',null,'timeline');
  (caso.historico||[]).forEach(evento=>{const li=el('li');li.append(el('strong',evento.acao),el('small',data(evento.data)+' · '+evento.autor));
    if(evento.acao==='Decisão revisada')li.append(el('p',evento.dados.prioridade+' · '+evento.dados.justificativa,'history-decision'));
    if(evento.dados?.motivo)li.append(el('p',evento.dados.motivo,'inset warning'));
    const registro=el('details');registro.append(el('summary','Ver registro da etapa'),json(evento.dados));li.append(registro);timeline.append(li);
  });return timeline;
}
function renderMapa() {
  const primeiroMapa=!state.mapa;
  if(!state.mapa)state.mapa=criarMapa('mapa-central','mapa-status');
  const casos=filtrarCasos(state.casos,$('mapa-busca').value,$('mapa-filtro').value);
  if(!casos.some(c=>c.id===state.mapaId))state.mapaId=(casos.find(c=>pontoValido(c)&&c.foto)||casos[0])?.id;
  const caso=casos.find(c=>c.id===state.mapaId),box=$('mapa-selecao');box.replaceChildren();
  const abrir=id=>{state.mapaId=id;renderMapa();const c=state.casos.find(c=>c.id===id);state.mapa?.focar(c);if(matchMedia('(max-width:680px)').matches)box.scrollIntoView({block:'start'});};
  state.mapa?.casos(casos,state.mapaId,abrir);state.mapa?.resize();
  if(primeiroMapa)state.mapa?.enquadrar(casos);
  if(caso) {
    box.append(badge(caso.situacao,caso.revisao?'':'orange'),el('p','Registro '+caso.id.slice(0,8).toUpperCase(),'fine'));
    if(caso.foto){const img=el('img',null,'map-case-image');img.src='/api/atendimentos/'+encodeURIComponent(caso.id)+'/foto?v='+caso.foto.sha256;img.alt='Foto anexada à ocorrência selecionada';box.append(img);}
    box.append(el('h2',caso.descricao),el('p',(caso.local||'Referência não informada')+' · '+caso.bairro,'case-place'));
    if(!pontoValido(caso))box.append(el('p','Este pedido está sem ponto confirmado no mapa. Você pode completar as informações.','inset warning'));
    const perto=proximos(caso,state.casos),area=el('div',null,'nearby');
    if(perto.length) {
      area.append(el('h3','Outros relatos próximos'),el('p','Até 100 m em linha reta. Proximidade não confirma que seja o mesmo problema.'));
      perto.slice(0,3).forEach(v=>area.append(botao(Math.round(v.metros)+' m · '+v.caso.descricao,()=>{state.mapaId=v.caso.id;$('mapa-busca').value='';$('mapa-filtro').value='todos';abrir(v.caso.id);},'nearby-case')));box.append(area);
    }
    const actions=el('div',null,'actions');actions.append(botao('Abrir histórico',async()=>{await navegar('acompanhar');await detalhe(caso.id);},'secondary'),botao('Revisar pedido',async()=>{await navegar('revisao');$('revisao-caso').value=caso.id;await resumoRevisao();},'primary'));box.append(actions);
  }else box.append(el('h2','O primeiro ponto começa com você.'),el('p',state.casos.length?'Nenhum pedido corresponde à busca. Ajuste os filtros.':'Registre uma ocorrência com dados fictícios para acompanhar o processo.','muted'));
  $('mapa-contagem').textContent=casos.length+' pedido'+(casos.length===1?'':'s');
  const lista=$('mapa-lista');lista.replaceChildren();
  casos.forEach(c=>{const b=botao('',()=>abrir(c.id),'map-case');b.setAttribute('aria-pressed',String(c.id===state.mapaId));b.append(el('strong',c.descricao),el('small',c.bairro+' · '+c.situacao+(pontoValido(c)?'':' · sem ponto no mapa')));lista.append(b);});
}
$('mapa-busca').addEventListener('input',renderMapa);$('mapa-filtro').addEventListener('change',renderMapa);
$('enquadrar-mapa').addEventListener('click',()=>state.mapa?.enquadrar(filtrarCasos(state.casos,$('mapa-busca').value,$('mapa-filtro').value)));
function pontoFormulario() {
  try{return coordenadas($('latitude').value,$('longitude').value,true,state.origemGeo,state.precisaoGeo);}catch{return null;}
}
function sincronizarPonto() {state.mapaLocal?.ponto(pontoFormulario());}
function escolherPonto(latitude,longitude) {
  cancelarGeo();
  $('latitude').value=latitude.toFixed(6);$('longitude').value=longitude.toFixed(6);state.origemGeo='manual';state.precisaoGeo=null;$('confirmar-localizacao').checked=false;
  state.mapaLocal?.ponto(pontoFormulario(),false);$('localizacao-status').textContent='Ponto ajustado no mapa. Confira a referência e confirme as coordenadas abaixo.';
}
function conferirEtapa(n) {
  if(n>=1 && !$('descricao').reportValidity()){mostrarEtapa(0);return false;}
  if(n>=2) {
    if(!$('bairro').reportValidity()){mostrarEtapa(1);return false;}
    if(!$('local').reportValidity()){mostrarEtapa(1);return false;}
    try{coordenadas($('latitude').value,$('longitude').value,$('confirmar-localizacao').checked,state.origemGeo,state.precisaoGeo);}
    catch(erro){mostrarEtapa(1);aviso(erro.message,true);$('confirmar-localizacao').focus();return false;}
  }return true;
}
function mostrarEtapa(n,foco=true) {
  state.etapa=n;if(n!==0)fecharCamera();
  if(n!==1)cancelarGeo();
  document.querySelectorAll('[data-request-step]').forEach(p=>p.hidden=Number(p.dataset.requestStep)!==n);
  document.querySelectorAll('[data-step]').forEach(b=>{if(Number(b.dataset.step)===n)b.setAttribute('aria-current','step');else b.removeAttribute('aria-current');});
  if(n===1){if(!state.mapaLocal)state.mapaLocal=criarMapa('mapa-local','mapa-local-status',escolherPonto);state.mapaLocal?.resize();sincronizarPonto();}
  if(n===2){const box=$('pedido-conferencia');box.replaceChildren();if(state.foto||state.fotoAtual){const img=el('img');img.src=$('foto-preview').src;img.alt='Foto que acompanhará o pedido';box.append(img);}const texto=el('div');texto.append(el('h3',$('descricao').value),el('p',($('local').value||'Sem referência textual')+' · '+$('bairro').value),el('p',$('contexto').selectedOptions[0].textContent,'fine'));const g=pontoFormulario();texto.append(el('p',g?'Ponto confirmado: '+g.latitude.toFixed(6)+', '+g.longitude.toFixed(6):'Sem coordenadas: a localização depende da referência informada.','inset'));box.append(texto);}
  if(n===2&&$('passagem-trecho').value)$('pedido-conferencia').append(el('p','Vínculo declarado: '+$('passagem-trecho').selectedOptions[0].textContent+' · '+$('passagem-condicao').selectedOptions[0].textContent+'. Percurso didático, sem confirmação espacial.','inset'));
  if(foco){const alvo=document.querySelector('[data-request-step="'+n+'"] h2');if(alvo){alvo.tabIndex=-1;alvo.focus();} $('request-progress').scrollIntoView({block:'start'});}
}
document.querySelectorAll('[data-step],[data-next],[data-back]').forEach(b=>b.addEventListener('click',()=>{const n=Number(b.dataset.step??b.dataset.next??b.dataset.back);if(n<=state.etapa||conferirEtapa(n))mostrarEtapa(n);}));
$('seguir-texto').addEventListener('click',()=>{if(conferirEtapa(1))mostrarEtapa(1);});
$('pedido-form').addEventListener('invalid',e=>{const p=e.target.closest('[data-request-step]');if(p)mostrarEtapa(Number(p.dataset.requestStep),false);},true);
function fecharCamera() {
  state.leituraCamera?.abort();state.leituraCamera=null;
  state.camera?.getTracks().forEach(t=>t.stop());state.camera=null;$('camera-video').srcObject=null;$('camera-video').hidden=true;
  $('ativar-camera').hidden=false;$('capturar-camera').hidden=true;$('fechar-camera').hidden=true;
  $('camera-status').textContent='Você pode usar foto, imagem da galeria ou somente texto.';
}
$('ativar-camera').addEventListener('click',e=>bloquearDurante([e.currentTarget],async()=>{
  if(!isSecureContext||!navigator.mediaDevices?.getUserMedia){$('camera-status').textContent='Câmera ao vivo indisponível. Use “Câmera do aparelho” ou escolha uma imagem.';return;}
  fecharCamera();const leitura=new AbortController();state.leituraCamera=leitura;$('fechar-camera').hidden=false;$('camera-status').textContent='Aguardando a permissão da câmera. Você pode cancelar e continuar por texto.';
  try{const stream=await abrirCamera(navigator.mediaDevices,leitura.signal);
    if(!stream)return;
    if(leitura.signal.aborted||state.etapa!==0||document.querySelector('[data-panel="pedido"]').hidden){stream.getTracks().forEach(t=>t.stop());return;}
    state.camera=stream;$('camera-video').srcObject=stream;$('camera-video').hidden=false;$('ativar-camera').hidden=true;$('capturar-camera').hidden=false;$('fechar-camera').hidden=false;$('camera-status').textContent='Enquadre o problema e toque em Capturar foto.';
  }catch{if(!leitura.signal.aborted){fecharCamera();$('camera-status').textContent='Câmera não autorizada ou indisponível. Escolha uma imagem ou use a câmera do aparelho.';}}
  finally{if(state.leituraCamera===leitura)state.leituraCamera=null;}
}).catch(erro=>aviso(erro.message,true)));
$('fechar-camera').addEventListener('click',fecharCamera);window.addEventListener('pagehide',fecharCamera);
$('capturar-camera').addEventListener('click',e=>durante(e.currentTarget,async()=>{
  const video=$('camera-video');if(!video.videoWidth)throw new Error('A imagem da câmera ainda não está pronta. Aguarde e tente novamente.');
  const canvas=document.createElement('canvas');canvas.width=video.videoWidth;canvas.height=video.videoHeight;canvas.getContext('2d').drawImage(video,0,0);
  const arquivo=await new Promise(resolve=>canvas.toBlob(resolve,'image/jpeg',.9));if(!arquivo)throw new Error('Não foi possível capturar. Escolha uma imagem.');
  const foto=await reduzirFoto(arquivo);state.foto=foto;state.removerFoto=false;state.envioId=null;fecharCamera();mostrarFoto(URL.createObjectURL(foto),'Foto capturada e preparada: '+Math.ceil(foto.size/1024)+' KB.');
}));
const passagem=iniciarPassagem({api,enviar,el,botao,badge,data,aviso,durante,
  abrir:async id=>{await navegar('acompanhar');await detalhe(id);},
  revisar:async id=>{await navegar('revisao');$('revisao-caso').value=id;await resumoRevisao();},
  evidencias:async id=>{await navegar('evidencias');$('evidencia-caso').value=id;aviso('As próximas consultas serão vinculadas ao pedido '+id.slice(0,8)+'. Use evidências pertinentes.');},
  novo:async trecho=>{if(state.edicao){aviso('Conclua ou cancele a edição atual antes de registrar outra observação.',true);return;}await navegar('pedido');$('passagem-trecho').value=trecho;$('passagem-condicao').value='nao_verificado';mostrarEtapa(0);}
});
navegar(location.hash.slice(1)||(matchMedia('(max-width:680px)').matches?'pedido':'mapa'),false);
