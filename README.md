# ZelaBairro · Central CitizenTech

Repositório da entrega: [GOV_GS_26.2](https://github.com/luizhenriqueposs7/GOV_GS_26.2). O código, os materiais das nove disciplinas e as instruções de execução estão reunidos neste projeto.

O [relatório de trabalho em PDF](output/pdf/Central_CitizenTech_Governanca_Versao_de_Trabalho.pdf) tem 14 páginas. A conclusão será elaborada com os integrantes. O [roteiro do vídeo integrado](docs/roteiro-video.md) prevê 6min30s; o vídeo deve ser publicado como Não Listado e seu link ainda será acrescentado. A central está em [gov262.vercel.app](https://gov262.vercel.app), com acesso público sem login. A execução local continua disponível.

A jornada móvel agora tem duas etapas: **tirar foto → conferir e enviar**. A foto gera uma descrição preliminar pelo Groq, com tentativas limitadas em caso de lotação; com permissão, o aparelho obtém GPS e consulta uma região aproximada. Texto e ponto continuam editáveis. A prévia não cria pedido. A sugestão original é assinada pelo servidor e vinculada à foto, preservando origem e correções no histórico. Cadastro manual, revisão, confirmação e contestação permanecem disponíveis. [Teste no celular](docs/teste-celular.md).


Preparação e acompanhamento local de pedidos sobre calçadas, buracos no asfalto e iluminação em São Paulo. A central recebe foto opcional e localização confirmada, pede contexto, mostra a fonte do encaminhamento, conserva a triagem original, registra uma revisão justificada e permite contestar a decisão. Depois da conferência, reutiliza a persistência do ZelaBairro.

O **Passagem Livre** relaciona pedidos em um percurso didático de quatro trechos, do ponto de ônibus até uma unidade de saúde ilustrativa. Compara reparos isolados e combinados, mantém condições desconhecidas e registra planos justificados sobre as versões dos pedidos. A linha no mapa é esquemática, sem levantamento de calçadas ou garantia de acessibilidade.

Protótipo acadêmico para Governança em IA e Business Analytics, GS CitizenTech 2026. Use relatos identificados como teste, sem nomes, contatos ou documentos. A gravação técnica pode usar foto e posição reais, conferidas pela pessoa e mantidas na base local. Não abre chamado municipal e não foi validado com moradores ou em campo.

## Executar no Windows

Para a adaptação à Vercel, veja [configuração e requisitos de publicação](docs/publicacao-vercel.md). O ponto de entrada e as dependências estão em `pyproject.toml`. O modo online usa Postgres e fotos privadas no Supabase, preserva a execução local e identifica a troca do modelo de Generative AI para Groq Free. As verificações e os limites estão registrados nesse documento.

Em 16/11/2026, o fluxo foi verificado pelo HTTPS: foto, localização manual confirmada, revisão, confirmação na persistência original do ZelaBairro, contestação, Visão e Groq com fonte. RPA processou um registro e rejeitou outro; PLN retornou trechos do corpus. No Passagem Livre, a contestação desatualizou o plano e impediu novo salvamento sem revisão. Passaram 139 testes Python e 25 JavaScript. O relatório mantém 14 páginas. Câmera e GPS físicos, conclusão e vídeo final continuam pendentes.

Requer Python 3.13 e PowerShell. Na pasta deste arquivo:

```powershell
.\INICIAR.ps1 -Instalar -Visao
```

A primeira instalação de Visão baixa cerca de 620 MB de bibliotecas de CPU. Nas próximas execuções, basta ` .\INICIAR.ps1 `. Abra [a central local](http://127.0.0.1:8840). O serviço escuta apenas no computador, com uma instância. A chave para revisar é gerada em `data/chave-gestao.txt`, se `GOV_MANAGER_KEY` não estiver definida. Esse arquivo não é servido pela aplicação nem versionado.

### Preparar a gravação

Com os ambientes já instalados, execute `./PREPARAR.ps1`. Ele inicia ou reutiliza a central e a IA local, sem abrir acesso externo, e executa sete verificações: central, RPA, registro/revisão/contestação em banco temporário, PLN, inferência de Visão, resposta atual de Generative AI e catálogo de materiais. O resultado atual fica em `data/runtime/prontidao.json`; uma falha impede a mensagem de preparação concluída. Nenhum pedido de teste é criado na base principal por esse diagnóstico.

Para abrir também o acesso HTTPS protegido no momento de gravar, use `./PREPARAR.ps1 -Celular -Email SEU_EMAIL -Minutos 60`. O e-mail deve ser o autorizado para o teste. O script permanece acompanhando o túnel até o encerramento; o computador precisa continuar ligado. As instruções do telefone estão em [teste no celular](docs/teste-celular.md).

Os caminhos do ambiente de IA desta máquina ficam em `data/preparacao-local.json`, fora do Git, com os campos `PastaProjetoIA` e `PythonIA`. As variáveis `CITIZENTECH_GENAI_PROJECT` e `CITIZENTECH_GENAI_PYTHON` têm prioridade. Sem configuração, o preparador procura o ambiente em `materiais/genai`. Se faltar ambiente ou modelo, indica a instalação necessária antes da gravação. Se apenas parte da IA estiver respondendo, interrompe com orientação de reinício, sem encerrar processos desconhecidos.

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

As variáveis opcionais estão explicadas em `.env.example`. São variáveis do processo; não há carregamento automático de `.env`. As bases ficam em `data/central.sqlite` e `data/zelabairro.sqlite`. Fotos anexadas ao pedido são normalizadas em JPEG, têm metadados retirados e ficam em `data/fotos`, identificadas por hash. A remoção retira o anexo atual e preserva a referência anterior no histórico; o arquivo não é apagado automaticamente. A imagem enviada apenas à análise de Visão é temporária e descartada. Fotos, textos e histórico permanecem na central. Ao abrir o mapa, o navegador solicita imagens da área visualizada ao OpenStreetMap; essa área pode revelar a localização do ponto. Não há geocodificação ou envio do relato ao provedor.

## Jornada móvel

O registro tem três etapas: foto e relato, localização e conferência. Oferece câmera ao vivo em navegadores compatíveis, câmera do aparelho e galeria, com prévia, substituição e remoção da foto. A espera pela permissão não bloqueia todo o formulário. Cancelar ou trocar de etapa descarta leituras atrasadas; um stream que chega depois do cancelamento é fechado. Permissão negada mantém as outras opções e o envio somente por texto. No navegador, JPEG/PNG de até 32 MB são reduzidos a 2048 pixels no maior lado; o servidor aceita até 8 MB e 16,8 megapixels. HEIC precisa ser exportado em JPEG. A foto é evidência do relato, sem detecção automática de buracos. O modelo original de Visão permanece restrito a sinalização de fissuras em concreto.

As coordenadas são opcionais. É possível marcar ou arrastar o ponto no mapa, usar GPS, digitar coordenadas ou seguir apenas com a referência. O botão de posição pede permissão ao navegador. Mudar o ponto, editar ou recuperar um rascunho exige nova confirmação. GPS não determina o endereço, o bairro ou a competência do serviço.

O rascunho é salvo explicitamente em IndexedDB neste navegador, com foto e coordenadas, sem chave de revisão. Recuperá-lo exige confirmar os dados novamente. Um rascunho salvo conserva a mesma tentativa de envio após perda de resposta. Registrar outro pedido não apaga esse rascunho. Nenhum envio é automático. Limpar os dados do navegador ou perder o aparelho pode eliminar o rascunho.

Manifesto, ícones e service worker permitem instalar como PWA nos navegadores compatíveis. Só o conjunto estático do formulário entra no cache. APIs, fotos, respostas e tiles do mapa não são armazenados pelo service worker. Mapas, envio e acompanhamento precisam de conexão. Ao publicar uma nova versão, altere a versão de cache em `web/sw.js` e feche/reabra as abas para ativar a atualização.

## Mapa e revisão

A central abre com mapa, busca por rua/bairro/registro e filtros de situação. Pedidos sem coordenadas continuam na lista acessível. Os marcadores abrem o pedido, o histórico e a revisão. Outros registros a até 100 m aparecem com distância em linha reta; isso não confirma duplicidade e não funde pedidos.

Leaflet 1.9.4 e a fonte Archivo estão em `web/vendor`, com licenças. Os tiles visíveis vêm de [OpenStreetMap](https://operations.osmfoundation.org/policies/tiles/), com atribuição no mapa e cache normal do navegador. Não há download em lote ou mapa offline. O uso da biblioteca segue a [documentação do Leaflet](https://leafletjs.com/reference-1.9.4.html).

Na revisão, a foto, o relato, a sugestão do RPA, a justificativa humana e o histórico ocupam áreas distintas. A chave continua obrigatória para decidir e confirmar no ZelaBairro. A contestação retira a decisão do estado atual e exige nova revisão, sem apagar as versões anteriores.

A abertura sem servidor e a recuperação do rascunho foram verificadas no navegador desta máquina. Câmera, GPS reais e instalação em smartphone continuam sem teste em aparelho pelo assistente. O acesso temporário para o teste da pessoa responsável usa HTTPS e código enviado ao e-mail autorizado. Veja [teste no celular](docs/teste-celular.md). O link dura até uma hora por padrão e muda a cada inicialização; não é uma publicação de produção. O endereço 127.0.0.1 do computador não abre a central no telefone.

## Percurso da demonstração

Abra [Passagem Livre](http://127.0.0.1:8840/#passagem). Em “Preparar o cenário para gravar”, use a chave local no campo da decisão e prepare os dois pedidos fictícios. A ação é explícita e idempotente: não acontece na inicialização e repetir não apaga contestação ou edição. Os quatro pedidos anteriores à ampliação ficam preservados. Novas instalações começam sem pedidos.

Marque só a calçada: a rampa ainda interrompe a ligação. Marque os dois: aparece continuidade **na hipótese do cenário**. Revise cada pedido e registre o plano com identificação e justificativa. A calçada pode ser confirmada na persistência do ZelaBairro; o pedido relacionado à rampa conserva a pendência de enquadramento municipal do catálogo e não pode ser confirmado enquanto ela existir. Planejar uma intervenção não resolve essa pendência. Contestar qualquer pedido retira a revisão atual e torna o plano anterior desatualizado. O conteúdo da decisão permanece consultável.

No celular, “Registrar observação neste trecho” abre o formulário. Na localização, escolha o trecho e informe passagem interrompida, dificultada ou condição que não conseguiu avaliar. O resumo, a edição e o rascunho conservam o vínculo. O ponto confirmado do pedido não é ajustado ao desenho: a associação é declarada pela pessoa, sem correspondência geográfica automática. Para um teste fora do percurso ilustrativo, registre o pedido sem vínculo. Um relato de condição desconhecida permanece na contagem e não vira livre ao simular reparo. Os números contam trechos, sem estimar pessoas beneficiadas, custo ou prioridade municipal.

Planos ficam na tabela `planos_passagem` da base atual, sem substituição de versões. O servidor calcula o resultado, exige revisão atual de todos os pedidos vinculados e compara a assinatura das entradas dentro da mesma transação da gravação. Alterar uma entrada pertinente, evidência ou revisão torna a base anterior desatualizada. Simular não altera pedidos, não encerra atendimento e não registra obra executada.

1. Registre um relato fictício de calçada danificada em praça, com bairro, referência e contexto de área pública. Confira a carta do serviço 931. O identificador exibido é local.
2. Em Revisão, selecione o pedido, preencha identificação, prioridade, justificativa e chave. Confirme no ZelaBairro. A rotina original grava em banco local separado; repetir a confirmação da mesma revisão conserva o mesmo registro.
3. Em Acompanhar, peça nova análise. A decisão sai do estado atual e continua no histórico. Corrigir informações também exige nova revisão quando os dados mudam.
4. Registre “Calçada sem rampa acessível”. Confira a sugestão original de prioridade Baixa e revisão dispensada. O novo controle exige revisão da categoria Acessibilidade. O serviço permanece indefinido, inclusive se o contexto selecionado for área pública.
5. Em Evidências, consulte o corpus de PLN e vincule um trecho pertinente. Execute a inferência de Visão sobre uma imagem do acervo em `materiais/visao/data/recortes/`. Consulte o assistente com seu serviço iniciado. Cada vínculo conserva o resultado e a origem.

Não existem registros inseridos automaticamente nem contagens de impacto inventadas. O cenário fictício só é preparado por ação explícita do gestor. As quatro métricas contam os pedidos desta instalação. “Prioridades alteradas” usa como denominador somente as revisões atuais, não o total de pedidos. A situação local não demonstra execução de um serviço público.

## Integração por disciplina

| Disciplina | Participação na central | Limite |
|---|---|---|
| RPA | Funções exportadas do notebook por AST, triagem e importação CSV | Regras de palavras e confiança heurística |
| Cluster Computing | Relatório e modelos iSPD de 2 e 4 workers | Simulação histórica; não é infraestrutura de produção |
| Computação Quântica | Relatório de alternativas para alocação da revisão | Estudo conceitual; nenhum ganho quântico demonstrado |
| Frontend | Validação e persistência originais do ZelaBairro, acionadas pela central | Interface nova; protocolo local de POC |
| Generative AI | Qwen3-4B local; seleção Groq online com corpus original | Modelo online identificado; métricas históricas do original |
| IoT | Documento e quatro vídeos do OuviAí no celular | Execução externa; sem fluxo automático de eventos para a central |
| PLN | Busca FTS5 no corpus original e vinculação de trecho com origem | Material de desastres; revisão humana do corpus pendente |
| Visão Computacional | Inferência atual do ResNet18, checkpoint e rotina originais | Sinalização de fissura; não constitui laudo |
| Governança e Business Analytics | Revisão, justificativa, contestação, histórico, indicadores e comparação conjunta de reparos no Passagem Livre | Percurso didático e cálculo determinístico, sem validação em campo |

O corpus de PLN pertence ao tema de prevenção de desastres e complementa casos pertinentes. Ele não fundamenta todas as orientações de calçadas e iluminação. As cartas municipais do fluxo principal foram curadas separadamente. O OuviAí atende acessibilidade sonora em outro contexto e permanece como módulo externo do conjunto de trabalhos.

## Fontes e materiais

`materiais/manifesto.json` relaciona os documentos expostos pela interface, origem e SHA-256. `materiais/arquivos.sha256.json` relaciona os arquivos do pacote de materiais. Os originais na pasta de trabalhos foram preservados. O checkpoint de Visão está incluído; os caches e pesos de Generative AI são obtidos pelo inicializador original e não entram no Git. A pasta de Visão conserva também o código de seu aplicativo anterior; a central importa somente `visao.py`, sem usar o assistente antigo desse trabalho.

Catálogo consultado em 14/11/2026: [calçada pública](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=931), [obstáculos na calçada](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=2634) e [iluminação](https://prefeitura.sp.gov.br/web/spregula/w/iluminacao_publica/perguntas_frequentes/355960). O serviço 906 é remissão da carta 931; seus requisitos completos não foram recuperados nesta conferência. O usuário deve consultar a carta antes de enviar o pedido. Nenhuma chamada autenticada à API SP156 foi executada.

## Verificações técnicas

Os testes JavaScript usam Node.js 20 ou posterior; o uso da central no navegador não exige Node.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -v
node --test tests/mobile.test.mjs tests/sw.test.mjs tests/mapa.test.mjs
```

Os testes usam bancos temporários e entradas fictícias. Cobrem o controle da barreira, preservação das decisões, contestação, atualização, repetição de lote, fonte de PLN, imagens inválidas, chave de revisão e falha de serviço. Isso verifica comportamento técnico; não é teste com usuários. O registro do que efetivamente foi executado nesta máquina está em `docs/progresso.md`.

Em 14/11/2026, os 60 testes Python, 17 testes JavaScript e quatro validações PowerShell passaram. Incluem contratos móveis, reenvio, mapa, cancelamento de câmera/GPS, bloqueios sobrepostos e diagnóstico de integração. O preparador passou com os serviços ativos e após reinício controlado. A interface ZelaBairro foi verificada no desktop e em larguras de 390 e 320 pixels. Os resultados anteriores e capturas estão em [evidências da interface](docs/evidencias/zelabairro-v2-2026-11-14.md); a preparação atual está em [diagnóstico operacional](docs/evidencias/preparacao-operacional-2026-11-14.json). Isso não equivale a teste em smartphone físico.

Em 15/11/2026, a ampliação Passagem Livre passou em 71 testes Python, 19 JavaScript e nas quatro validações PowerShell. As sete verificações atuais do preparador também passaram, incluindo execução de RPA, PLN, Visão e Generative AI. O navegador conferiu reparo isolado/conjunto, revisão, plano, contestação, incerteza coexistente, preservação de foco e cadastro móvel com foto do acervo, ponto manual e rascunho. A base principal conservou os quatro pedidos anteriores e recebeu dois casos fictícios de preparação. Evidência: [Passagem Livre](docs/evidencias/passagem-livre-2026-11-15.md). Relatório de trabalho: 14 páginas; roteiro: 6min30s. Conclusão conjunta e links finais seguem pendentes.

Uma consulta real anterior de Generative AI pela central retornou orientação com fonte oficial; a evidência está em docs/evidencias/execucao-http-genai-2026-11-14.json. Como verificação complementar, `python -X utf8 verificar_fluxo.py` executa as funções reais das rotas e a persistência em bancos temporários; esse percurso também passou. O fluxo de cadastro, revisão, confirmação no ZelaBairro e contestação foi executado e repetido pela interface. O teste também conferiu o histórico, o bloqueio de confirmação sem revisão, a preservação de rascunho e a repetição da confirmação sem duplicação por versão. Evidências anteriores: docs/evidencias/fluxo-browser-2026-11-14.json e docs/evidencias/fluxo-persistencia-2026-11-14.json.

A ampliação móvel, o teste de resposta perdida e as verificações do formulário sem servidor estão em `docs/evidencias/mobile-2026-11-14.json`. A sonda de falha é `tests/tools/proxy-resposta-perdida.mjs`: aponta somente à prévia local em 8841 e usa 8842, sem interferir na instância principal.

## Limites para uso fora da demonstração

Esta demonstração não possui contas individuais ou isolamento entre solicitantes. A entrada online é pública, sem usuário e senha; os pedidos e fotos podem ser consultados pelo link. Revisão, confirmação, lotes e planos continuam exigindo a chave de gestão. Para operar com pessoas reais, ainda seria necessário definir contas e permissões por solicitante, responsáveis, retenção dos dados e acordos com quem recebe os pedidos.

O relatório e o roteiro da entrega ficam em `docs/`. A conclusão será elaborada com os integrantes. O link do vídeo final não listado depende da publicação; os vídeos de módulos anteriores não substituem a gravação integrada de 5 a 7 minutos. Repositório da entrega: [GOV_GS_26.2](https://github.com/luizhenriqueposs7/GOV_GS_26.2).
