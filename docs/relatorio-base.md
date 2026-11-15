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

Versão de trabalho de 15 de novembro de 2026. A conclusão será elaborada com os integrantes. Os endereços do vídeo integrado e do repositório serão acrescentados após a publicação.

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

O desenvolvimento reúne nove disciplinas. RPA, persistência do Frontend, corpus de PLN e inferência de Visão são reutilizados em código. Generative AI possui um adaptador para o serviço local. IoT, Cluster e Quântica conservam contribuições externas, simuladas ou conceituais. Essa distinção orienta a leitura do relatório.

<!-- pagina -->
# 2 DESENVOLVIMENTO

## 2.1 RPA

O notebook original recebe arquivos CSV, valida os campos case_id, description e neighborhood e classifica as solicitações por regras. As funções foram exportadas sem executar as células de demonstração. A central utiliza essas funções para a triagem de novos relatos e para o processamento de lotes. Os identificadores do CSV são preservados como texto.

O caso “Calçada sem rampa acessível” retorna categoria Acessibilidade, prioridade Baixa, confiança heurística 1,0 e revisão dispensada. Essa saída foi mantida. O controle da central exige revisão para a categoria Acessibilidade e registra a decisão posterior separadamente. A confiança da regra não é uma probabilidade calibrada de acerto.

A reaplicação de um lote com os mesmos dados de origem conserva os complementos manuais e a revisão. Se a descrição ou o bairro de origem mudarem, a revisão é invalidada. A versão anterior permanece no histórico. O CSV não pode fornecer análises prontas para substituir a execução do RPA.

## 2.2 Cluster Computing

O trabalho de Cluster compara dois cenários no simulador iSPD. Os arquivos de modelo e o relatório foram incorporados como evidências do estudo de distribuição de trabalho. Não há cluster executando a aplicação da central.

Tabela 1 - Tempos dos cenários simulados no iSPD

| Cenário | Workers | Tempo simulado |
| --- | --- | --- |
| Primeiro modelo | 2 | 1,20230 s |
| Segundo modelo | 4 | 0,604501 s |

Fonte: relatório e modelos de Cluster Computing entregues pelo grupo.

A diferença equivale a aproximadamente 49,72% de redução no tempo simulado entre esses dois cenários. O resultado não mede a latência de uma solicitação completa, o modelo de linguagem ou a operação de um serviço público. Na central, o módulo participa da documentação de capacidade, sem ser apresentado como infraestrutura implantada.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.3 Computação Quântica

O relatório de Computação Quântica discute a alocação de recursos para tarefas de revisão. Esse problema se relaciona ao planejamento de uma fila quando há prioridades, restrições de disponibilidade e capacidade limitada de atendimento.

O material foi incluído como estudo conceitual. Não foi executado algoritmo quântico nem demonstrado ganho em relação a métodos clássicos. A central não modifica a prioridade de pedidos com uma rotina quântica.

Uma avaliação futura dependeria de dados operacionais e de uma comparação com alternativas clássicas adequadas ao problema. Como não existe piloto, esses dados e essa comparação não estão disponíveis. O relatório conserva essa limitação em vez de atribuir um resultado à aplicação.

## 2.4 Frontend

A central tem interface própria e reutiliza a validação e a persistência do ZelaBairro. Os bancos de relatos e de histórico ficam separados.

O formulário móvel reúne foto opcional, coordenadas confirmadas e associação declarada a um trecho do Passagem Livre. O rascunho conserva esses dados. A imagem recebe normalização e remoção de metadados. O catálogo distingue via comum e corredor de ônibus (SÃO PAULO, 2026c). O modelo de fissuras não identifica buracos.

A confirmação exige revisão justificada e dados completos. Repetir a confirmação da mesma revisão mantém o registro. Alterar o pedido ou contestar retira a decisão e o vínculo atuais, preservando o histórico. O identificador é local; protocolos externos anotados permanecem sem verificação no órgão.

Cadastro, edição, revisão, confirmação e contestação foram executados no navegador. O rascunho salvo foi recuperado sem servidor. Reenviar após perder a resposta conservou o pedido, inclusive no contrato anterior ao Passagem Livre. O acesso HTTPS protegido está preparado; câmera, GPS e instalação ainda dependem do teste físico no smartphone.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.5 Generative AI

O projeto atual de Generative AI utiliza recuperação híbrida e Qwen3-4B-Instruct-2507, quantizado em Q4_K_M. O modelo seleciona uma evidência recuperada. Quando a orientação é respondida, o texto devolvido corresponde ao trecho da fonte selecionada, com endereço oficial para consulta.

A central implementa uma chamada HTTP para esse serviço no próprio computador. O adaptador valida os estados esperados, o conteúdo da resposta e a correspondência entre orientação e fonte. Uma falha de serviço deve retornar indisponibilidade, sem trocar a execução por uma resposta histórica.

O serviço pode pedir esclarecimento, indicar falta de evidência, reconhecer uma pergunta fora do escopo e bloquear pedidos incompatíveis com suas regras. A orientação não cria protocolo e não confirma que o serviço foi solicitado.

As avaliações anteriores do projeto são mantidas nos materiais. A primeira aplicação ao conjunto reservado obteve 13 de 16 casos. A avaliação diagnóstica posterior obteve 16 de 16 em casos conhecidos. Esses dois resultados pertencem a momentos diferentes e não devem ser usados como uma única estimativa de generalização.

O vídeo anterior da disciplina foi produzido com outra versão do modelo. Ele não demonstra automaticamente a execução do Qwen3 pela central. A chamada atual foi executada pela central e retornou a fonte ILU.1 para uma pergunta sobre manutenção de iluminação pública. Essa consulta verifica a execução, sem estimar acurácia geral.

O inicializador e os códigos do projeto estão incluídos no pacote. O modelo de aproximadamente 2,5 GB e os caches são obtidos separadamente pelo inicializador, com conferência dos hashes previstos no trabalho original.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.6 IoT

O OuviAí reconhece sons e apresenta uma resposta visual no navegador do celular. O documento e os quatro vídeos registram a abertura do modelo e os exemplos de porta, ambiente e campainha. O requisito original de uso no smartphone não exige exportação de firmware ou de pesos.

O relatório do módulo registra 78 acertos em 100 janelas de teste, 14 em 15 arquivos e 14 em 15 exemplos ao vivo. Em 12 dos 15 exemplos ao vivo, o reconhecimento foi imediato. São unidades de avaliação diferentes. Os dados de teste participaram de ajustes e compartilham fontes sonoras, o que limita sua interpretação como amostra independente.

A central disponibiliza essas evidências. Não recebe previsões automaticamente do celular e não fabrica ocorrências sonoras. O benefício de acessibilidade sonora pertence ao contexto do OuviAí, distinto do fluxo municipal de calçadas e iluminação.

## 2.7 Processamento de Linguagem Natural

A Fábrica de Corpus reúne 88 trechos de texto, 112 pares de perguntas e respostas, 30 diálogos e 20 casos de teste sobre desastres. A central consulta o corpus textual e pode vincular um trecho ao histórico de um pedido pertinente. O vínculo utiliza a linha do material entregue, sem aceitar um texto substituto enviado pelo navegador.

Os resultados mostram fonte, endereço, página ou seção e data disponível no registro. Documentos PDF possuem páginas; a fonte HTML é localizada por seção. A consulta é textual e não corresponde a um alerta sobre a situação atual do bairro.

A planilha de revisão contém 39 registros ainda sem decisão humana preenchida. Os trechos consultados continuam sujeitos a essa pendência. Esse corpus complementa assuntos de prevenção de desastres e não é a base de todas as orientações municipais do catálogo principal.

<!-- pagina -->
# DESENVOLVIMENTO

## 2.8 Visão Computacional

O módulo utiliza ResNet18 e o checkpoint entregue para imagens de 160 × 160 pixels. A central normaliza a imagem enviada e executa a rotina original em processo separado. A saída contém classe, escore, limiar e sinalização. O arquivo temporário da imagem é descartado após a execução.

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

A Governança preserva a sugestão original, exige revisão, registra justificativa e permite contestação. As pendências impedem a confirmação no ZelaBairro. A chave local protege decisões e importação; não equivale a contas individuais para uso público.

O Passagem Livre compara reparos em quatro trechos de um percurso didático. Só a calçada reparada mantém a barreira da rampa; ambas tratadas permitem continuidade na hipótese. Condições desconhecidas permanecem pendentes. O plano exige revisão, conserva cenário e justificativa e fica desatualizado após mudança ou contestação. O cálculo é determinístico, sem execução quântica ou certificação de acessibilidade.

Quadro 1 - Participação dos materiais na central

| Disciplina | Material utilizado | O que não foi integrado |
| --- | --- | --- |
| RPA | Triagem e pipeline CSV originais | Automação do envio ao órgão |
| Cluster | Modelos e relatório iSPD | Cluster de produção |
| Quântica | Relatório conceitual | Algoritmo quântico executável |
| Frontend | Validação e persistência do ZelaBairro | Protocolo municipal automático |
| Generative AI | Consulta atual pelo serviço local | Abertura automática de chamado |
| IoT | Documento e vídeos do OuviAí | Eventos automáticos do celular |
| PLN | Consulta ao corpus e origem do trecho | Revisão humana concluída |
| Visão | Inferência com checkpoint original | Laudo ou diagnóstico estrutural |
| Governança | Revisão, plano, histórico e indicadores | Validação com usuários ou em campo |

Fonte: implementação e materiais reunidos pelo grupo em 2026.

Os indicadores contam registros locais; prioridades alteradas são divididas pelas revisões atuais. Não medem benefício social ou reparos. As evidências em docs/evidencias registram foto do acervo, ponto manual, vínculo, revisão, persistência, plano e contestação no navegador. O teste físico permanece pendente.

<!-- pagina -->
# 3 CONCLUSÃO

Seção reservada à elaboração conjunta com os integrantes, conforme combinado. Esta versão não deve ser apresentada como relatório final.

A redação final deverá distinguir o que a integração demonstrou tecnicamente do que permanece como hipótese de uso. Também deverá registrar os módulos externos, as limitações dos dados e a ausência de validação com pessoas.

A execução técnica está registrada em docs/evidencias. A conclusão desta seção continua reservada à discussão conjunta com os integrantes.

# 4 LINKS

Vídeo integrado de Governança: publicação pendente. A versão final deverá ter de 5 a 7 minutos e estar no YouTube como Não Listado.

Repositório do GitHub: publicação pendente. O endereço deverá apontar para a versão que contém os códigos, materiais, relatório e instruções da entrega.

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
