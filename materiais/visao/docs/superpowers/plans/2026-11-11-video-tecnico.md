# Vídeo técnico CitizenTech Implementation Plan

> Execução nesta sessão, preservando a narração original e os arquivos da apresentação anterior.

**Goal:** Entregar um MP4 técnico de aproximadamente 7min37s com o áudio do usuário, código real, resultados verificáveis e inferência real no CitizenTech.

**Architecture:** Um visualizador local mostra os arquivos originais sem modificá-los e transmite a saída de comandos Python permitidos. Playwright grava a navegação e a aplicação real em tempo contínuo; Python/FFmpeg combina a captura com a narração original a 1,0×.

**Tech Stack:** Python, Flask, PyTorch existente, Playwright existente, FFmpeg existente.

**Spec:** Proposta aceita na conversa: dados → modelo → avaliação → CitizenTech funcionando → desempenho e limitações. Áudio original integral, sem voz sintética ou aceleração.

## Global Constraints

- Preservar a entrega e o vídeo anteriores; saída nova Apresentacao_Tecnica_CitizenTech.mp4.
- Mostrar código e dados reais. A saída do terminal deve vir de processos executados, com falhas visíveis e verificadas.
- A inferência da demonstração deve ocorrer durante a gravação, incluindo atualização por quadro.
- Não publicar nem alterar o vídeo do YouTube.

## Review Focus

- Legibilidade do código na resolução exportada.
- Sincronização entre a fala e o arquivo exibido.
- Metadados de execução separados dos experimentos históricos.
- Continuidade do áudio original e da execução real, ambos a 1,0×.
- Ausência de recortes de tela vazios, comandos com falha e dados privados.

## Tasks

- [x] Preparar video/tecnico/conferir.py, servidor.py e index.html usando os arquivos do projeto; validar as contagens e métricas por execução real. Os tempos ficam em gravar.cjs e gravacao.json.
- [x] Gravar a navegação técnica e a inferência real; verificar erros de página, comandos concluídos e 180 atualizações do vídeo.
- [x] Exportar em H.264/AAC com a narração integral; conferir decodificação, duração, amostras de áudio e trechos visuais.
- [x] Documentar a reprodução e apontar o novo vídeo no README.

## Registro

- Autorização: pedido explícito do usuário para produzir o vídeo proposto usando o áudio existente.
- Escopo: novos arquivos de montagem e documentação; nenhum ajuste no modelo ou na aplicação.
- Conferência final: 457,08 s, 1440 × 900, 180 atualizações ao vivo, quatro comandos concluídos sem falha, nove amostras de áudio correlacionadas e 43 quadros comparados à captura com conversão de faixa adequada. Revisão visual de todos os capítulos, sem escuta perceptiva.
