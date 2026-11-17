# OuviAí: áudio no navegador

Pedido: resolver a ausência de áudio e de reconhecimento na estação conceitual. A tela atual apenas injeta eventos fictícios. O ZIP de IoT e os links do DOCX contêm relatório e vídeos, sem exportação ou link de execução do modelo original ZoomKaiseR-project-1. O link foi solicitado ao integrante.

Decisão de implementação: manter a estação visual e adicionar escuta iniciada pelo usuário, classificação local e parada explícita/automática. Usar provisoriamente YAMNet via MediaPipe, hospedado junto dos arquivos estáticos e identificado como modelo alternativo. Não atribuir seus resultados à CNN do trabalho. O modelo original permanece execução externa pendente de integração. Substituição futura exige o artefato original e testes de paridade.

Alternativas: somente reproduzir sons continuaria sem reconhecer; depender do export original bloquearia todo teste de áudio; classificar no servidor transmitiria áudio sem necessidade. A escolha acima é do implementador, reversível e sem serviço pago.

Fluxo: usuário ativa microfone em HTTPS, navegador pede permissão, analisa janelas mono, exibe possível campainha/batida ou resultado inconclusivo. Pontuação é saída do modelo, não acurácia. Limiar inicial experimental e intervalo entre alertas limitam repetição. Sem disparar chamados municipais. Somente eventos ficam na memória da aba. A fonte real é diferenciada de simulação manual. Ao sair da seção, ocultar a página, parar ou falhar, encerrar tracks, contexto e worker; cancelar também permissões tardias. Sem gravação ou envio de áudio.

Alcance: módulo de áudio, worklet/worker, assets e licenças, HTML/CSS, navegação, CSP restrita a WebAssembly, SW, catálogo de integração, roteiro IoT e orientações de teste. Preservar pedidos existentes e APIs. Testar classificação com arquivos conhecidos, lifecycle/negativa de permissão, Chrome e WebKit. Teste físico do celular permanece com o grupo. Não instalar estação fixa nem prometer alertas de emergência.
