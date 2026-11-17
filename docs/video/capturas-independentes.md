# Capturas independentes e narrações

Foram gravadas seis fontes brutas em 17/11/2026: abertura, Cluster, Generative AI, PLN, Visão e OuviAí. São arquivos WebM nativos em 1920 × 1080, a 25 fps, sem narração e sem retimar a gravação. As fontes somam 182,80 segundos; não constituem o vídeo final.

| Arquivo em output/video/fontes_independentes | Duração | Ambiente e alcance |
| --- | --- | --- |
| 00_abertura.webm | 15,88 s | Entrada da central oficial, sem criar pedido. |
| 03_cluster_2_4_workers.webm | 27,52 s | Pipeline real em base local de QA isolada, com threads e CSV fictício. Não é execução HTTP na Vercel. |
| 05_generative_ai.webm | 45,52 s | Consulta oficial atual, resposta e fonte, sem vínculo com pedido. |
| 06_pln.webm | 32,40 s | Busca oficial no corpus, com origem, sem vínculo com pedido. |
| 07_visao_computacional.webm | 28,80 s | Inferência oficial sobre recorte do acervo original, sem vínculo com pedido. |
| 08_iot_ouviai_simulacao.webm | 32,68 s | Interface oficial, com eventos explicitamente simulados; sem hardware/modelo de áudio conectado. |

O manifesto registra origem, parâmetros e resultados reais de cada cena. Todos os quadros foram decodificados pela verificação automatizada, além da inspeção de amostras visuais. Não houve substituição de respostas de API por mocks nos endpoints filmados.

A gravação do Cluster foi isolada em QA local para evitar criar ou alterar registros na implantação oficial, e a fala identifica esse ambiente. Os demais clipes usam consultas sem vínculo e não alteram pedidos oficiais.

## Arquivos para compartilhar

- Capturas: `output/video/Capturas_independentes_ZelaBairro.zip`, com seis vídeos, manifesto, verificação e instruções.
- Roteiros: `output/video/roteiros_individuais/Roteiros_para_os_tres_integrantes.zip`, com um PDF e um TXT de falas para cada integrante.
- PDFs individuais: Luiz Henrique (RM562177), Luis Filipe (RM564706) e Felipe (RM563380), com a divisão de disciplinas solicitada.

Os PDFs reúnem falas e contexto de tela. Os TXT reúnem apenas as falas, horários e nomes sugeridos dos arquivos de áudio. Gravar um áudio por cena, no ritmo natural, sem ler títulos ou instruções.

## O que falta para a montagem

Luiz enviará o vídeo original do celular, desde foto/GPS até conferência, envio e recibo/ID. Deixar o pedido aguardando revisão. Com esse ID serão gravados RPA do mesmo pedido, planejamento que o inclua, Governança, contestação e histórico. Assim a continuidade não será simulada com outro registro.

Depois de receber os áudios e a gravação do celular, alinhar voz, ações e resultados. A duração final deve ser medida entre 5 e 7 minutos. Cortes na espera devem manter ordem e contexto; não acelerar falas, inventar execução ou apresentar outra foto como reparo real.

As consultas já capturadas estão sem vínculo. Se uma delas for pertinente ao pedido real, executar e vincular a consulta na etapa posterior. A captura independente não deve ser apresentada como prova de um vínculo que ainda não foi feito.

## Reproduzir

`scripts/video/gravar_independentes.py` usa Playwright CLI e Chrome. A captura do Cluster requer o QA local em 127.0.0.1:8851 com a chave sintética; não lê a chave de produção. `--resume` preserva tomadas concluídas. Os caminhos dos binários documentam a instalação desta máquina e devem ser ajustados em outra.

`scripts/video/gerar_roteiros.py` gera PDFs/TXT a partir dos Markdown individuais. Usa ReportLab, PyMuPDF e Pillow já disponíveis no ambiente de documentos. `scripts/video/verificar_e_empacotar.py` usa OpenCV para decodificar as fontes e criar o pacote. Os arquivos de trabalho e contatos de revisão ficam em .tmp, fora do Git.
