# Teste no celular

## Acesso online atual

Abra **https://gov262.vercel.app/#pedido** no Chrome do Android ou Safari do iPhone. Não é necessário deixar o computador ligado. A entrada é direta, sem usuário e senha. Somente as ações de gestão exigem a chave de revisão, disponível no arquivo privado local `data/acesso-zelabairro-online.txt`, fora do Git. Pedidos e fotos da demonstração ficam visíveis a quem acessar o link. Se a versão anterior estiver aberta ou instalada, feche todas as abas da central e abra novamente para atualizar o formulário.

1. Em **Registrar**, fotografe pelo botão da câmera e depois **Capturar foto**, ou use **Câmera do aparelho**. Escolher uma imagem também inicia a preparação automática.
2. Permita a localização. A foto vai ao Groq para preparar uma descrição; a posição atual vai diretamente do aparelho à BigDataCloud para sugerir uma região. O mapa usa OpenStreetMap. Não há endereço inventado pela imagem ou localização por IP.
3. Aguarde a tela **Conferir e enviar**. Confira a foto, ajuste o relato, o bairro/região e o ponto no mapa. A região é aproximada, sem rua ou número; complete uma referência quando necessário. Se GPS/IA falharem, a tela explica a falha e permite preencher manualmente. Imagem inconclusiva exige descrição da pessoa.
4. O tipo de local e vínculo ao Passagem Livre são opcionais para registrar. Expanda **Conferir tipo de local** quando souber o contexto. Não associe uma foto real de outro lugar ao percurso didático.
5. Marque a única confirmação de texto, foto e local e toque em **Enviar pedido**. Antes desse botão, nenhum pedido foi registrado. Anote o identificador e confira o mesmo registro em **Meus pedidos**.
6. Em **Revisão**, selecione o pedido, informe revisor, prioridade, justificativa e chave. Toque em **Registrar decisão** e depois **Confirmar registro local**. Pendências de contexto/localização podem impedir a confirmação; corrija o pedido e revise novamente. Não é um protocolo municipal.
7. Em **Abrir pedido e contestação**, veja **Encaminhar e acompanhar**: responsável, canal, ficha copiável/baixável e foto inicial. O catálogo trata São Paulo; confirme o canal local se estiver em outro município. Não envie um caso fictício ao órgão.
8. Para o vídeo, selecione **Demonstração · sem envio a um órgão**, mantenha o número SIM e toque em **Iniciar acompanhamento**. Um protocolo real só deve ser anotado após recebê-lo pelo canal oficial; permanece declarado, sem sincronização.
9. Em **Registrar um retorno**, selecione atendimento em andamento, retorno sem solução ou correção informada. Esta última exige uma foto posterior. Use um cenário identificado para demonstrar; não apresente duas fotos de lugares diferentes como prova de reparo.
10. Para **Confirmar correção no protótipo**, o responsável confere foto e contexto, informa justificativa e chave de gestão. Se o pedido mudar durante a conferência, atualize e confira novamente. Isso não é vistoria municipal. O Passagem Livre desconsidera só a barreira do pedido conferido, mantendo condições desconhecidas.
11. Explique o motivo em **Pedir uma nova análise** e toque em **Solicitar nova revisão**. O acompanhamento reabre, a barreira volta ao cenário e a decisão anterior fica no histórico. A contestação é local; reclamações ao órgão seguem o canal de Ouvidoria indicado.

Em **Como o relato foi preparado**, confira modelo, data, sugestão original e alterações humanas. O rascunho guarda a sugestão e os campos, mas pede nova confirmação após recuperar. Campos preenchidos automaticamente acompanham o novo GPS; correções manuais são preservadas.

Chrome e WebKit verificaram o fluxo com controles sintéticos claramente identificados, incluindo recuperação de rascunho com foto e abertura sem rede. Foram conferidas 32 combinações de tela e largura, de 320 a 844 px. Refazer o GPS, recuperar um rascunho ou trocar o método do planejamento exige confirmar novamente. [Resultados e limites da auditoria móvel](evidencias/qa-mobile-2026-11-17.md).

Câmera e GPS físicos ainda devem ser testados pelo integrante. Registre aparelho, navegador, resultado, precisão GPS e identificador do pedido, sem divulgar senha/chave. A análise é preliminar e não comprova gravidade ou acessibilidade.

## Lotes e planejamento da revisão

Em Revisão, informe a chave de gestão e use Processar lote do RPA. Selecione o CSV de demonstração em docs/exemplos/cluster-revisoes.csv e execute com 2 ou 4 workers. Confira aceitos, rejeitados, IDs e tempos de coordenação/RPA, gravação e total. Os tempos iSPD pertencem ao estudo original, sem comparação direta com a latência desta execução.

Abra Planejar as próximas revisões ou https://gov262.vercel.app/#planejamento. Escolha até oito pendentes, defina conscientemente a prioridade, estime minutos e marque os obrigatórios. Informe capacidade e chave; compare os métodos. Escolha um, confira selecionados/adiados e registre responsável/justificativa. O plano fica no histórico, sem aprovar os pedidos. Os botões da seleção abrem a revisão existente. Alterar ou contestar um caso exige nova comparação. O QAOA é executado em simulador CPU, sem hardware ou vantagem quântica demonstrada.

## Estação OuviAí proposta

Abra https://gov262.vercel.app/#ouviai, também disponível em Materiais e fontes e no Passagem Livre. Explore os componentes e use Simular campainha, Simular batida na porta e Simular som ambiente. Interrompa a conexão simulada, gere um evento e restabeleça a conexão para observar sua exibição no painel demonstrativo. Limpar demonstração apaga os eventos da aba. Nenhum controle usa microfone, executa o modelo ou cria ocorrências. O desenho e os eventos representam uma proposta de dispositivo, sem hardware conectado.

## Histórico da execução local por túnel

As instruções abaixo documentam o modo local anterior. Para a publicação atual, use o acesso online acima.

## Passagem Livre na gravação

Depois de autenticar o telefone, abra “Passagem Livre”. O percurso ponto → unidade de saúde é didático e esquemático. O computador pode preparar os dois pedidos fictícios antes da tomada, usando a chave de gestão. Marcar só a calçada conserva a barreira da rampa; marcar ambos mostra continuidade na hipótese do cenário. O resultado não comprova passagem física ou reparo executado.

Use “Registrar observação neste trecho” para vincular uma observação didática. Na segunda etapa, confira o trecho e informe a condição da passagem; a terceira etapa mostra o vínculo junto da foto e do ponto confirmado. A associação é declarada, sem ajuste automático da posição ao traçado. Se a foto/GPS reais forem de outro local, faça o pedido sem vínculo ao percurso ilustrativo. Escolher “Não consigo avaliar” conserva a incerteza na simulação.

Salvar e recuperar o rascunho mantém o vínculo, a foto e as coordenadas, mas pede nova confirmação. Para mostrar a Governança, revise os pedidos, registre o plano e depois conteste um pedido. O plano anterior passa a desatualizado; o histórico permanece. A revisão da rampa pode coexistir com pendência de enquadramento municipal, que impede confirmar aquele pedido no ZelaBairro. A gravação deve explicar essa abstenção.

O acesso temporário usa Cloudflare Quick Tunnel com `--allowed-mail`. Apenas o e-mail explicitamente autorizado pode entrar com o código recebido. O túnel aponta para a central local em 127.0.0.1:8840 e não exige abrir portas no roteador. Fotos, relatos e GPS atravessam a Cloudflare até o computador; a área do mapa também é recebida pelo OpenStreetMap. As permissões de câmera e localização são concedidas pela pessoa no telefone.

## Preparação

O executável oficial cloudflared 2026.11.0 foi baixado em `data/runtime/cloudflared.exe`, fora do Git. O SHA-256 foi conferido com a publicação da Cloudflare no GitHub: `d5c1d82031da6253dcdcff64c944cd0fe063016edeb2e4fd088075fc9bd52d0a`. O inicializador confere esse hash novamente e não inicia sem a opção de proteção por e-mail.

- [Publicação oficial e hash](https://github.com/cloudflare/cloudflared/releases/tag/2026.11.0)
- [Proteção por e-mail](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/#restrict-access-by-email)

Com a central aberta, execute em PowerShell: `./INICIAR-CELULAR.ps1 -Email SEU_EMAIL -Minutos 60`. O e-mail real fica apenas no processo local e na configuração temporária do provedor, sem ser versionado. O endereço e o horário limite ficam em `data/runtime/celular-acesso.json`. O link muda a cada inicialização. Ao terminar o tempo, o processo encerra o túnel. Para encerrar antes, use `./ENCERRAR-CELULAR.ps1`; a central local continua aberta.

Para preparar tudo em um comando, use `./PREPARAR.ps1 -Celular -Email SEU_EMAIL -Minutos 60`. Ele inicia ou reutiliza a central e a IA, confere as sete integrações técnicas e só depois abre o acesso protegido. Sem `-Celular`, a preparação é apenas local. A leitura de câmera e GPS pode ser cancelada: uma resposta atrasada não deve substituir o ponto escolhido manualmente. A confirmação final declara o teste, sem exigir que uma foto ou coordenada reais sejam chamadas de fictícias.

O computador precisa permanecer ligado, conectado e sem suspensão durante o teste. A disponibilidade do serviço temporário depende da Cloudflare. O acesso não é uma publicação de produção.

## Percurso

O teste físico e a gravação foram planejados pelo integrante para 15/11/2026. O link temporário de 14/11 não será reutilizado: iniciar a central e gerar outro link protegido no momento do teste. O e-mail já autorizado pode ser mantido. Isso não significa que o teste físico tenha passado antecipadamente.

Para a gravação, escolha uma situação urbana simples que possa fotografar sem risco, como um trecho de calçada. Capture a foto pelo aplicativo, confira o GPS e envie o pedido na hora. Continue o mesmo identificador no computador: verifique o anexo e o ponto, registre a revisão e a justificativa, confirme no ZelaBairro e faça a contestação. O histórico deve conservar cada etapa. Grave a operação completa; selecione depois o trecho que cabe no vídeo final de 5 a 7 minutos, que também precisa apresentar as outras disciplinas.

1. Abra o link HTTPS no Safari do iPhone ou Chrome do Android. Informe o e-mail autorizado e o código enviado à caixa de entrada. Não use o navegador interno de um mensageiro.
2. Entre em Registrar. Toque no botão da câmera e permita o acesso. Fotografe um objeto ou superfície de demonstração, sem pessoas, placas ou documentos. Se a câmera ao vivo não abrir, use Câmera do aparelho ou Escolher imagem.
3. Escreva um relato claramente identificado como teste. Avance para localização e toque em Usar posição do aparelho. Permita a localização; confira o ponto, a precisão informada e a referência. O GPS não preenche endereço ou bairro automaticamente.
4. Para não guardar a posição real no pedido, após conferir o GPS use Limpar coordenadas e escolha um ponto de demonstração. Se mantiver a posição real, ela ficará no banco e no histórico locais, fora do Git.
5. Confirme o ponto, avance, confira a foto e o relato e registre o pedido de demonstração. Anote o identificador recebido. Ele aparecerá na mesma central aberta no computador.
6. Abra Meus pedidos para conferir a foto e o histórico. Revisão e confirmação no ZelaBairro continuam exigindo a chave local do responsável. O registro não abre chamado municipal.

O que a demonstração pode provar: captura/anexo, localização do aparelho, confirmação do ponto, persistência e revisão do pedido. A foto de uma calçada não comprova detecção automática de buraco; o GPS não comprova o endereço. Se alguma etapa falhar, registre a condição e o resultado observado, sem substituir silenciosamente por uma execução anterior.

Registre separadamente o aparelho, navegador, permissões concedidas, resultado da câmera, precisão do GPS e identificador do pedido. A preparação do link não comprova funcionamento físico: esse resultado depende do teste feito pela pessoa no celular. Não envie códigos de acesso, chave de gestão ou foto pessoal para o GitHub.

## Conferência da preparação em 14/11/2026

Sintaxe dos dois scripts aprovada e quatro configurações inválidas rejeitadas antes de iniciar o túnel: wildcard de domínio, múltiplos e-mails, tentativa de argumentos extras e duração fora do limite. A conexão HTTP/2 com a Cloudflare foi estabelecida. No navegador sem autenticação, o endereço abriu a tela de login da Cloudflare Access; nenhum código foi solicitado pelo assistente.

Requisições sem cookie à página inicial, à lista de pedidos e à foto de um pedido fictício retornaram 302 para a autenticação, sem liberar o conteúdo. Evidência sem e-mail, cookies ou códigos em [verificação do acesso](evidencias/acesso-celular-2026-11-14.json). O endereço temporário e seus parâmetros de autenticação não são versionados.
