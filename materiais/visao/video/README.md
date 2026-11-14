# Apresentação completa do CitizenTech

A narração original está em narracao_original.ogg. As entradas em roteiro_visual.json usam os tempos da fala em segundos. As telas são renderizadas a partir dos dados e do código da entrega por montar.py. A captura contínua do navegador está em captura_completa.webm.

Para preparar as telas no Windows, execute python video/montar.py na raiz do projeto. O script utiliza Pillow e as fontes Segoe UI e Consolas.

Para refazer a captura, inicie a aplicação com python app.py em 127.0.0.1:8765 e sirva esta pasta com python -m http.server 8766 --bind 127.0.0.1 --directory video. O script gravar.cjs utiliza Playwright e recebe CV_PLAYWRIGHT, CV_CHROME e CV_PROJETO no ambiente. Ele grava a navegação e a inferência dos arquivos durante a apresentação.

Para exportar, execute python video/montar.py --exportar C:\caminho\para\ffmpeg.exe. A narração é utilizada integralmente a 1,0×, com redução de 2,5 dB no volume para dar margem aos picos. A gravação da execução também permanece a 1,0×.

O arquivo edicao.json registra o intervalo de quadros utilizado. A montagem encerra após a fala e a tela de encerramento previstas no roteiro, em aproximadamente 457,12 segundos.
