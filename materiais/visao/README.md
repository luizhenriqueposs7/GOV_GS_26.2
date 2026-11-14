# CitizenTech · Visão Computacional para Manutenção Urbana

**Global Solution 2026.2 · FIAP**

- Luiz Henrique Poss · RM562177
- Luis Filipe Chaves Amorim · RM564706
- Felipe Stefani Honorato · RM563380

O módulo classifica recortes de concreto com e sem fissura e sinaliza os casos que merecem inspeção humana. A interface mostra a imagem analisada, o escore de fissura e a confiança da classe exibida. A análise serve para triagem. A gravidade do dano e a segurança estrutural dependem de inspeção profissional.

A apresentação recomendada para esta entrega está em `Apresentacao_Tecnica_CitizenTech.mp4`. Ela acompanha a narração original de aproximadamente 7min37s, mostra o código, a auditoria dos dados, a avaliação recalculada e a execução real do CitizenTech. A pasta `video/tecnico/` contém a captura contínua e os arquivos da montagem.

A versão anterior permanece em `Apresentacao_Completa_CitizenTech.mp4`, com seus arquivos na pasta `video/`.

O vídeo oficial da entrega está no [YouTube](https://youtu.be/zPO3fmRpRLA).

## Apresentação técnica

O código, os resultados e as imagens apresentados são lidos dos arquivos reais da entrega. O terminal executa as verificações durante a gravação. A documentação para reproduzir a montagem está em `video/tecnico/README.md`.

## Executar no Windows

Na pasta que contém este README, com Python 3.13 x64, execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abra [CitizenTech](http://127.0.0.1:8765) e selecione **Inspeção visual**. Envie uma foto, uma sequência de até 24 imagens ou um vídeo curto de até 180 quadros. Durante a execução, a interface mostra o quadro atual, a classificação, a confiança e a contagem processada. Use `demo/monitoramento_ao_vivo.mp4`, com 180 quadros, para acompanhar esse fluxo. Os pesos já estão em `artifacts/`. O assistente de texto pode ser iniciado com `Executar-CitizenTech.ps1` em um ambiente que também tenha o motor de linguagem configurado. A página de inspeção visual funciona sem esse motor.

## Reproduzir os dados e o treino

O [Concrete Crack Segmentation Dataset](https://doi.org/10.17632/jwsn7tfbrp.1) de Çağlar Fırat Özgenel (CC BY 4.0) disponibiliza as fotos e máscaras que deram origem ao [Concrete Crack Images for Classification](https://doi.org/10.17632/5y9wdsg2zt.1). As imagens distribuídas nesta entrega são recortes dessas fotos. Os originais permanecem disponíveis no Mendeley Data.

Para usar a amostra já preparada:

```powershell
.\.venv\Scripts\python.exe -B train.py --saida artifacts_reproduzidos
.\.venv\Scripts\python.exe -B -m unittest discover
```

Para regenerar a amostra, baixe e extraia o arquivo oficial `concreteCrackSegmentationDataset.rar`. A soma SHA-256 publicada é `1b8458ab6f84dc5086e9af8579e2cabccd3d209df97b46622096a4c105d5a6b2`.

```powershell
.\.venv\Scripts\python.exe dados.py C:\caminho\para\originais --saida data_reproduzida
.\.venv\Scripts\python.exe train.py --dados data_reproduzida --saida artifacts_reproduzidos
```

A pasta de entrada deve conter `rgb/` e `BW/`. O treino usa CPU e baixa a ResNet18 ImageNet no primeiro uso. Para execução offline, informe o caminho do arquivo oficial de pesos com `--pesos-imagenet`.

`data/manifesto.csv` identifica a foto original, o conjunto, as coordenadas do recorte, a classe, a contagem de pixels da máscara e o hash do RGB decodificado. `train.py` valida os hashes dos JPEGs e recusa origens ou pixels compartilhados entre treino, validação e teste antes de ajustar o modelo. As previsões individuais estão em `artifacts/previsoes_teste.csv`.

## Comparar as resoluções e inspecionar os erros

```powershell
.\.venv\Scripts\python.exe -B train.py --resolucao 224 --saida artifacts_reproduzidos_224
.\.venv\Scripts\python.exe -B experimentos.py
```

A aplicação usa o checkpoint de 160 × 160. O de 224 × 224 está em `artifacts/resolucao_224/`. A comparação usa as mesmas fotos, recortes e configuração de treino. A época e o limiar de cada modelo foram escolhidos na validação. O teste compara as duas configurações fixadas.

`experimentos.py` usa os checkpoints entregues para avaliar os recortes sutis em `data/sutis/` e medir os dois clipes de `demo/`. Registra cinco execuções por clipe e resolução, após aquecimento, em `artifacts/experimentos.json`. Se a pasta `data/sutis/` estiver ausente, acrescente `--originais C:\caminho\para\originais` para regenerá-la a partir das máscaras. Os clipes simulam monitoramento com recortes do teste.

`artifacts/analise_erros.csv` descreve os 13 erros do modelo de 160 × 160 e registra a previsão correspondente a 224 × 224. O relatório em PDF reúne a comparação e exemplos visuais. As apresentações incluem o envio de duas fotos e a inferência dos 180 quadros de um vídeo. Nesse modo, o tempo exibido também inclui a transmissão das prévias para o navegador.

## Limitações

Os testes usam fotografias do mesmo acervo. Outros locais, câmeras e condições de iluminação ainda precisam de avaliação.

Nos 26 recortes complementares com apenas 1 a 31 pixels marcados na máscara, cada modelo sinalizou 2 exemplos. Fragmentos mínimos e sinais pouco contrastados podem passar sem sinalização.

A classificação apoia a triagem para inspeção humana. A presença de fissura isoladamente não determina a gravidade do dano nem a segurança estrutural.
