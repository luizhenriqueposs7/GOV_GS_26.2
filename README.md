# Central CitizenTech

Preparação e acompanhamento local de pedidos sobre calçadas e iluminação em São Paulo. A central pede contexto, mostra a fonte do encaminhamento, conserva a triagem original, registra uma revisão justificada e permite contestar a decisão. Depois da conferência, reutiliza a persistência do ZelaBairro.

Protótipo acadêmico para Governança em IA e Business Analytics, GS CitizenTech 2026. Use somente dados fictícios. Não abre chamado municipal e não foi validado com pessoas ou em campo.

## Executar no Windows

Requer Python 3.13 e PowerShell. Na pasta deste arquivo:

```powershell
.\INICIAR.ps1 -Instalar -Visao
```

A primeira instalação de Visão baixa cerca de 620 MB de bibliotecas de CPU. Nas próximas execuções, basta ` .\INICIAR.ps1 `. Abra [a central local](http://127.0.0.1:8840). O serviço escuta apenas no computador, com uma instância. A chave para revisar é gerada em `data/chave-gestao.txt`, se `GOV_MANAGER_KEY` não estiver definida. Esse arquivo não é servido pela aplicação nem versionado.

Generative AI usa o projeto original em processo separado. Em outro terminal:

```powershell
.\INICIAR-IA.ps1
```

O inicializador preservado baixa Qwen3-4B-Instruct-2507 Q4_K_M e o motor llama.cpp, conferindo os hashes. A primeira execução também prepara embeddings. O modelo ocupa aproximadamente 2,5 GB, além das bibliotecas. Sem esse serviço, a central informa indisponibilidade ao consultar o assistente; as outras funções continuam independentes.

Para reutilizar os arquivos e o ambiente existentes nesta máquina:

```powershell
$env:CITIZENTECH_GENAI_PROJECT = (Resolve-Path ..\CitizenTech_Generative_AI).Path
$env:CITIZENTECH_GENAI_PYTHON = Join-Path $env:CITIZENTECH_GENAI_PROJECT '.runtime/instalacao-limpa-20261110/.venv/Scripts/python.exe'
.\INICIAR-IA.ps1
```

As variáveis opcionais estão explicadas em `.env.example`. São variáveis do processo; não há carregamento automático de `.env`. As bases ficam em `data/central.sqlite` e `data/zelabairro.sqlite`; o histórico e as imagens não são enviados a serviços externos pela central. A imagem é normalizada, analisada em arquivo temporário e descartada. O histórico recebe a saída da análise quando houver vínculo selecionado.

## Percurso da demonstração

1. Registre um relato fictício de calçada danificada em praça, com bairro, referência e contexto de área pública. Confira a carta do serviço 931. O identificador exibido é local.
2. Em Revisão, selecione o pedido, preencha identificação, prioridade, justificativa e chave. Confirme no ZelaBairro. A rotina original grava em banco local separado; repetir a confirmação da mesma revisão conserva o mesmo registro.
3. Em Acompanhar, peça nova análise. A decisão sai do estado atual e continua no histórico. Corrigir informações também exige nova revisão quando os dados mudam.
4. Registre “Calçada sem rampa acessível”. Confira a sugestão original de prioridade Baixa e revisão dispensada. O novo controle exige revisão da categoria Acessibilidade. O serviço permanece indefinido, inclusive se o contexto selecionado for área pública.
5. Em Evidências, consulte o corpus de PLN e vincule um trecho pertinente. Execute a inferência de Visão sobre uma imagem do acervo em `materiais/visao/data/recortes/`. Consulte o assistente com seu serviço iniciado. Cada vínculo conserva o resultado e a origem.

Não existem registros inseridos automaticamente nem contagens de impacto inventadas. As quatro métricas contam os pedidos desta instalação. “Prioridades alteradas” usa como denominador somente as revisões atuais, não o total de pedidos. A situação local não demonstra execução de um serviço público.

## Integração por disciplina

| Disciplina | Participação na central | Limite |
|---|---|---|
| RPA | Funções exportadas do notebook por AST, triagem e importação CSV | Regras de palavras e confiança heurística |
| Cluster Computing | Relatório e modelos iSPD de 2 e 4 workers | Simulação histórica; não é infraestrutura de produção |
| Computação Quântica | Relatório de alternativas para alocação da revisão | Estudo conceitual; nenhum ganho quântico demonstrado |
| Frontend | Validação e persistência originais do ZelaBairro, acionadas pela central | Interface nova; protocolo local de POC |
| Generative AI | Chamada HTTP local do projeto atual, com seleção de fonte pelo Qwen3 | Execução depende do serviço e modelo; métricas históricas identificadas |
| IoT | Documento e quatro vídeos do OuviAí no celular | Execução externa; sem fluxo automático de eventos para a central |
| PLN | Busca FTS5 no corpus original e vinculação de trecho com origem | Material de desastres; revisão humana do corpus pendente |
| Visão Computacional | Inferência atual do ResNet18, checkpoint e rotina originais | Sinalização de fissura; não constitui laudo |
| Governança e Business Analytics | Revisão, justificativa, contestação, histórico e indicadores calculados | Sem validação em campo |

O corpus de PLN pertence ao tema de prevenção de desastres e complementa casos pertinentes. Ele não fundamenta todas as orientações de calçadas e iluminação. As cartas municipais do fluxo principal foram curadas separadamente. O OuviAí atende acessibilidade sonora em outro contexto e permanece como módulo externo do conjunto de trabalhos.

## Fontes e materiais

`materiais/manifesto.json` relaciona os documentos expostos pela interface, origem e SHA-256. `materiais/arquivos.sha256.json` relaciona os arquivos do pacote de materiais. Os originais na pasta de trabalhos foram preservados. O checkpoint de Visão está incluído; os caches e pesos de Generative AI são obtidos pelo inicializador original e não entram no Git. A pasta de Visão conserva também o código de seu aplicativo anterior; a central importa somente `visao.py`, sem usar o assistente antigo desse trabalho.

Catálogo consultado em 14/11/2026: [calçada pública](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931), [obstáculos na calçada](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2634) e [iluminação](https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960). O serviço 906 é remissão da carta 931; seus requisitos completos não foram recuperados nesta conferência. O usuário deve consultar a carta antes de enviar o pedido. Nenhuma chamada autenticada à API SP156 foi executada.

## Verificações técnicas

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -v
```

Os testes usam bancos temporários e entradas fictícias. Cobrem o controle da barreira, preservação das decisões, contestação, atualização, repetição de lote, fonte de PLN, imagens inválidas, chave de revisão e falha de serviço. Isso verifica comportamento técnico; não é teste com usuários. O registro do que efetivamente foi executado nesta máquina está em `docs/progresso.md`.

Em 14/11/2026, os 30 testes de catálogo, registros e módulos passaram. A suíte HTTP não concluiu por bloqueio de comunicação local no ambiente desta sessão; não está declarada aprovada. Como verificação complementar, `python -X utf8 verificar_fluxo.py` executa as funções reais das rotas e a persistência em bancos temporários. Esse percurso passou, sem substituir a conferência HTTP e visual que ainda precisa ser feita.

## Limites para uso fora da demonstração

Esta instalação não possui contas individuais, isolamento entre solicitantes nem controle de leitura por usuário. A chave protege operações de revisão e lote; as demais operações pertencem à demonstração local. Não exponha a porta na rede nem insira dados pessoais. Para operar com pessoas reais, seria necessário definir responsáveis pelo atendimento, autenticação, autorizações, retenção e proteção de dados, além de acordos operacionais com quem recebe os pedidos.

O relatório e o roteiro da entrega ficam em `docs/`. A conclusão será elaborada com o integrante. Os links do vídeo final não listado e do repositório público dependem da publicação; os vídeos de módulos anteriores não substituem a gravação integrada de 5 a 7 minutos.
