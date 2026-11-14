# Apresentação técnica

Vídeo oficial da entrega: [YouTube](https://youtu.be/zPO3fmRpRLA).

Saída: `../../Apresentacao_Tecnica_CitizenTech.mp4`.

A narração é o arquivo original `../narracao_original.ogg`, integral e a 1,0×, com ganho de -2,5 dB. Não há voz sintética. A captura também permanece a 1,0×.

O visualizador local lê os arquivos reais do projeto, destaca os trechos de código e mostra imagens e tabelas dos manifestos. O terminal transmite a saída dos processos Python executados durante a gravação. A aplicação CitizenTech é acessada diretamente em 127.0.0.1:8765, com inferência por quadro e atualização real da interface.

As métricas do teste principal e dos recortes sutis são recalculadas na gravação e comparadas aos registros da entrega. Os números de FPS da comparação entre resoluções são os experimentos anteriores de cinco repetições; essa origem aparece na tela. O FPS mostrado pela aplicação corresponde à nova execução gravada.

## Reproduzir

Dependências da aplicação, mais Pygments e Playwright para a montagem. FFmpeg é localizado pelo pacote imageio-ffmpeg já usado nesta edição. A aplicação não depende do visualizador para funcionar.

1. Na raiz do projeto, iniciar `python app.py`.
2. Em outro terminal, iniciar `python video/tecnico/servidor.py`.
3. Configurar `CV_PLAYWRIGHT` com o caminho do módulo Playwright, `CV_CHROME` com o executável do navegador e `PLAYWRIGHT_BROWSERS_PATH` com a pasta que contém o FFmpeg do Playwright.
4. Executar `node video/tecnico/gravar.cjs`. A opção `--testar` confere as telas rapidamente, sem gravar o vídeo nem executar os comandos de avaliação.
5. Executar `python video/tecnico/exportar.py` e depois `python video/tecnico/exportar.py --verificar`.

O exportador exige que o MP4 de destino ainda não exista. Para uma nova revisão, preserve o anterior com outro nome antes de exportar.

## Evidências

- `captura_tecnica.webm`: gravação contínua original.
- `gravacao.json`: tempos previstos e reais, saída dos quatro comandos e contagem de atualizações.
- `resultados/`: saídas recalculadas.
- `edicao.json`: intervalo de quadros, áudio, ganho e velocidade.
- `verificacao.json`: duração, correlação do áudio, comparação de quadros e decodificação.

A revisão técnica confere imagens, transcrição e medições. Não equivale a uma escuta perceptiva da narração.
