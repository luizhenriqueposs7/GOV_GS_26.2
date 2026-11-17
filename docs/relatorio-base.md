# CENTRAL CITIZENTECH

Planejamento de acesso, pedidos e revisão

Governança em IA e Business Analytics · Global Solution 2026

Luiz Henrique Poss · RM562177

Luis Filipe Chaves Amorim · RM564706

Felipe Stefani Honorato · RM563380

São Paulo · 2026

VERSÃO DE TRABALHO. Conclusão conjunta e links de publicação pendentes.

<!-- pagina -->
# FOLHA DE ROSTO

Luiz Henrique Poss · RM562177

Luis Filipe Chaves Amorim · RM564706

Felipe Stefani Honorato · RM563380

## CENTRAL CITIZENTECH

Planejamento de acesso, pedidos e revisão

Relatório de integração dos trabalhos da Global Solution, apresentado à disciplina de Governança em IA e Business Analytics da FIAP. O documento reúne os materiais das disciplinas, descreve a participação de cada módulo e registra os limites da aplicação construída.

O projeto utiliza dados fictícios. Não houve testes com pessoas nem validação em campo, por decisão do grupo. As verificações mencionadas neste relatório são técnicas.

Versão de trabalho de 16 de novembro de 2026. A conclusão será elaborada com os integrantes. O repositório está indicado no tópico Links; o endereço do vídeo integrado será acrescentado após a publicação.

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

O público previsto são moradores que precisam preparar pedidos e responsáveis por uma eventual triagem local. Esse uso ainda é uma hipótese de aplicação. Não houve acesso a uma instituição parceira, testes com pessoas ou acompanhamento de solicitações reais. Não se afirma redução de prazo ou de erros no atendimento público.

Figura 1 - Fluxo de preparação, revisão e registro local

[[figura-fluxo]]

Fonte: elaboração do grupo, a partir da aplicação construída em 2026.

As nove disciplinas participam com alcances distintos. RPA, Frontend, PLN e Visão reutilizam código. Generative AI tem adaptação online. Cluster processa lotes; Quântica apoia a seleção de revisões em simulador. IoT mantém execução externa e interface conceitual.

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

Os 49,72% pertencem ao iSPD. Na central, cada minilote mede seus tempos: threads locais ou invocações HTTP na Vercel, sem garantia de máquinas distintas. Rede, inicialização e banco podem superar ganhos. O modo com workers limita a gravação a 50 registros aceitos por lote.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.3 Computação Quântica

O estudo de alocação foi ampliado com um piloto de seleção de até oito revisões. O gestor informa prioridades, durações estimadas e capacidade. Obrigatórios sem capacidade geram aviso; casos adiados ficam explícitos.

O QAOA p=1 é calculado em vetor de estado NumPy: fase de custo e rotações Rx, com busca clássica de parâmetros. Compara-se o estado factível mais provável com fila e enumeração exata. Não há QPU ou ganho quântico demonstrado.

O plano justificado fica no histórico e abre os pedidos para revisão humana. Mudanças exigem recalcular. É um recorte do estudo: não modela turnos, competências, prazos ou equidade, nem altera prioridades automaticamente.

## 2.4 Frontend

A central reutiliza a validação e a persistência do ZelaBairro. Localmente, os bancos ficam separados. Na adaptação online, Postgres mantém relatos e histórico na mesma transação, com fotos privadas no Supabase.

Na jornada móvel, a foto prepara ocorrência, impactos possíveis e pedido de vistoria, sem medir dimensões. O GPS sugere região pela BigDataCloud, sem rua ou número. A pessoa confere texto e ponto antes de enviar. O rascunho conserva os dados; a foto perde metadados. O catálogo distingue os serviços (SÃO PAULO, 2026c).

A confirmação exige revisão justificada e dados completos. Repetir a confirmação da mesma revisão mantém o registro. Alterar o pedido ou contestar retira a decisão e o vínculo atuais, preservando o histórico. O identificador é da central; protocolos externos anotados permanecem sem verificação no órgão.

Cadastro, edição, revisão, confirmação e contestação foram executados no navegador. A prévia não grava pedidos; a sugestão original e as correções ficam rastreáveis. O teste móvel controlado conferiu rascunho, GPS negado e cancelamento. Câmera, GPS reais e instalação ainda dependem do teste físico no smartphone.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.5 Generative AI

A execução local de Generative AI utiliza recuperação híbrida e Qwen3-4B-Instruct-2507, em Q4_K_M. O modelo seleciona uma evidência recuperada. A resposta corresponde ao trecho escolhido, com endereço oficial para consulta.

Na versão online, Qwen3.8-27B no Groq Free seleciona evidências do corpus e gera descrições preliminares por foto. A sugestão guarda modelo, data e hash da imagem; não substitui o ResNet18 nem a revisão. Texto retornou ILU.1; a foto gerou relato. Sobrecarga exigiu tentativas limitadas. As avaliações abaixo pertencem ao modelo local.

O serviço pode pedir esclarecimento, indicar falta de evidência, reconhecer uma pergunta fora do escopo e bloquear pedidos incompatíveis com suas regras. A orientação não cria protocolo e não confirma que o serviço foi solicitado.

As avaliações anteriores do projeto são mantidas nos materiais. A primeira aplicação ao conjunto reservado obteve 13 de 16 casos. A avaliação diagnóstica posterior obteve 16 de 16 em casos conhecidos. Esses dois resultados pertencem a momentos diferentes e não devem ser usados como uma única estimativa de generalização.

O vídeo anterior da disciplina foi produzido com outra versão do modelo. Ele não demonstra automaticamente a execução do Qwen3 pela central. A chamada atual foi executada pela central e retornou a fonte ILU.1 para uma pergunta sobre manutenção de iluminação pública. Essa consulta verifica a execução, sem estimar acurácia geral.

O inicializador e os códigos do projeto estão incluídos no pacote. O modelo de aproximadamente 2,5 GB e os caches são obtidos separadamente pelo inicializador, com conferência dos hashes previstos no trabalho original.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.6 IoT

O OuviAí reconhece sons e apresenta uma resposta visual no navegador do celular. O documento e os quatro vídeos registram a abertura do modelo e os exemplos de porta, ambiente e campainha. O requisito original de uso no smartphone não exige exportação de firmware ou de pesos.

O relatório do módulo registra 78 acertos em 100 janelas de teste, 14 em 15 arquivos e 14 em 15 exemplos ao vivo. Em 12 dos 15 exemplos ao vivo, o reconhecimento foi imediato. São unidades de avaliação diferentes. Os dados de teste participaram de ajustes e compartilham fontes sonoras, o que limita sua interpretação como amostra independente.

A central apresenta evidências e uma estação conceitual com eventos simulados, sem microfone ou inferência. Hardware e recepção de previsões reais permanecem pendentes. O fluxo municipal não utiliza os sons.

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

A Governança preserva sugestão, revisão e contestação. A ficha reúne relato, destino e canal; o envio cabe ao solicitante. Protocolo declarado e demonstração ficam separados. Retorno e foto posterior exigem conferência humana para encerrar. Pedidos e fotos são públicos; a chave protege decisões de gestão.

O Passagem Livre compara reparos em quatro trechos didáticos. Correção conferida retira só a barreira daquele pedido; outras barreiras e condições desconhecidas permanecem. Alteração ou contestação reabre o acompanhamento e desatualiza o plano. O cálculo é determinístico, sem execução quântica ou certificação de acessibilidade.

Quadro 1 - Participação dos materiais na central

| Disciplina | Material utilizado | O que não foi integrado |
| --- | --- | --- |
| RPA | Triagem e pipeline CSV originais | Automação do envio ao órgão |
| Cluster | RPA em workers lógicos | Cluster físico dedicado |
| Quântica | QAOA simulado e comparação | QPU e agenda completa |
| Frontend | Validação e persistência do ZelaBairro | Protocolo municipal automático |
| Generative AI | Serviço local e adaptador Groq | Qwen3-4B na nuvem |
| IoT | Tela conceitual e vídeos | Modelo e eventos reais |
| PLN | Consulta ao corpus e origem do trecho | Revisão humana concluída |
| Visão | Inferência com checkpoint original | Laudo ou diagnóstico estrutural |
| Governança | Revisão, plano, histórico e indicadores | Validação com usuários ou em campo |

Fonte: implementação e materiais reunidos pelo grupo em 2026.

Indicadores separam pedidos sem protocolo, protocolos declarados e demonstrações. Correções conferidas são decisões do protótipo, sem confirmação municipal. Não houve envio ao órgão nem reparo validado. Evidências técnicas estão em docs/evidencias. O teste físico permanece pendente.

<!-- pagina -->
# 3 CONCLUSÃO

Seção reservada à elaboração conjunta com os integrantes, conforme combinado. Esta versão não deve ser apresentada como relatório final.

A redação final deverá distinguir o que a integração demonstrou tecnicamente do que permanece como hipótese de uso. Também deverá registrar os módulos externos, as limitações dos dados e a ausência de validação com pessoas.

A execução técnica está registrada em docs/evidencias. A conclusão desta seção continua reservada à discussão conjunta com os integrantes.

# 4 LINKS

Vídeo integrado de Governança: publicação pendente. A versão final deverá ter de 5 a 7 minutos e estar no YouTube como Não Listado.

Repositório do GitHub: [GOV_GS_26.2](https://github.com/luizhenriqueposs7/GOV_GS_26.2). Destino dos códigos, materiais, relatório e instruções da entrega.

Os quatro vídeos do OuviAí e os vídeos das outras disciplinas são evidências complementares. Eles não substituem o vídeo integrado exigido para Governança.

<!-- pagina -->
# REFERÊNCIAS

FIAP. CitizenTech: Global Solution. 2026. Disponível em: [experience.fiap.com.br/global-solution-citizen-tech](https://experience.fiap.com.br/global-solution-citizen-tech#new-d1-global-solution). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Manutenção de calçada pública. SP156, 2026a. Disponível em: [sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Avaliação de obstáculo na calçada. SP156, 2026b. Disponível em: [sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2634](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2634). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Perguntas frequentes: iluminação pública. SP Regula, 2026. Disponível em: [prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960](https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Perguntas frequentes: SP156. 2026. Disponível em: [prefeitura.sp.gov.br/web/inovacao/w/acesso_a_informacao/350229](https://prefeitura.sp.gov.br/web/inovacao/w/acesso_a_informacao/350229). Acesso em: 14 nov. 2026.

SÃO PAULO (Município). Tapa-buraco. SP156, 2026c. Disponível em: [sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=952](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=952). Acesso em: 14 nov. 2026.

POSS, Luiz Henrique; AMORIM, Luis Filipe Chaves; HONORATO, Felipe Stefani. Trabalhos da Global Solution CitizenTech. RPA, Cluster, Computação Quântica, Frontend, Generative AI, IoT, PLN e Visão Computacional. FIAP, 2026. Arquivos reunidos na pasta materiais, com origem e hashes no manifesto.

POSS, Luiz Henrique; AMORIM, Luis Filipe Chaves; HONORATO, Felipe Stefani. Central CitizenTech: registros das verificações técnicas. 14 nov. 2026. Arquivos de evidência em docs/evidencias: testes de domínio, percurso das funções e inferência visual. Dados de demonstração fictícios.
