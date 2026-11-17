# OuviAí com áudio local

A estação passou a captar o microfone do celular ou computador e a transformar classificações em avisos visuais. A pessoa autoriza a escuta e pode pará-la. A navegação para outra seção, página oculta, microfone desconectado e falhas de captura/modelo encerram tracks, contexto de áudio e worker. Nenhum áudio é enviado, gravado ou incluído em pedidos. O diário conserva oito mudanças/avisos na memória da aba e identifica a origem. A simulação manual fica em uma seção separada e desliga a escuta.

## Modelo e alcance da integração

O relatório e o ZIP originais contêm evidências do Edge Impulse, sem pesos, WebAssembly ou link de execução. Os quatro links do DOCX são vídeos. O integrante informou não conseguir fornecer o projeto. Portanto, a CNN original continua externa. A ampliação usa **YAMNet float32 v1, via MediaPipe Tasks Audio 1.2.3**, explicitamente identificado como modelo alternativo. Os arquivos oficiais, licença Apache-2.0 e hashes estão em `public/ouviai/manifesto.json`. A Vercel serve essa pasta pela CDN, sem passar o WASM de 22 MB pela função Python; localmente há montagem estática equivalente. Os assets públicos têm cache de um dia. Nenhum dado pessoal recebe esse cache.

Referências de implementação: [MediaPipe Audio Classifier](https://developers.google.com/edge/mediapipe/solutions/audio/audio_classifier?tab=Web), [YAMNet](https://www.tensorflow.org/hub/tutorials/yamnet) e [arquivos estáticos do FastAPI na Vercel](https://vercel.com/docs/frameworks/backend/fastapi).

## Como testar

1. Abra `https://gov262.vercel.app/#ouviai` em Chrome ou Safari atualizado, em primeiro plano. Atualize/reabra se o aplicativo instalado ainda mostrar só simulação.
2. Use Wi-Fi para o primeiro carregamento, cerca de 27 MB. Toque em Ativar microfone e permita o acesso.
3. Aguarde Escutando. Bata na porta próxima ao aparelho ou toque uma campainha. O resultado deve corresponder ao que o modelo realmente retornar; não use botões de simulação como prova de reconhecimento.
4. Confira texto, luz e origem Microfone · YAMNet no diário. Pare a escuta. Ative outra vez e saia para Pedidos; o indicador de uso do microfone deve cessar.

Não há emissão automática de som: a entrada é o som ambiente; a saída principal é texto/luz, voltada à acessibilidade auditiva. Não há estação fixa nem comunicação entre aparelhos.

## Regras iniciais, sem calibração de campo

O AudioWorklet fornece janelas mono de dois segundos, com passo de um segundo. O worker executa a inferência sem bloquear a interface. O runtime recebe a taxa real do AudioContext e prepara a entrada do modelo. Todas as categorias são consideradas, pois YAMNet é multirrótulo. Doorbell/Ding-dong correspondem a possível campainha e Knock a possível batida. Um aviso exige score mínimo 0,60 e margem de 0,15 contra o outro tipo de aviso, inclusive rivais abaixo do limiar. Door e Knock simultâneos não se anulam. Outros sons não viram avisos de campainha ou porta.

O aviso permanece visível por pelo menos quatro segundos; o mesmo tipo de aviso repete no máximo a cada sete segundos. Os parâmetros são experimentais. Pontuação não é acurácia nem probabilidade calibrada. As métricas 78/100 e 14/15 do trabalho original não avaliam YAMNet.

## Verificações

- Classificação real de arquivos no navegador: batida e campainha geraram os avisos correspondentes; cachorro e silêncio não geraram esses avisos. São quatro entradas controladas, sem amostragem independente, avaliação de campo ou estimativa de acurácia.
- Chrome com WAV de batida fornecido como microfone virtual: entrada passou por getUserMedia, AudioContext, AudioWorklet e worker reais; a tela exibiu possível batida e ativou a luz. Nenhuma resposta do modelo foi mockada.
- Parar, reativar e navegar: tracks terminaram e contextos fecharam. Nenhum POST/PUT ou upload durante o teste. Larguras de 360, 390, 768 e 1440 px sem overflow horizontal.
- Testes unitários cobrem categorias simultâneas, ambiguidade, score inválido, janelas, permissão negada, autorização tardia e erro do processador antes da primeira janela.
- Suíte final: 193 testes Python com PostgreSQL temporário e 41 testes JavaScript passaram. Relatório manteve 14 páginas; roteiro de Luis foi atualizado.
- HTTPS oficial, versão 0.6.4, commit de implementação `d234230`: modelo e runtime retornaram HTTP 200 pela CDN, com MIME WASM e cache de um dia. A batida do microfone virtual gerou aviso/luz, sem uploads; Parar escuta encerrou o fluxo. Resultado detalhado em `ouviai-audio-producao-2026-11-17.json` e imagem em `output/playwright/iot-audio-mobile-oficial.png`.
- O WebKit disponibilizado nesta máquina Windows não oferece AudioContext, AudioWorklet ou getUserMedia. A interface deve informar a indisponibilidade. Isso não substitui teste físico no Safari do iPhone.

Fontes dos áudios de teste: [batida ESC-50, 1-101336-A-30.wav](https://github.com/karolpiczak/ESC-50/blob/master/audio/1-101336-A-30.wav), [cachorro ESC-50, 1-100032-A-0.wav](https://github.com/karolpiczak/ESC-50/blob/master/audio/1-100032-A-0.wav) e [Sound Of A Doorbell](https://orangefreesounds.com/sound-doorbell/). Silêncio foi um array de zeros. Arquivos de controle foram usados somente no teste local e não integram o aplicativo. A evidência JSON acompanha este documento. O teste de lifecycle é reproduzível em `tests/ouviai.browser.js` pelo Playwright CLI, com microfone virtual autorizado.

## Limitações que permanecem

Não foi construído dispositivo IoT físico. Não há validação com pessoas com deficiência auditiva, campainhas físicas variadas ou ambientes ruidosos. Navegadores e sistemas podem suspender o áudio; a escuta não continua em segundo plano e não substitui alarmes de segurança. A CNN original não foi incorporada. O modelo alternativo não detecta buracos nem determina prioridades municipais; seus eventos não abrem chamados automaticamente.
