# Central CitizenTech

Preparação e acompanhamento local de pedidos sobre calçadas, buracos no asfalto e iluminação em São Paulo. A central recebe foto opcional e localização confirmada, pede contexto, mostra a fonte do encaminhamento, conserva a triagem original, registra uma revisão justificada e permite contestar a decisão. Depois da conferência, reutiliza a persistência do ZelaBairro.

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

As variáveis opcionais estão explicadas em `.env.example`. São variáveis do processo; não há carregamento automático de `.env`. As bases ficam em `data/central.sqlite` e `data/zelabairro.sqlite`. Fotos anexadas ao pedido são normalizadas em JPEG, têm metadados retirados e ficam em `data/fotos`, identificadas por hash. A remoção retira o anexo atual e preserva a referência anterior no histórico; o arquivo não é apagado automaticamente. A imagem enviada apenas à análise de Visão é temporária e descartada. Histórico, fotos e coordenadas não são enviados a mapas ou outros serviços externos pela central.

## Jornada móvel

O formulário oferece câmera e galeria, prévia, substituição e remoção da foto. No navegador, JPEG/PNG de até 32 MB são reduzidos a 2048 pixels no maior lado; o servidor aceita até 8 MB e 16,8 megapixels. HEIC precisa ser exportado em JPEG. A foto é evidência do relato, sem detecção automática de buracos. O modelo original de Visão permanece restrito a sinalização de fissuras em concreto.

As coordenadas são opcionais. O botão de posição pede permissão ao navegador; a pessoa deve confirmar que o ponto corresponde à ocorrência. Também é possível digitar coordenadas ou seguir apenas com a referência. GPS não determina o endereço, o bairro ou a competência do serviço.

O rascunho é salvo explicitamente em IndexedDB neste navegador, com foto e coordenadas, sem chave de revisão. Recuperá-lo exige confirmar os dados novamente. Um rascunho salvo conserva a mesma tentativa de envio após perda de resposta. Registrar outro pedido não apaga esse rascunho. Nenhum envio é automático. Limpar os dados do navegador ou perder o aparelho pode eliminar o rascunho.

Manifesto, ícones e service worker permitem instalar como PWA nos navegadores compatíveis. Só o conjunto estático do formulário entra no cache. APIs, fotos e respostas não são armazenadas pelo service worker. O envio e o acompanhamento dependem do servidor. Ao publicar uma nova versão, altere a versão de cache em `web/sw.js` e feche/reabra as abas para ativar a atualização.

A abertura sem servidor e a recuperação do rascunho foram verificadas no navegador desta máquina. Câmera, GPS reais e instalação em smartphone continuam sem teste em aparelho. Para usar no celular, é necessário preparar um acesso HTTPS protegido; o endereço 127.0.0.1 do computador não abre a central no telefone. Não existe acesso externo publicado nesta entrega de trabalho.

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

Os testes JavaScript usam Node.js 20 ou posterior; o uso da central no navegador não exige Node.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -v
node --test tests/mobile.test.mjs tests/sw.test.mjs
```

Os testes usam bancos temporários e entradas fictícias. Cobrem o controle da barreira, preservação das decisões, contestação, atualização, repetição de lote, fonte de PLN, imagens inválidas, chave de revisão e falha de serviço. Isso verifica comportamento técnico; não é teste com usuários. O registro do que efetivamente foi executado nesta máquina está em `docs/progresso.md`.

Em 14/11/2026, os 55 testes Python e 7 testes JavaScript passaram, incluindo contratos móveis, reenvio e cache do formulário. O servidor foi iniciado e a página inicial abriu no navegador. Uma consulta real de Generative AI pela central retornou orientação com fonte oficial; a evidência está em docs/evidencias/execucao-http-genai-2026-11-14.json. Como verificação complementar, `python -X utf8 verificar_fluxo.py` executa as funções reais das rotas e a persistência em bancos temporários; esse percurso também passou. O fluxo de cadastro, revisão, confirmação no ZelaBairro e contestação foi executado e repetido pela interface. O teste também conferiu o histórico, o bloqueio de confirmação sem revisão, a preservação de rascunho e a repetição da confirmação sem duplicação por versão. Evidências: docs/evidencias/fluxo-browser-2026-11-14.json e docs/evidencias/fluxo-persistencia-2026-11-14.json.

A ampliação móvel, o teste de resposta perdida e as verificações do formulário sem servidor estão em `docs/evidencias/mobile-2026-11-14.json`. A sonda de falha é `tests/tools/proxy-resposta-perdida.mjs`: aponta somente à prévia local em 8841 e usa 8842, sem interferir na instância principal.

## Limites para uso fora da demonstração

Esta instalação não possui contas individuais, isolamento entre solicitantes nem controle de leitura por usuário. A chave protege operações de revisão e lote; as demais operações pertencem à demonstração local. Não exponha a porta na rede nem insira dados pessoais. Para operar com pessoas reais, seria necessário definir responsáveis pelo atendimento, autenticação, autorizações, retenção e proteção de dados, além de acordos operacionais com quem recebe os pedidos.

O relatório e o roteiro da entrega ficam em `docs/`. A conclusão será elaborada com o integrante. Os links do vídeo final não listado e do repositório público dependem da publicação; os vídeos de módulos anteriores não substituem a gravação integrada de 5 a 7 minutos.
