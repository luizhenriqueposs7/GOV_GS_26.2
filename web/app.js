"use strict";
const $ = (id) => document.getElementById(id);
const state = {casos: [], selecionado: null, edicao: null, ativos: false};
const titulos = {pedido: "PREPARAR PEDIDO", acompanhar: "ACOMPANHAR", revisao: "REVISÃO", evidencias: "EVIDÊNCIAS"};
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
  const resposta = await fetch(url, options);
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
  try { await acao(); } catch (erro) { aviso(erro.message || "Não foi possível concluir a operação.", true); }
  finally { botao.disabled = false; botao.textContent = anterior; }
}
function formulario(id, acao) {
  $(id).addEventListener("submit", (event) => {event.preventDefault(); durante(event.submitter, () => acao(new FormData(event.currentTarget)));});
}
async function navegar(view, foco = true) {
  if (!titulos[view]) view = "pedido";
  document.querySelectorAll("[data-panel]").forEach(n => n.hidden = n.dataset.panel !== view);
  document.querySelectorAll("[data-view]").forEach(n => {n.classList.toggle("active", n.dataset.view === view); if(n.dataset.view === view) n.setAttribute("aria-current", "page"); else n.removeAttribute("aria-current");});
  $("breadcrumb").textContent = "ATENDIMENTO / " + titulos[view];
  if (location.hash !== "#" + view) history.replaceState(null, "", "#" + view);
  if (foco) { $("principal").focus(); window.scrollTo(0, 0); }
  try { await atualizar(); if (view === "evidencias" && !state.ativos) await ativos(); }
  catch (erro) { aviso(erro.message, true); }
}
document.querySelectorAll("[data-view]").forEach(n => n.addEventListener("click", () => navegar(n.dataset.view)));
window.addEventListener("hashchange", () => navegar(location.hash.slice(1)));
document.querySelector(".brand").addEventListener("click", () => navegar("pedido"));
async function atualizar() {
  const [casos, indicadores] = await Promise.all([api("/api/atendimentos"), api("/api/indicadores")]);
  state.casos = casos;
  lista(); metricas(indicadores);
  for (const id of ["revisao-caso", "evidencia-caso"]) {
    const select = $(id), valor = select.value;
    select.replaceChildren();
    if (id === "evidencia-caso") {const vazio = el("option", "Consultar sem vínculo"); vazio.value = ""; select.append(vazio);}
    casos.forEach(c => {const option = el("option", c.descricao.slice(0, 65) + " · " + c.id.slice(0, 8)); option.value = c.id; select.append(option);});
    if ([...select.options].some(n => n.value === valor)) select.value = valor;
  }
  resumoRevisao();
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
    texto.append(badge(c.situacao, c.revisao ? "" : "orange"), el("h3", c.descricao), el("p", c.bairro + " · Registro local " + c.id.slice(0, 8) + " · " + data(c.criado_em)));
    row.append(texto, botao("Ver pedido ↗", () => durante(row.querySelector("button"), () => detalhe(c.id)))); box.append(row);
  });
}
function preparacao(caso) {
  const p = caso.preparacao, box = el("article", null, "result");
  box.append(badge(p.faltantes.length ? "PRECISA DE CONFERÊNCIA" : "SERVIÇO PARA CONFERIR", p.faltantes.length ? "orange" : ""));
  box.append(el("h2", p.servico ? p.servico.nome : "Vamos conferir o encaminhamento."));
  if(p.pergunta) box.append(el("p", p.pergunta, "lead"));
  if(p.servico) {box.append(el("p", p.servico.orientacao, "lead"), link("Consultar a orientação oficial ↗", p.servico.url), el("p", "Canal: " + p.servico.canal, "fine"));}
  if(p.faltantes.length) box.append(el("p", "Pendências: " + p.faltantes.map(f => ({contexto:"contexto do local", local:"localização", enquadramento:"serviço para o caso da rampa"}[f] || f)).join("; ") + ".", "inset warning"));
  box.append(el("p", p.observacao, "fine"), el("p", "Registro local: " + caso.id + " · Fonte consultada em " + p.data_consulta, "fine"));
  const actions = el("div", null, "actions");
  actions.append(botao("Acompanhar este pedido", async () => {await navegar("acompanhar"); await detalhe(caso.id);}, "primary"), botao("Conferir informações", () => editar(caso), "quiet"));
  box.append(actions); return box;
}
formulario("pedido-form", async form => {
  const dados = Object.fromEntries(form); dados.confirmado = form.get("confirmado") === "on";
  const editando = state.edicao;
  const caso = await enviar("/api/atendimentos" + (editando ? "/" + editando : ""), dados, null, editando ? "PUT" : "POST");
  cancelarEdicao(); await atualizar();
  const resultado = $("preparacao-resultado"); resultado.replaceChildren(preparacao(caso)); resultado.hidden = false; resultado.scrollIntoView({block:"start"});
  aviso(editando ? "Informações atualizadas. Se houve alteração, a decisão anterior precisa de nova revisão." : "Pedido registrado nesta demonstração. Confira a preparação abaixo.");
});
function cancelarEdicao() {state.edicao = null; $("pedido-form").reset(); $("cancelar-edicao").hidden = true; $("pedido-form").querySelector("button[type=submit]").textContent = "Preparar meu pedido ↗";}
$("cancelar-edicao").addEventListener("click", cancelarEdicao);
async function editar(caso) {
  await navegar("pedido"); state.edicao = caso.id;
  ["descricao", "bairro", "local", "contexto"].forEach(k => $(k).value = caso[k] || "");
  $("pedido-form").elements.confirmado.checked = false;
  $("pedido-form").querySelector("button[type=submit]").textContent = "Atualizar pedido";
  $("cancelar-edicao").hidden = false; $("preparacao-resultado").hidden = true;
  aviso("Editando o pedido " + caso.id.slice(0,8) + ". Alterações exigem nova revisão antes de confirmar no ZelaBairro."); $("descricao").focus();
}
async function detalhe(id) {
  const caso = await api("/api/atendimentos/" + encodeURIComponent(id)); state.selecionado = id;
  const box = el("article", null, "panel detail");
  box.append(badge(caso.situacao), el("h2", caso.descricao), el("p", "Registro local " + caso.id, "fine"));
  const grid = el("div", null, "details-grid"), principal = el("div"), decisao = el("div");
  const dl = el("dl"); for(const [nome,valor] of [["Bairro",caso.bairro],["Local",caso.local || "Não informado"],["Serviço",caso.preparacao.servico?.nome || "Ainda não definido"],["Pendências",caso.preparacao.faltantes.join(", ") || "Informações disponíveis para conferência"]]) dl.append(el("dt",nome),el("dd",valor));
  principal.append(dl);
  if(caso.preparacao.fonte) principal.append(link("Ver fonte do encaminhamento ↗",caso.preparacao.fonte));
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
  contestar.addEventListener("submit",e=>{e.preventDefault();durante(bc,async()=>{await enviar("/api/atendimentos/"+id+"/contestacao",{motivo:motivo.value});await atualizar();await detalhe(id);aviso("Nova análise solicitada. A revisão anterior ficou preservada no histórico.");});});
  protocolo.append(el("h3","Anotar protocolo externo"),el("p","Somente se você já abriu o chamado pelo canal oficial. Aqui o número é uma informação fornecida, sem confirmação do órgão.","fine"));const numero=el("input");numero.id="numero-protocolo";numero.required=true;numero.maxLength=80;const ln=el("label","Número informado");ln.htmlFor=numero.id;const bp=el("button","Salvar número informado","secondary");bp.type="submit";protocolo.append(ln,numero,bp);
  protocolo.addEventListener("submit",e=>{e.preventDefault();durante(bp,async()=>{await enviar("/api/atendimentos/"+id+"/protocolo",{protocolo:numero.value});await detalhe(id);aviso("Número externo anotado como informação não verificada.");});});
  forms.append(contestar,protocolo);box.append(forms,el("h3","Histórico do pedido","spaced"));
  const timeline=el("ol",null,"timeline");caso.historico.forEach(evento=>{const li=el("li");li.append(el("strong",evento.acao),el("small",data(evento.data)+" · "+evento.autor));const details=el("details");details.append(el("summary","Ver registro da etapa"),json(evento.dados));li.append(details);timeline.append(li);});box.append(timeline);
  $("detalhe-caso").replaceChildren(box);box.scrollIntoView({block:"start"});
}
$("atualizar-casos").addEventListener("click",e=>durante(e.currentTarget,atualizar));
function resumoRevisao() {
  const caso=state.casos.find(c=>c.id===$("revisao-caso").value),box=$("resumo-revisao");box.replaceChildren();
  if(!caso){box.append(el("p","Nenhum pedido disponível para revisão."));return;}
  box.append(el("p",caso.descricao),el("p","RPA original: "+caso.triagem_original.priority+" · "+caso.triagem_original.category),el("p","Situação: "+caso.situacao),el("p","Pendências: "+(caso.preparacao.faltantes.join(", ")||"informações preenchidas"),"fine"));
  if(caso.revisao)box.append(el("p","Revisão atual: "+caso.revisao.prioridade+" · "+caso.revisao.justificativa,"fine"));
  $("frontend-resultado").textContent=caso.frontend?"Registro local: "+caso.frontend.id:"";
  $("confirmar-frontend").disabled=!caso.revisao||caso.preparacao.faltantes.length>0;
}
$("revisao-caso").addEventListener("change",resumoRevisao);
formulario("revisao-form",async form=>{const id=$("revisao-caso").value;if(!id)throw new Error("Selecione um pedido.");await enviar("/api/atendimentos/"+id+"/revisao",Object.fromEntries(form),$("chave").value);await atualizar();aviso("Decisão registrada com justificativa. A análise original permanece no histórico.");});
$("confirmar-frontend").addEventListener("click",e=>durante(e.currentTarget,async()=>{if(!$("chave").value)throw new Error("Preencha a chave local de revisão.");const id=$("revisao-caso").value;const caso=await enviar("/api/atendimentos/"+id+"/zelabairro",{},$("chave").value);await atualizar();$("frontend-resultado").textContent="Registro local confirmado: "+caso.frontend.id+". Não é um protocolo municipal.";aviso("Registro confirmado na persistência do ZelaBairro.");}));
formulario("lote-form",async()=>{if(!$("chave").value)throw new Error("Preencha a chave local de revisão.");const arquivo=$("lote-arquivo").files[0];if(arquivo.size>1024*1024)throw new Error("O CSV deve ter até 1 MB.");const form=new FormData();form.append("arquivo",arquivo);const resultado=await api("/api/lotes",{method:"POST",headers:{"X-Manager-Key":$("chave").value},body:form});$("lote-resultado").textContent=JSON.stringify(resultado.resumo,null,2);$("lote-resultado").hidden=false;await atualizar();aviso("Lote processado. Registros aceitos: "+resultado.atendimentos.length+"; rejeitados pelo RPA: "+resultado.rejeitados.length+".");});
formulario("assistente-form",async()=>{const box=$("assistente-resultado");box.replaceChildren(el("p","Consultando o modelo local. A operação pode levar até um minuto…","fine"));try{const r=await enviar("/api/assistente",{pergunta:$("pergunta").value,atendimento_id:$("evidencia-caso").value||null});box.replaceChildren(el("p",r.resposta,"inset"),el("p","Status: "+r.status+" · "+r.modo,"fine"));if(r.fonte)box.append(link("Consultar a fonte da orientação ↗",r.fonte.url));if($("evidencia-caso").value)box.append(el("p","Saída vinculada ao histórico do pedido.","fine"));}catch(erro){box.replaceChildren(el("p",erro.message,"inset warning"));throw erro;}});
formulario("visao-form",async()=>{const arquivo=$("imagem").files[0];if(arquivo.size>8*1024*1024)throw new Error("A imagem deve ter até 8 MB.");const form=new FormData();form.append("arquivo",arquivo);form.append("atendimento_id",$("evidencia-caso").value);const box=$("visao-resultado");box.replaceChildren(el("p","Executando o modelo de Visão…","fine"));try{const r=await api("/api/visao",{method:"POST",body:form});box.replaceChildren(el("p",r.rotulo||r.classe||r.resultado||"Inferência concluída","inset"),el("p",r.limite,"fine"));const details=el("details");details.append(el("summary","Ver saída e parâmetros"),json(r));box.append(details);}catch(erro){box.replaceChildren(el("p",erro.message,"inset warning"));throw erro;}});
formulario("fontes-form",async()=>{const fontes=await api("/api/fontes?q="+encodeURIComponent($("busca").value));const box=$("fontes-resultado");box.replaceChildren();if(!fontes.length)box.append(el("p","Nenhum trecho localizado. Tente outro termo do assunto.","inset"));fontes.forEach(f=>{const card=el("article",null,"source-card");card.append(badge("LINHA "+f.linha_corpus),el("p",f.text),link(f.fonte||"Consultar fonte ↗",f.url),el("p",(f.paginas?"Páginas: "+f.paginas.join(", "):"Seção: "+f.secao)+" · "+(f.data_coleta||f.data_acesso||"Data registrada no corpus"),"fine"));card.append(botao("Vincular este trecho ao pedido",e=>durante(e.currentTarget,async()=>{const id=$("evidencia-caso").value;if(!id)throw new Error("Selecione um pedido para vincular o trecho.");await enviar("/api/atendimentos/"+id+"/evidencia-pln",{linha_corpus:f.linha_corpus});aviso("Trecho e origem vinculados ao histórico do pedido.");})));box.append(card);});});
async function ativos(){const materiais=await api("/api/ativos");const box=$("ativos");box.replaceChildren();materiais.forEach(m=>{const card=el("article",null,"asset");card.append(badge(m.modo,["cluster","quantica","iot"].includes(m.id)?"orange":""),el("h3",m.nome),el("p",m.resumo));if(m.metricas){const ul=el("ul",null,"mini-metrics");m.metricas.forEach(k=>{const li=el("li");li.append(el("span",k.nome),el("strong",k.valor));ul.append(li);});card.append(ul);}card.append(el("p",m.limite,"limit"));const links=el("div",null,"material-links");m.materiais.forEach((id,i)=>links.append(link("Material "+(i+1)+" ↗","/api/materiais/"+encodeURIComponent(id))));(m.videos||[]).forEach(v=>links.append(link(v.nome+" ↗",v.url)));card.append(links);box.append(card);});state.ativos=true;}
navegar(location.hash.slice(1)||"pedido",false);
