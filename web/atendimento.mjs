const etapas = {
  protocolo_informado: 'Protocolo anotado · aguardando retorno', em_atendimento: 'Atendimento informado',
  sem_solucao: 'Retorno sem solução', correcao_informada: 'Correção informada · falta conferir',
  correcao_verificada: 'Correção conferida no protótipo', reaberto: 'Acompanhamento reaberto',
};

export function atendimento(caso, {el, link, botao, enviar, api, durante, aviso, atualizar, reduzirFoto, data}) {
  const id = caso.id, url = '/api/atendimentos/' + encodeURIComponent(id);
  const atual = caso.atendimento, servico = caso.preparacao.servico;
  const box = el('section', null, 'service-followup divider');
  box.append(el('p', 'Do pedido à resposta', 'eyebrow'), el('h2', 'Encaminhar e acompanhar'));
  box.append(el('p', 'O ZelaBairro prepara o pedido. O serviço responsável recebe pelo próprio canal, avalia e executa quando cabível. Você traz o protocolo e o retorno para acompanhar aqui.', 'muted'));
  const destino = el('div', null, 'inset');
  destino.append(el('h3', servico?.nome || 'Confirmar o serviço com o atendimento oficial'),
    el('p', 'Quem recebe: ' + (servico?.responsavel || 'A definir pelo atendimento oficial')),
    el('p', 'Canal: ' + (servico?.canal || 'Telefone 156, para orientação em São Paulo')),
    el('p', servico?.orientacao || caso.preparacao.pergunta, 'fine'));
  if (servico) destino.append(link('Abrir a orientação e o canal oficial', servico.url));
  destino.append(el('p', 'Catálogo de São Paulo. Fora do município, confirme o órgão e o canal locais. Nenhum envio automático é realizado.', 'fine'));
  box.append(destino);
  if (!caso.revisao || !caso.frontend) box.append(el('p', 'Conferência local pendente: revise e confirme o registro na aba Revisão antes de usar a ficha.', 'inset warning'));
  const acoes = el('div', null, 'actions'), baixar = link('Baixar ficha do pedido', url + '/ficha');
  baixar.download = 'zelabairro-' + id.slice(0, 8) + '.txt';
  acoes.append(botao('Copiar ficha para encaminhar', e => durante(e.currentTarget, async () => {
    const resposta = await fetch(url + '/ficha');
    if (!resposta.ok) throw new Error('Não foi possível preparar a ficha. Tente baixar novamente.');
    await navigator.clipboard.writeText(await resposta.text());
    aviso('Ficha copiada. Confira os dados e anexe a foto no canal responsável.');
  })), baixar);
  if (caso.foto) {const foto = link('Baixar foto inicial', url + '/foto'); foto.download = 'ocorrencia.jpg'; acoes.append(foto);}
  box.append(acoes);
  const passo = el('ol', null, 'handoff-steps');
  ['Conferir o serviço e concluir o envio no canal responsável.', 'Anotar o protocolo recebido ou iniciar uma demonstração.',
    'Registrar o retorno e, se houver correção, anexar uma foto posterior.', 'Conferir a correção ou solicitar nova análise.'].forEach(t => passo.append(el('li', t)));
  box.append(passo);
  if (atual) box.append(el('p', (atual.demonstracao ? 'DEMONSTRAÇÃO · ' : 'INFORMAÇÃO DO USUÁRIO · ') + etapas[atual.etapa], 'inset warning'),
    el('p', 'Protocolo: ' + atual.protocolo.numero + '. Sem confirmação ou sincronização com o órgão.', 'fine'));
  else if (caso.protocolo_oficial) box.append(el('p', 'Protocolo declarado: ' + caso.protocolo_oficial.numero + '. Salve o número abaixo para iniciar o acompanhamento.', 'fine'));

  function campo(form, titulo, node, sufixo) {
    node.id = 'atendimento-' + sufixo;
    const label = el('label', titulo); label.htmlFor = node.id; form.append(label, node); return node;
  }
  if (!atual || atual.etapa !== 'correcao_verificada') {
    const form = el('form', null, 'spaced'), modo = el('select');
    for (const [valor, texto] of [['demo', 'Demonstração · sem envio a um órgão'], ['declarado', 'Já recebi um protocolo pelo canal oficial']]) {
      const o = el('option', texto); o.value = valor; modo.append(o);
    }
    if (caso.protocolo_oficial) modo.value = 'declarado';
    if (atual) {modo.value = atual.demonstracao ? 'demo' : 'declarado'; modo.disabled = true;}
    campo(form, 'Como deseja acompanhar?', modo, 'modo');
    const numero = campo(form, 'Número do protocolo', el('input'), 'numero'); numero.required = true; numero.maxLength = 80;
    numero.value = atual?.protocolo.numero || caso.protocolo_oficial?.numero || 'SIM-' + id.slice(0, 8).toUpperCase();
    modo.addEventListener('change', () => {numero.value = modo.value === 'demo' ? 'SIM-' + id.slice(0, 8).toUpperCase() : '';});
    const salvar = el('button', atual ? 'Corrigir número do protocolo' : 'Iniciar acompanhamento', 'primary'); salvar.type = 'submit'; form.append(salvar);
    form.addEventListener('submit', e => {e.preventDefault(); durante(salvar, async () => {
      await enviar(url + '/protocolo', {protocolo: numero.value, demonstracao: modo.value === 'demo'});
      await atualizar(); aviso('Acompanhamento local iniciado. Nenhum pedido foi enviado ao órgão pela central.');
    });}); box.append(form);
  }
  if (atual && atual.etapa !== 'correcao_verificada') {
    const form = el('form', null, 'spaced'), situacao = el('select');
    [['em_atendimento', 'Atendimento em andamento, conforme retorno recebido'], ['sem_solucao', 'Resposta recebida, mas problema permanece'],
      ['correcao_informada', 'Correção informada · anexar foto posterior']].forEach(([v, t]) => {const o = el('option', t); o.value = v; situacao.append(o);});
    campo(form, 'Registrar um retorno', situacao, 'situacao');
    const relato = campo(form, 'O que foi informado ou observado?', el('textarea'), 'retorno'); relato.required = true; relato.minLength = 10; relato.maxLength = 1000; relato.rows = 3;
    const foto = campo(form, 'Foto posterior, obrigatória para informar correção', el('input'), 'foto');
    foto.type = 'file'; foto.accept = 'image/jpeg,image/png'; foto.setAttribute('capture', 'environment'); foto.disabled = true;
    situacao.addEventListener('change', () => {foto.disabled = situacao.value !== 'correcao_informada'; foto.required = !foto.disabled; if (foto.disabled) foto.value = '';});
    const salvar = el('button', 'Salvar retorno', 'secondary'); salvar.type = 'submit'; form.append(salvar);
    form.addEventListener('submit', e => {e.preventDefault(); durante(salvar, async () => {
      const dados = new FormData(); dados.append('etapa', situacao.value); dados.append('relato', relato.value);
      if (foto.files[0] && !foto.disabled) dados.append('arquivo', await reduzirFoto(foto.files[0]), 'depois.jpg');
      await api(url + '/retorno', {method: 'POST', body: dados}); await atualizar();
      aviso('Retorno anotado como informação do usuário. Uma correção ainda exige conferência humana.');
    });}); box.append(form);
  }
  if (atual?.retorno) {
    box.append(el('h3', 'Último retorno'), el('p', atual.retorno.relato), el('p', data(atual.retorno.data) + ' · ' + atual.retorno.origem, 'fine'));
    if (atual.retorno.foto) {const img = el('img', null, 'followup-photo'); img.src = url + '/foto-correcao?v=' + atual.retorno.foto.sha256; img.alt = 'Foto posterior enviada para conferência da correção'; box.append(img);}
  }
  if (atual?.etapa === 'correcao_informada') {
    const form = el('form', null, 'spaced'); form.append(el('h3', 'Conferência da correção pelo responsável'), el('p', 'Confira foto, local e passagem. Uma foto com outro hash não prova data, lugar ou execução do reparo. A conferência é do protótipo e não substitui uma vistoria técnica.', 'fine'));
    const revisor = campo(form, 'Responsável pela conferência', el('input'), 'revisor'); revisor.required = true; revisor.minLength = 2; revisor.maxLength = 80;
    const motivo = campo(form, 'O que permite considerar o problema corrigido?', el('textarea'), 'justificativa'); motivo.required = true; motivo.minLength = 10; motivo.maxLength = 500;
    const chave = campo(form, 'Chave de gestão', el('input'), 'chave'); chave.type = 'password'; chave.required = true; chave.autocomplete = 'off';
    const label = el('label', null, 'check'), check = el('input'); check.type = 'checkbox'; check.required = true;
    label.append(check, el('span', 'Conferi a evidência e o contexto. Entendo o alcance desta conferência.')); form.append(label);
    const salvar = el('button', 'Confirmar correção no protótipo', 'primary'); salvar.type = 'submit'; form.append(salvar);
    form.addEventListener('submit', e => {e.preventDefault(); durante(salvar, async () => {
      await enviar(url + '/verificar-correcao', {base: caso.atualizado_em, revisor: revisor.value, justificativa: motivo.value, confirmado: check.checked}, chave.value);
      await atualizar(); aviso('Correção conferida no protótipo. O percurso considera somente a barreira deste pedido.');
    });}); box.append(form);
  }
  if (atual?.conferencia) box.append(el('p', atual.conferencia.revisor + ' · ' + atual.conferencia.justificativa, 'inset'), el('p', atual.conferencia.alcance, 'fine'));
  if (atual && ['sem_solucao', 'correcao_verificada'].includes(atual.etapa)) box.append(el('p', 'Se o problema persistir, solicite nova análise abaixo. Isso reabre apenas o acompanhamento local.', 'fine'),
    link('Consultar reclamação à Ouvidoria com o protocolo anterior', 'https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2630'));
  return box;
}
