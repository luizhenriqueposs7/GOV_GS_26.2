const classes = {
  som_campainha: {nome: 'Campainha', mensagem: 'Possível campainha', alerta: true},
  batida_porta: {nome: 'Batida na porta', mensagem: 'Possível batida na porta', alerta: true},
  som_ambiente: {nome: 'Som ambiente', mensagem: 'Som ambiente no cenário', alerta: false},
};

export function estadoInicial() {return {conectado: true, eventos: []};}

export function simularSom(estado, classe, data) {
  if (!Object.hasOwn(classes, classe)) throw new Error('Classe fora do trabalho original de IoT.');
  const evento = {classe, data, alerta: classes[classe].alerta, simulacao: true, exibido: estado.conectado};
  return {...estado, eventos: [evento, ...estado.eventos].slice(0, 8)};
}

export function conectar(estado, conectado) {
  return {...estado, conectado, eventos: estado.eventos.map(e => ({...e, exibido: conectado || e.exibido}))};
}

export function iniciarOuviAi() {
  const $ = id => document.getElementById(id);
  let estado = estadoInicial();
  function renderizar() {
    const ultimo = estado.eventos[0], classe = ultimo && classes[ultimo.classe];
    $('ouviai-aparelho').dataset.alerta = String(Boolean(classe?.alerta));
    $('ouviai-display').textContent = classe?.nome || 'Pronto para simular';
    $('ouviai-display-nota').textContent = ultimo ? 'Evento demonstrativo' : 'Nenhum áudio captado';
    $('ouviai-conexao-texto').textContent = estado.conectado ? 'Conexão simulada disponível' : 'Conexão simulada interrompida';
    $('ouviai-status').textContent = classe?.mensagem || 'Escolha um som para explorar o dispositivo.';
    $('ouviai-status-nota').textContent = ultimo
      ? (ultimo.exibido ? 'Evento fictício exibido neste painel. Não houve transmissão de um dispositivo.'
        : 'O aviso local continua no desenho. A exibição na central aguarda reconexão simulada.')
      : 'Os botões representam resultados. Não ativam microfone nem executam o modelo.';
    $('ouviai-conexao').textContent = estado.conectado ? 'Simular perda de conexão' : 'Restabelecer conexão simulada';
    $('ouviai-conexao').setAttribute('aria-pressed', String(!estado.conectado));
    const lista = $('ouviai-eventos'); lista.replaceChildren();
    $('ouviai-vazio').hidden = Boolean(estado.eventos.length);
    for (const evento of estado.eventos) {
      const item = document.createElement('li'), texto = document.createElement('div');
      const nome = document.createElement('strong'); nome.textContent = classes[evento.classe].nome;
      const detalhe = document.createElement('p'); detalhe.textContent = evento.alerta ? 'Aviso visual representado no aparelho' : 'Sem aviso de campainha ou batida neste exemplo';
      const nota = document.createElement('small');
      nota.textContent = 'Simulação · ' + new Date(evento.data).toLocaleTimeString('pt-BR') + ' · ' + (evento.exibido ? 'Exibido no painel demonstrativo' : 'Aguardando reconexão simulada');
      texto.append(nome, detalhe, nota); item.append(texto); lista.append(item);
    }
  }
  document.querySelectorAll('[data-ouviai-som]').forEach(b => b.addEventListener('click', () => {
    estado = simularSom(estado, b.dataset.ouviaiSom, new Date().toISOString()); renderizar();
  }));
  $('ouviai-conexao').addEventListener('click', () => {estado = conectar(estado, !estado.conectado); renderizar();});
  $('ouviai-limpar').addEventListener('click', () => {estado = estadoInicial(); renderizar();});
  const componentes = {
    microfone: 'Microfone: captaria as janelas de áudio para o modelo original. Nesta tela ele está apenas representado; nenhum som é captado.',
    aviso: 'Aviso visual: indicaria uma possível campainha ou batida. A luz e o texto não dependeriam de o usuário ouvir o sinal.',
    conexao: 'Conexão prevista: comunicaria eventos classificados à central. A interface abaixo apenas demonstra essa troca, sem hardware ou servidor de ingestão.',
  };
  document.querySelectorAll('[data-ouviai-parte]').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('[data-ouviai-parte]').forEach(n => n.setAttribute('aria-pressed', String(n === b)));
    $('ouviai-componente').textContent = componentes[b.dataset.ouviaiParte];
  }));
  renderizar();
}
