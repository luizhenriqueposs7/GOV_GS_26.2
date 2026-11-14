# Registro da Central CitizenTech

Plano: ../../docs/superpowers/plans/2026-11-14-central-citizentech.md

Em 14/11/2026, iniciada a implementação em pasta própria. O usuário pediu uma central separada, orientada à utilidade prática, e decidiu não realizar testes com pessoas ou piloto externo. As verificações técnicas permanecem previstas.

Decisão do assistente: executar diretamente neste chat e manter os originais preservados. Usar preparação de pedidos com cartas oficiais como fluxo principal; tratar revisão de acessibilidade como controle dentro desse fluxo. O recorte não será apresentado como validado em campo.

Tarefa 1: concluída. Seis testes passaram após falharem com o recurso ausente. O catálogo pede contexto e localização e distingue os serviços documentados.

Tarefa 2: concluída. Sete testes de registros e indicadores passaram após falha inicial. A revisão preserva a saída original, a contestação reabre a análise e o protocolo externo é apenas informado pelo usuário.

Tarefa 3: em execução. Materiais selecionados copiados com manifesto e hashes. Pipeline do notebook exportado por AST, consulta do corpus e reutilização da persistência do Frontend implementadas. A fonte HTML de PLN usa paginação nula, reconhecida pelo adaptador após regressão reproduzida. Confirmação repetida no Frontend foi corrigida com teste vermelho/verde e serialização local; esta POC assume uma instância da central.

Verificação real de Visão: checkpoint de 160 × 160 executado em CPU no ambiente isolado da central, com a rotina original e uma imagem do acervo. A saída sinalizou ausência de fissura nesse exemplo; isso não estima desempenho geral. Torch e Torchvision foram instalados somente no ambiente desta central.

Tarefa 3: código e empacotamento concluídos. A nova execução de Visão, após validação do contrato, confirmou escore 0,051956 para a imagem 017_1135_2497.jpg, com limiar 0,49. A evidência inclui o hash da imagem. O serviço de GenAI ainda não foi executado por HTTP pela central nesta sessão.

Tarefa 4: API implementada, com criação, atualização, revisão, contestação, protocolo informado, vínculo Frontend, corpus, lote e inferência. Corrigida a codificação do processo filho com `-X utf8`, após erro real com acentos. O percurso pelas funções reais das rotas passou em bancos temporários: registrar, completar, revisar, confirmar sem duplicação, contestar e controlar o caso de rampa. Esse percurso não é transporte HTTP.

Tarefa 5: interface implementada com quatro áreas, identidade CitizenTech, fontes locais, validação nativa, rótulos, foco visível, estados de erro e renderização por textContent. Conferência visual e percurso HTTP ainda pendentes. Não há afirmação de teste com pessoas.

Limitação técnica observada: TestClient bloqueou na criação do socketpair interno do Python Windows. Uma primeira execução com permissão de testes locais chegou aos 35 testes e revelou o erro de codificação. Depois, novas chamadas de exec_command deixaram de retornar até para comandos simples. Foram encerradas as esperas e usados subprocessos limitados via node_repl para os testes sem HTTP, com TEMP/TMP dentro da pasta .tmp da central. Nenhuma rejeição automática de aprovação foi recebida. Não houve tentativa de alterar o controle de acesso da máquina.

Revisão final independente: três achados P2 reproduzidos e corrigidos em uma passagem. (1) Estados arbitrários e resposta vazia de GenAI, além de saída inválida de Visão, agora são recusados. (2) Nova revisão e contestação retiram o vínculo atual com a versão anterior do Frontend, preservando-o no evento. (3) Lote idêntico compara a entrada de origem e conserva os complementos manuais e a decisão. Os quatro novos testes falharam antes da correção. Resultado posterior: 30/30 testes de catálogo, registros e módulos, sem falhas.

Tarefa 6: README, inicializadores, dependências, manifesto integral, roteiro e relatório-base preparados. PDF de trabalho com 14 páginas, nomes dos três integrantes confirmados pelo usuário. A revisão de renderização corrigiu o tamanho do diagrama antes da conferência final. Conclusão conjunta, links publicados, execução HTTP/visual e gravação continuam pendentes; a entrega não foi declarada finalizada.

O usuário informou que não consegue iniciar o servidor agora. A conferência no navegador permanecerá pendente até que o ambiente permita executá-lo. Não foi tratada como aprovação nem como teste concluído.

Conferência do pacote: sintaxe de JavaScript e Python e dos dois inicializadores PowerShell aprovada; 30 materiais principais sem divergência de hash. O índice Git contém 2.610 arquivos, incluindo 2.332 arquivos do acervo de Visão, sem chave, bancos locais, ambientes ou caches. Repositório local separado em codex/central-citizentech; publicação ainda pendente.

Em 14/11/2026, após o usuário pedir a execução, o servidor foi iniciado fora da restrição de sockets, somente em 127.0.0.1:8840. A página inicial abriu no navegador e foi registrada em output/screenshots/central-em-execucao.jpg. A suíte completa passou: 44/44 testes, incluindo os 14 testes HTTP; 5,608 segundos reportados pelo unittest. Isso supera a limitação anterior de execução HTTP, sem constituir validação com pessoas ou navegação integral.

Generative AI confirmado em execução nesta etapa: a central chamou o serviço de 127.0.0.1:8765, com modelo em 127.0.0.1:8080, e retornou status respondido, fonte ILU.1 e historico=false para a pergunta sobre manutenção de iluminação. Evidência em docs/evidencias/execucao-http-genai-2026-11-14.json. A inicialização com Windows PowerShell 5.1 falhou no carregamento de Get-FileHash; reiniciar com o mesmo host PowerShell 7.6.9 verificado preservou o inicializador original e as políticas de segurança. Uma sonda separada encontrou o comando em ambos os hosts, portanto não se afirma incompatibilidade geral do PowerShell 5.1.

Revisão visual pedida pelo usuário: removidos o banner promocional, os números decorativos e a grade de cartões dos módulos. A abertura agora prioriza o formulário, com navegação horizontal e referência de serviços inspirada em sinalização urbana. Os materiais passaram a ter nomes descritivos e organização em lista. Foram preservados os contratos e os bancos existentes. Após as mudanças, 44/44 testes passaram em 5,374 segundos. No navegador, a consulta de Generative AI também respondeu com fonte pela nova interface, sem vincular ou criar atendimento.

Conferência visual da revisão: as quatro áreas abriram no navegador. Capturas em 1280 × 900 e 390 × 844; formulário e acervo não apresentaram rolagem horizontal no celular (375 px úteis e 375 px de conteúdo). A largura foi restaurada ao padrão ao finalizar. A central permaneceu aberta na página de novo pedido. As capturas estão em output/screenshots e o registro em docs/evidencias/interface-2026-11-14.json. O cadastro, a revisão e a contestação completos pelo navegador ainda não foram repetidos nesta revisão visual; os contratos correspondentes passaram nos testes HTTP.

Fluxo completo pelo navegador concluído em 14/11/2026, com o pedido fictício 77bdab73-2852-44c1-9dcb-27832e4eb292. Cadastro, revisão, confirmação no ZelaBairro e contestação passaram. A primeira passagem reproduziu dois problemas: aviso de outra tela persistente e detalhe desatualizado após revisão/confirmação. A navegação agora oculta o aviso anterior; a atualização consulta a versão do detalhe selecionado e o recompõe quando muda. Sem mudança de versão, preserva o rascunho.

As duas falhas foram observadas antes da correção e as verificações passaram depois dela. Na repetição, a prioridade Alta e o novo vínculo apareceram automaticamente no acompanhamento; a contestação retirou a decisão e o vínculo ativos e bloqueou nova confirmação sem revisão. Sete eventos permaneceram no histórico do mesmo pedido. A leitura somente dos bancos confirmou duas linhas do ZelaBairro para duas versões de revisão, sem linhas adicionais nas confirmações repetidas. Nenhum protocolo municipal foi criado. A chave local não foi incluída nas evidências e foi removida do campo ao concluir as ações.

Verificação final: 44/44 testes automáticos, 4,909 segundos; sintaxe JavaScript aprovada. O relatório-base e o PDF de trabalho foram atualizados com as verificações efetivamente feitas. Conclusão conjunta, vídeo e publicações continuam pendentes.

Ampliação móvel autorizada em 14/11, para entrega até 16/11. Formulário com foto opcional normalizada, coordenadas confirmadas, alternativa manual, rascunho explícito no navegador e PWA. Sem geocodificação externa ou detector de buracos. Catálogo ampliado com fonte 952; corredor de ônibus usa remissão 3170, cujos requisitos completos devem ser conferidos no portal.

Revisão independente única identificou quatro problemas de confiabilidade em rascunho, foto e cache; todos corrigidos. Teste com proxy local perdeu a resposta após o commit. Recuperar e reenviar resultou no mesmo pedido 2121d452-3f4b-4372-b198-1ba9879f27ae, com um evento. Com o proxy desligado, o formulário abriu e o rascunho foi recuperado. Outro cadastro deixou o rascunho independente salvo. Sem APIs ou fotos no cache do service worker.

Servidor principal atualizado com backup prévio do banco em data/backups. Caso fictício 697af04a-29dc-4e88-a028-23fd31417308 percorreu cadastro com foto, edição preservando anexo/posição, revisão, confirmação no ZelaBairro 2b4d4bfe-3e01-46c1-a4ca-586e5db84399 e contestação. Cinco eventos, decisão e vínculo atuais retirados, foto e coordenadas preservadas. A confirmação voltou a ficar bloqueada. Chave removida do campo. Instância principal: 127.0.0.1:8840.

Verificação final: 55 testes Python (7,305 s), 7 testes JavaScript, sintaxe aprovada. Inferência atual de Visão repetida depois de reutilizar o normalizador: ResNet18/160, escore 0,0519560948, sem fissura sinalizada. A normalização não alterou essa saída do recorte de teste. Registro em docs/evidencias/mobile-2026-11-14.json. Largura 390 × 844, 375 px úteis e de conteúdo, sem rolagem horizontal. PDF atualizado e páginas 8, 12 e 14 conferidas visualmente; total 14 páginas.

Pendente: comprovação de câmera/GPS e instalação em smartphone por HTTPS protegido, conclusão conjunta, gravação de 5 a 7 minutos e publicação dos links. Não houve acesso externo nem teste com pessoas.
