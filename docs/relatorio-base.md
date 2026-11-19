# CENTRAL CITIZENTECH

Planejamento de acesso, pedidos e revisão

Governança em IA e Business Analytics · Global Solution 2026

Luiz Henrique Poss · RM562177

Luis Filipe Chaves Amorim · RM564706

Felipe Stefani Honorato · RM563380

São Paulo · 2026

<!-- pagina -->
# FOLHA DE ROSTO

Luiz Henrique Poss · RM562177

Luis Filipe Chaves Amorim · RM564706

Felipe Stefani Honorato · RM563380

## CENTRAL CITIZENTECH

Planejamento de acesso, pedidos e revisão

Relatório de integração dos trabalhos da Global Solution, apresentado à disciplina de Governança em IA e Business Analytics da FIAP. O documento reúne os materiais das disciplinas, descreve a participação de cada módulo e registra os limites da aplicação construída.

A demonstração combina cenários fictícios com um cadastro feito a partir de foto e posição reais. O grupo fez testes técnicos, sem testar o sistema com moradores nem conferir o percurso em campo.

São Paulo · 2026

<!-- pagina -->
# LISTA DE FIGURAS

Figura 1 - Fluxo de preparação, revisão e registro local ................................ 5

Figura 2 - Recorte usado na execução técnica de Visão Computacional .......... 10

<!-- pagina -->
# LISTA DE QUADROS

Quadro 1 - Participação dos materiais na central ........................................ 11

## LISTA DE TABELAS

Tabela 1 - Tempos dos cenários simulados no iSPD ..................................... 6

Tabela 2 - Resultados históricos do modelo de Visão ................................ 10

<!-- pagina -->
# SUMÁRIO

1 INTRODUÇÃO ........................................................................................ 5

2 DESENVOLVIMENTO ............................................................................. 6

2.1 RPA ...................................................................................................... 6

2.2 Cluster Computing ................................................................................. 6

2.3 Computação Quântica ............................................................................ 7

2.4 Frontend ................................................................................................ 7

2.5 Generative AI ........................................................................................ 8

2.6 IoT ........................................................................................................ 9

2.7 Processamento de Linguagem Natural .................................................... 9

2.8 Visão Computacional ........................................................................... 10

2.9 Governança em IA e Business Analytics ............................................... 11

3 CONCLUSÃO ........................................................................................ 12

4 LINKS .................................................................................................... 12

REFERÊNCIAS ......................................................................................... 13

<!-- pagina -->
# 1 INTRODUÇÃO

Registrar um problema do bairro exige identificar o serviço e reunir informações sobre o local. Uma calçada danificada em uma praça, um objeto bloqueando a passagem e a falta de uma rampa não têm necessariamente o mesmo encaminhamento. As cartas de serviços da Prefeitura de São Paulo delimitam essas diferenças (SÃO PAULO, 2026a; 2026b).

O SP156 já oferece registro de solicitações e consulta de protocolos. A Central CitizenTech foi construída como um protótipo de preparação e revisão: organiza o relato, solicita contexto, apresenta a fonte da orientação e mantém a justificativa das decisões. A aplicação não substitui o canal municipal nem executa reparos.

O protótipo foi pensado para moradores que precisam preparar pedidos e para quem faz a triagem. Os testes do grupo usaram a própria central. Sem uma equipe municipal parceira, não foi possível medir mudanças no prazo ou nos erros de atendimento.

Figura 1 - Fluxo de preparação, revisão e registro local

[[figura-fluxo]]

Fonte: elaboração do grupo, a partir da aplicação construída em 2026.

RPA, Frontend, PLN e Visão reutilizam código dos trabalhos originais. A versão online usa uma adaptação de Generative AI. Cluster processa os lotes, e o simulador de Quântica ajuda a escolher os pedidos da rodada de revisão. No IoT, a central usa outro modelo para reconhecer sons no navegador.

<!-- pagina -->
# 2 DESENVOLVIMENTO

## 2.1 RPA

O notebook original recebe arquivos CSV, valida os campos case_id, description e neighborhood e classifica as solicitações por regras. As funções foram exportadas sem executar as células de demonstração. A central utiliza essas funções para a triagem de novos relatos e para o processamento de lotes. Os identificadores do CSV são preservados como texto.

O caso “Calçada sem rampa acessível” retorna categoria Acessibilidade, prioridade Baixa, confiança heurística 1,0 e revisão dispensada. Essa saída foi mantida. O controle da central exige revisão para a categoria Acessibilidade e registra a decisão posterior separadamente. A confiança da regra não é uma probabilidade calibrada de acerto.

A reaplicação de um lote com os mesmos dados de origem conserva os complementos manuais e a revisão. Se a descrição ou o bairro de origem mudarem, a revisão é invalidada. A versão anterior permanece no histórico. O CSV não pode fornecer análises prontas para substituir a execução do RPA.

## 2.2 Cluster Computing

A central adapta o Round Robin e os 2/4 workers do estudo iSPD para processar CSV pelo RPA original. IDs repetidos ficam juntos. Os resultados são validados e gravados em uma transação; falhas impedem gravação parcial.

Tabela 1 - Tempos dos cenários simulados no iSPD

| Cenário | Workers | Tempo simulado |
| --- | --- | --- |
| Primeiro modelo | 2 | 1,20230 s |
| Segundo modelo | 4 | 0,604501 s |

Fonte: relatório e modelos de Cluster Computing entregues pelo grupo.

A redução de 49,72% foi medida na simulação do iSPD. A central mede cada lote separadamente. Em execução local, os workers são threads. Na Vercel, cada worker é acionado por HTTP e pode rodar na mesma máquina. O modo com workers aceita até 50 registros por lote.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.3 Computação Quântica

O estudo de alocação foi ampliado com um piloto de seleção de até oito revisões. O gestor informa prioridades, durações estimadas e capacidade. Obrigatórios sem capacidade geram aviso; casos adiados ficam explícitos.

O QAOA p=1 é calculado em vetor de estado NumPy: fase de custo e rotações Rx, com busca clássica de parâmetros. Compara-se o estado factível mais provável com fila e enumeração exata. Não há QPU ou ganho quântico demonstrado.

O plano justificado fica no histórico e abre os pedidos para revisão humana. Mudanças exigem recalcular. É um recorte do estudo: não modela turnos, competências, prazos ou equidade, nem altera prioridades automaticamente.

## 2.4 Frontend

A central reutiliza a validação e a persistência do ZelaBairro. Localmente, os bancos ficam separados. Na adaptação online, Postgres mantém relatos e histórico na mesma transação, com fotos privadas no Supabase.

A partir da foto, a central sugere um relato, possíveis impactos e um pedido de vistoria. A imagem não permite medir dimensões. A posição ajuda a sugerir a região pela BigDataCloud. A pessoa confere o texto e o ponto no mapa antes de enviar. O rascunho conserva os dados, e a central remove os metadados da foto.

A confirmação exige revisão justificada e dados completos. Repetir a confirmação da mesma revisão mantém o registro. Alterar o pedido ou contestar retira a decisão e o vínculo atuais, preservando o histórico. O identificador é da central; protocolos externos anotados permanecem sem verificação no órgão.

O grupo testou cadastro, edição, revisão, confirmação e contestação no navegador. A gravação mostra a abertura da câmera no celular. O restante do cadastro, incluindo a conferência da posição e o envio, aparece em outro exemplo gravado no computador. O teste móvel controlado cobriu rascunho, permissão de GPS negada e cancelamento.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.5 Generative AI

A execução local de Generative AI utiliza recuperação híbrida e Qwen3-4B-Instruct-2507, em Q4_K_M. O modelo seleciona uma evidência recuperada. A resposta corresponde ao trecho escolhido, com endereço oficial para consulta.

Na versão online, o Qwen3.8-27B, executado pelo Groq, seleciona fontes do corpus e sugere relatos a partir de fotos. O registro guarda o modelo, a data e o hash da imagem. O ResNet18 continua responsável pela análise de fissuras. A versão online foi testada na central. Os resultados de avaliação abaixo são do modelo local.

O serviço pode pedir esclarecimento, indicar falta de evidência, reconhecer uma pergunta fora do escopo e bloquear pedidos incompatíveis com suas regras. A orientação não cria protocolo e não confirma que o serviço foi solicitado.

As avaliações anteriores do projeto são mantidas nos materiais. A primeira aplicação ao conjunto reservado obteve 13 de 16 casos. A avaliação diagnóstica posterior obteve 16 de 16 em casos conhecidos. Esses dois resultados pertencem a momentos diferentes e não devem ser usados como uma única estimativa de generalização.

O vídeo original da disciplina mostra outra versão do modelo. Para verificar a integração atual, o grupo fez uma consulta pela central sobre manutenção de iluminação pública e obteve a fonte ILU.1. A resposta confirma que a consulta chegou ao serviço e retornou uma fonte.

O inicializador e os códigos do projeto estão incluídos no pacote. O modelo de aproximadamente 2,5 GB e os caches são obtidos separadamente pelo inicializador, com conferência dos hashes previstos no trabalho original.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.6 IoT

O OuviAí reconhece sons e apresenta uma resposta visual no navegador do celular. O documento e os quatro vídeos registram a abertura do modelo e os exemplos de porta, ambiente e campainha. O requisito original de uso no smartphone não exige exportação de firmware ou de pesos.

O relatório do módulo registra 78 acertos em 100 janelas de teste, 14 em 15 arquivos e 14 em 15 exemplos ao vivo. Em 12 dos 15 exemplos ao vivo, o reconhecimento foi imediato. São unidades de avaliação diferentes. Os dados de teste participaram de ajustes e compartilham fontes sonoras, o que limita sua interpretação como amostra independente.

Na central, o YAMNet reconhece o som e gera um aviso visual no navegador. O teste do vídeo usou uma batida de referência em um microfone virtual. A CNN original ficou nos materiais do trabalho. A estação física e a transmissão entre aparelhos ficaram fora do teste.

## 2.7 Processamento de Linguagem Natural

A Fábrica de Corpus reúne 88 trechos de texto, 112 pares de perguntas e respostas, 30 diálogos e 20 casos de teste sobre desastres. A central consulta o corpus textual e pode vincular um trecho ao histórico de um pedido pertinente. O vínculo utiliza a linha do material entregue, sem aceitar um texto substituto enviado pelo navegador.

Os resultados mostram fonte, endereço, página ou seção e data disponível no registro. Documentos PDF possuem páginas; a fonte HTML é localizada por seção. A consulta é textual e não corresponde a um alerta sobre a situação atual do bairro.

A planilha de revisão contém 39 registros ainda sem decisão humana preenchida. Os trechos consultados continuam sujeitos a essa pendência. Esse corpus complementa assuntos de prevenção de desastres e não é a base de todas as orientações municipais do catálogo principal.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.8 Visão Computacional

O módulo utiliza o checkpoint ResNet18 de 160 × 160 pixels. A rotina local foi preservada. A conversão ONNX para a nuvem manteve as decisões em 378 imagens e três controles. Essa comparação verifica a conversão, sem constituir nova avaliação de acurácia.

Figura 2 - Recorte usado na execução técnica de Visão Computacional

[[figura-visao]]

Fonte: acervo do trabalho de Visão, recorte 017_1135_2497.jpg. Execução em 14/11/2026.

Nesse exemplo, a rotina retornou “Sem fissura sinalizada”, com escore de fissura 0,05196 e limiar 0,49. O registro da execução contém a saída e o hash da imagem. Um exemplo isolado confirma a execução da função, mas não estima o desempenho geral.

Tabela 2 - Resultados históricos do modelo de Visão

| Medida | Amostra ou denominador | Resultado |
| --- | --- | --- |
| F1 no teste | 352 recortes | Aproximadamente 0,963 |
| Erros de classificação | 352 recortes | 13 |
| Sinal em fissuras sutis | 26 exemplos | 2 |

Fonte: métricas e análise de erros do trabalho de Visão Computacional.

Os resultados pertencem ao acervo avaliado. O desempenho em fissuras sutis é uma limitação relevante. A sinalização não determina gravidade, acessibilidade ou segurança estrutural e não comprova que um local foi reparado.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.9 Governança em IA e Business Analytics

O histórico guarda a sugestão, a decisão do revisor e a contestação. A ficha indica o canal para envio pelo solicitante. A central distingue o protocolo anotado do protocolo de demonstração. O revisor confere o retorno e a foto antes de encerrar. A consulta é pública, e a gestão exige uma chave.

O Passagem Livre compara reparos em quatro trechos didáticos. Correção conferida retira só a barreira daquele pedido; outras barreiras e condições desconhecidas permanecem. Alteração ou contestação reabre o acompanhamento e desatualiza o plano. O cálculo é determinístico, sem execução quântica ou certificação de acessibilidade.

Quadro 1 - Participação dos materiais na central

| Disciplina | Material utilizado | O que não foi integrado |
| --- | --- | --- |
| RPA | Triagem e pipeline CSV originais | Automação do envio ao órgão |
| Cluster | RPA em workers lógicos | Cluster físico dedicado |
| Quântica | QAOA simulado e comparação | QPU e agenda completa |
| Frontend | Validação e persistência do ZelaBairro | Protocolo municipal automático |
| Generative AI | Serviço local e adaptador Groq | Qwen3-4B na nuvem |
| IoT | YAMNet alternativo; vídeos | CNN original; hardware |
| PLN | Consulta ao corpus e origem do trecho | Revisão humana concluída |
| Visão | Inferência com checkpoint original | Laudo ou diagnóstico estrutural |
| Governança | Revisão, plano, histórico e indicadores | Validação com usuários ou em campo |

Fonte: implementação e materiais reunidos pelo grupo em 2026.

O painel separa pedidos sem protocolo, protocolos declarados e demonstrações. No vídeo, 21 dos 23 registros da instalação estavam sem protocolo anotado. O grupo não enviou o pedido ao órgão nem verificou um reparo no local. Os registros dos testes estão em docs/evidencias.

<!-- pagina -->
# 3 CONCLUSÃO

O ZelaBairro reuniu, no mesmo pedido, a foto, a localização, a triagem, a decisão justificada e a contestação. Na demonstração, foi possível pedir uma nova análise e consultar a decisão anterior no histórico. No Passagem Livre, simular o reparo de um único trecho deixou o caminho interrompido. A comparação mostrou por que vale a pena olhar para o percurso inteiro ao planejar os reparos.

O envio ao município depende do solicitante, e o protocolo mostrado no vídeo foi usado apenas na demonstração. O percurso é didático. O ensaio de IoT usou YAMNet no navegador, e a estação física ficou como proposta. O próximo passo é testar o fluxo com moradores e conferir em campo as condições de passagem antes de usar o sistema para orientar decisões de reparo.

# 4 LINKS

Repositório GitHub: [GOV_GS_26.2](https://github.com/luizhenriqueposs7/GOV_GS_26.2). Código, materiais das disciplinas e instruções de execução.

Vídeo integrado: [ZelaBairro | Global Solution CitizenTech](https://youtu.be/JLS1Hy6AXSM). Duração da edição: 5min41s.

Aplicativo: [Abrir o ZelaBairro](https://gov262.vercel.app/). Versão online da Central CitizenTech.

<!-- pagina -->
# REFERÊNCIAS

GOOGLE. MediaPipe Audio Classifier e YAMNet. 2026. Disponível em: [developers.google.com/edge/mediapipe/solutions/audio/audio_classifier](https://developers.google.com/edge/mediapipe/solutions/audio/audio_classifier?tab=Web). Acesso em: 17 nov. 2026.

FIAP. CitizenTech: Global Solution. 2026. Disponível em: [experience.fiap.com.br/global-solution-citizen-tech](https://experience.fiap.com.br/global-solution-citizen-tech#new-d1-global-solution). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Manutenção de calçada pública. SP156, 2026a. Disponível em: [sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Avaliação de obstáculo na calçada. SP156, 2026b. Disponível em: [sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2634](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2634). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Perguntas frequentes: iluminação pública. SP Regula, 2026. Disponível em: [prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960](https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Perguntas frequentes: SP156. 2026. Disponível em: [prefeitura.sp.gov.br/web/inovacao/w/acesso_a_informacao/350229](https://prefeitura.sp.gov.br/web/inovacao/w/acesso_a_informacao/350229). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Tapa-buraco. SP156, 2026c. Disponível em: [sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=952](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=952). Acesso em: 14 nov. 2026.

POSS, Luiz Henrique; AMORIM, Luis Filipe Chaves; HONORATO, Felipe Stefani. Trabalhos da Global Solution CitizenTech. RPA, Cluster, Computação Quântica, Frontend, Generative AI, IoT, PLN e Visão Computacional. FIAP, 2026. Arquivos reunidos na pasta materiais, com origem e hashes no manifesto.

POSS, Luiz Henrique; AMORIM, Luis Filipe Chaves; HONORATO, Felipe Stefani. Central CitizenTech: registros das verificações técnicas. 14 nov. 2026. Arquivos de evidência em docs/evidencias: testes de domínio, percurso das funções e inferência visual. Dados de demonstração fictícios.
