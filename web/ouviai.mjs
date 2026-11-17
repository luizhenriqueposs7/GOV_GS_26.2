import {criarEscuta} from './ouviai-audio.mjs';

const classes = {
  som_campainha: {nome: 'Campainha', mensagem: 'Possível campainha', alerta: true},
  batida_porta: {nome: 'Batida na porta', mensagem: 'Possível batida na porta', alerta: true},
  som_ambiente: {nome: 'Som ambiente', mensagem: 'Som ambiente no cenário', alerta: false},
  inconclusivo: {nome: 'Sem identificação', mensagem: 'Som não identificado com segurança', alerta: false},
  outro_som: {nome: 'Outro som', mensagem: 'Sem indicação de campainha ou batida', alerta: false},
};

export function interpretarAudio(categorias) {
  const validas = (Array.isArray(categorias) ? categorias : []).filter(c =>
    typeof c.categoryName === 'string' && Number.isFinite(c.score) && c.score >= 0 && c.score <= 1
  ).sort((a,b) => b.score - a.score);
  const alvos = {Doorbell:'som_campainha', 'Ding-dong':'som_campainha', Knock:'batida_porta'};
  const avisos = validas.filter(c=>Object.hasOwn(alvos,c.categoryName));
  const primeiro = avisos.find(c=>c.score>=0.6) || validas[0];
  if (!primeiro) return {classe:'inconclusivo', alerta:false, pontuacao:null, rotulo:null};
  // shortcut: limiar inicial experimental; calibrar com sons e aparelhos do ambiente de uso.
  // YAMNet é multirrótulo: Door e Knock podem coexistir; comparar somente tipos de aviso distintos.
  const disputa = avisos.some(c=>alvos[c.categoryName]!==alvos[primeiro.categoryName] && primeiro.score-c.score<0.15);
  const claro = primeiro.score >= 0.6 && !disputa;
  const classe = claro ? (alvos[primeiro.categoryName] || (primeiro.categoryName==='Silence'?'som_ambiente':'outro_som')) : 'inconclusivo';
  return {classe, alerta:classes[classe].alerta, pontuacao:primeiro.score, rotulo:primeiro.categoryName};
}

export function estadoInicial() {return {conectado: true, eventos: []};}

export function simularSom(estado, classe, data) {
  if (!['som_campainha','batida_porta','som_ambiente'].includes(classe)) throw new Error('Classe fora do trabalho original de IoT.');
  const evento = {classe, data, alerta: classes[classe].alerta, simulacao: true, exibido: estado.conectado};
  return {...estado, eventos: [evento, ...estado.eventos].slice(0, 8)};
}

export function conectar(estado, conectado) {
  return {...estado, conectado, eventos: estado.eventos.map(e => ({...e, exibido: conectado || e.exibido}))};
}

export function iniciarOuviAi() {
  const $ = id => document.getElementById(id);
  let estado = estadoInicial(), exibido = null, ultimoAviso = 0;
  const escuta = criarEscuta(categorias=>{
    const resultado = interpretarAudio(categorias), agora = Date.now();
    if (exibido?.alerta && !exibido.simulacao && !resultado.alerta && agora-ultimoAviso<4000) return;
    if (exibido && !exibido.simulacao && exibido.classe === resultado.classe && (!resultado.alerta || agora-ultimoAviso<7000)) return;
    exibido = {...resultado, data:new Date().toISOString(), simulacao:false, exibido:true};
    if (resultado.alerta) ultimoAviso=agora;
    estado = {...estado, eventos:[exibido,...estado.eventos].slice(0,8)};
    renderizar();
  },(ativo,mensagem)=>{
    $('ouviai-iniciar').disabled=ativo;
    $('ouviai-parar').disabled=!ativo;
    $('ouviai-microfone-status').textContent=mensagem;
    $('ouviai-microfone-status').dataset.ativo=String(ativo);
    if(ativo && mensagem.startsWith('Escutando'))$('ouviai-status').scrollIntoView({block:'center'});
    if(!ativo && exibido && !exibido.simulacao)$('ouviai-display-nota').textContent='Escuta encerrada';
  });
  function renderizar() {
    const ultimo = exibido, classe = ultimo && classes[ultimo.classe];
    $('ouviai-aparelho').dataset.alerta = String(Boolean(classe?.alerta));
    $('ouviai-display').textContent = classe?.nome || 'Microfone desligado';
    $('ouviai-display-nota').textContent = ultimo ? (ultimo.simulacao?'Evento simulado':'Áudio deste aparelho') : 'Ative para reconhecer';
    $('ouviai-conexao-texto').textContent = estado.conectado ? 'Conexão simulada disponível' : 'Conexão simulada interrompida';
    $('ouviai-origem').textContent=ultimo?.simulacao?'Simulação manual': 'Classificação local · YAMNet';
    $('ouviai-status').textContent = classe?.mensagem || 'Ative o microfone para começar.';
    $('ouviai-status-nota').textContent = ultimo
      ? (ultimo.simulacao ? (ultimo.exibido ? 'Evento fictício. Nenhum som foi reconhecido.' : 'Evento fictício aguardando reconexão simulada.')
        : (ultimo.rotulo ? 'Saída do modelo: '+ultimo.rotulo+' · pontuação '+Math.round(ultimo.pontuacao*100)+'%. Pontuação não é acurácia.' : 'O modelo não retornou uma identificação.'))
      : 'O resultado aparecerá aqui depois de captar e processar o som.';
    $('ouviai-conexao').textContent = estado.conectado ? 'Simular perda de conexão' : 'Restabelecer conexão simulada';
    $('ouviai-conexao').setAttribute('aria-pressed', String(!estado.conectado));
    const lista = $('ouviai-eventos'); lista.replaceChildren();
    $('ouviai-vazio').hidden = Boolean(estado.eventos.length);
    for (const evento of estado.eventos) {
      const item = document.createElement('li'), texto = document.createElement('div');
      const nome = document.createElement('strong'); nome.textContent = classes[evento.classe].nome;
      const detalhe = document.createElement('p'); detalhe.textContent = evento.alerta ? 'Possível evento: confira no local' : 'Sem aviso de campainha ou batida';
      const nota = document.createElement('small');
      nota.textContent = (evento.simulacao?'Simulação manual':'Microfone · YAMNet')+' · '+new Date(evento.data).toLocaleTimeString('pt-BR')+
        (evento.simulacao ? (evento.exibido?' · Exibido':' · Aguardando reconexão simulada') : ' · '+evento.rotulo+' · '+Math.round(evento.pontuacao*100)+'%');
      texto.append(nome, detalhe, nota); item.append(texto); lista.append(item);
    }
  }
  $('ouviai-iniciar').addEventListener('click',()=>{exibido=null;renderizar();void escuta.iniciar();});
  $('ouviai-parar').addEventListener('click',()=>escuta.parar());
  window.addEventListener('pagehide',()=>escuta.parar());
  document.addEventListener('visibilitychange',()=>{if(document.hidden)escuta.parar('Escuta encerrada porque a página ficou em segundo plano.');});
  document.querySelectorAll('[data-ouviai-som]').forEach(b => b.addEventListener('click', () => {
    escuta.parar();estado = simularSom(estado, b.dataset.ouviaiSom, new Date().toISOString()); exibido=estado.eventos[0];renderizar();
  }));
  $('ouviai-conexao').addEventListener('click', () => {estado = conectar(estado, !estado.conectado);if(exibido?.simulacao)exibido=estado.eventos.find(e=>e.data===exibido.data);renderizar();});
  $('ouviai-limpar').addEventListener('click', () => {escuta.parar();estado = estadoInicial();exibido=null;ultimoAviso=0;renderizar();});
  const componentes = {
    microfone: 'O teste usa o microfone deste celular ou computador, depois da sua autorização. O microfone da estação desenhada é ilustrativo.',
    aviso: 'A luz e o texto desta tela mostram o resultado local. Não existe lâmpada física conectada. Não dependa deste protótipo para emergências.',
    conexao: 'O áudio é processado neste aparelho. Não há transmissão entre dispositivos nem estação fixa instalada; o diário fica somente nesta aba.',
  };
  document.querySelectorAll('[data-ouviai-parte]').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('[data-ouviai-parte]').forEach(n => n.setAttribute('aria-pressed', String(n === b)));
    $('ouviai-componente').textContent = componentes[b.dataset.ouviaiParte];
  }));
  renderizar();
  return escuta;
}
