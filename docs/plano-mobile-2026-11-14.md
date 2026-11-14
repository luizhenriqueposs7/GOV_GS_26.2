# Ampliação móvel da Central CitizenTech

Autorização: em 14/11, o grupo escolheu ampliar o protótipo antes da entrega de 16/11. A conclusão será feita em conjunto depois da verificação.

## Resultado esperado

Uma aplicação web que funcione em tela de celular, reúna foto opcional, descrição e localização confirmada no mesmo pedido e conserve revisão, confirmação local no ZelaBairro e contestação. A foto é evidência; o modelo de fissuras não será apresentado como detector de buracos. Câmera e GPS terão alternativas manuais. O protótipo continua destinado a dados fictícios.

## Escopo e interfaces

1. Backend: aceitar foto JPEG/PNG no cadastro e na edição; normalizar orientação, retirar metadados, limitar tamanho e guardar por hash. Coordenadas opcionais exigem confirmação. Reenvio do mesmo identificador de envio não duplica o pedido; reutilização com conteúdo diferente gera conflito. Preservar contratos JSON existentes, enriquecimentos em reimportação de RPA e histórico de versões. Arquivos não usam nomes enviados pelo cliente.
2. Interface: foto da câmera ou galeria com prévia e remoção; coordenadas digitadas ou obtidas com permissão, sempre confirmadas; referência de endereço continua necessária. Rascunho salvo explicitamente no aparelho, sem chave de gestão e sem envio automático. Instalação como PWA e abertura do formulário sem rede; APIs, fotos e respostas não entram no cache do service worker.
3. Verificação: testes de contrato e persistência, navegador em tela estreita, cadastro com imagem, revisão, confirmação local, edição e contestação. Documentar o que foi executado e as limitações. Revisão independente única ao final.

Alterações alcançam central/app.py, registros.py, utilitário de imagens, catálogo, web/index.html, app.js, style.css, novos recursos PWA, testes e documentação. Não mudam os materiais originais das disciplinas.

## Decisões

- Reaproveitar FastAPI e JavaScript existentes; não criar aplicativos nativos separados.
- Não consultar geocodificador externo nesta versão. GPS fornece coordenadas, não prova o endereço da ocorrência. O usuário confere o ponto e informa a referência. Isso evita enviar a posição a um terceiro.
- HTTPS e aparelho real são necessários para comprovar câmera/GPS e instalação no celular. Acesso público não está autorizado por esta ampliação; nenhuma porta ou túnel será exposto nesta etapa.
- Trabalho no checkout existente da branch codex/central-citizentech, com commits locais e servidor de conferência separado. Evita copiar o acervo de 370 MB e preserva os dados da execução anterior.
- Sem teste com pessoas ou piloto, conforme decisão anterior do grupo. Não declarar conformidade integral de acessibilidade.

## Registro de execução

- Planejamento: contratos existentes inspecionados. Base anterior: 44 testes aprovados e fluxo completo técnico executado. Interfaces compartilhadas: foto/posição precisam sobreviver à edição e à reimportação; a revisão lê os mesmos dados do acompanhamento.
- Tarefa 1: concluída — contratos, imagem, persistência e catálogo; regressão Python com 55 testes aprovada.
- Tarefa 2: concluída — jornada móvel, rascunho e PWA; 7 testes JavaScript aprovados.
- Tarefa 3: concluída — fluxo principal com foto, coordenadas fictícias, edição, revisão, ZelaBairro e contestação no navegador; reenvio após resposta descartada; rascunho independente preservado; formulário e rascunho com servidor desligado. Relatório conferido em 14 páginas.

Fontes consultadas: [geolocalização no navegador](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation), [carta Tapa-buraco SP156, serviço 952](https://sp156.prefeitura.sp.gov.br/portal/servicos/informacao?servico=952), [formulários acessíveis W3C WAI](https://www.w3.org/WAI/tutorials/forms/). A carta 952 diferencia faixa exclusiva/corredor de ônibus e exige endereço completo e descrição; o protótipo não substitui esse formulário oficial.

## Revisão independente e correções

Uma revisão independente, somente leitura, examinou a diferença desde af87d8e. Quatro achados foram tratados na mesma passagem: (1) identificador e metadados GPS do rascunho não persistiam antes da tentativa; (2) seleção tardia da foto podia desfazer remoção/cancelamento; (3) outro cadastro apagava o rascunho salvo; (4) rede e cache podiam fornecer versões diferentes dos arquivos.

A tentativa agora atualiza atomicamente seu rascunho antes do POST; foto bloqueia os controles durante a preparação; exclusão automática compara a identidade do rascunho em transação; o service worker usa o conjunto estático da mesma versão. Testes de controle assíncrono, metadados, identidade e queda parcial de rede passaram. O descarte real da primeira resposta pelo proxy local foi seguido de recuperação e reenvio: mesmo UUID, um registro e um evento. A reprodução de exclusão indevida foi observada no navegador antes da correção; depois, A foi recuperado após enviar B.

Na conferência, também foi corrigido o detalhe que podia ser substituído durante o início da contestação e o texto do botão que ainda indicava atualização após concluir uma edição. A versão principal preservou o texto digitado e voltou a oferecer novo cadastro.

Nenhum achado menor foi deixado pendente nessa revisão. Câmera/GPS reais, instalação no aparelho, acesso HTTPS e testes com pessoas não foram verificados; os dois últimos dependem de outra etapa e o teste com pessoas foi descartado pelo grupo. A conclusão permanece conjunta.
