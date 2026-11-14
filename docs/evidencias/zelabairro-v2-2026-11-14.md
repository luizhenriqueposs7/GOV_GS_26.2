# ZelaBairro: visual e fluxo integrados

Implementação em 14/11/2026, após aprovação dos mockups pelo grupo. Os exemplos são fictícios. Não houve teste com pessoas ou vistoria em campo.

## Resultado

A interface usa a marca ZelaBairro, sinalização em laranja, tipografia Archivo local e uma composição centrada na tarefa. A entrada pelo celular tem foto e relato, localização e conferência. A central abre com mapa navegável e painel do pedido. A revisão apresenta evidência, sugestão original, decisão e histórico em áreas próprias.

O mapa permite clicar ou arrastar o ponto, preencher coordenadas e confirmar o local. GPS continua opcional. Alteração do ponto, edição e recuperação do rascunho exigem confirmar novamente. Não há preenchimento automático do endereço nem detector validado de buracos.

Os pedidos existentes alimentam os marcadores, a busca e os filtros. Um pedido sem ponto continua na lista. A comparação mostra relatos a até 100 m em linha reta e conserva cada registro separado. No teste, dois pedidos ficaram a aproximadamente 32 m.

## Verificação

- 57 testes Python passaram, incluindo upload, normalização da foto, coordenadas, chave de revisão, confirmação local, contestação e nova revisão.
- 12 testes Node passaram, incluindo validação de pontos, proximidade, busca/filtros, alternativa sem biblioteca de mapa, rascunho e cache estático.
- No navegador, foram concluídos dois registros: um no desktop e outro em viewport de 390 × 844. Ambos receberam foto, ponto confirmado, revisão, confirmação na persistência original do ZelaBairro e contestação.
- As contestações preservaram os eventos e retiraram a revisão e o vínculo ativo. A confirmação ficou bloqueada até nova revisão. O percurso de nova revisão também passou no teste automatizado.
- O rascunho com foto e coordenadas foi recuperado depois de recarregar a página. A confirmação do ponto não foi reaproveitada.
- Clique e arraste do marcador atualizaram as coordenadas. Arrastar retirou a confirmação anterior. A edição usada para essa conferência foi cancelada, sem gravar o ajuste.
- Todas as cinco áreas foram abertas em 320 × 844, sem rolagem horizontal. Console sem erros na conferência.
- Os dois pedidos anteriores conservaram seus históricos: sete e cinco eventos, respectivamente.

Comandos: `python -X utf8 -m unittest discover -s tests -q`; `node --test tests/mobile.test.mjs tests/sw.test.mjs tests/mapa.test.mjs`; `node --check web/app.js`; `git diff --check`.

Os testes Python sem progresso no ambiente restrito foram interrompidos e executados novamente com temporários isolados em `.tmp/unit-v2`. Essa execução terminou com os 57 testes aprovados.

## Revisão independente e correções

Uma revisão de código independente apontou dois problemas. A edição aberta a partir da última etapa podia mostrar o resumo do pedido anterior. O cenário foi reproduzido no navegador e corrigido: a edição começa na primeira etapa, com o relato e a foto do registro escolhido. A repetição passou.

Uma foto já selecionada podia ficar sobre o vídeo da câmera. A camada do vídeo foi colocada acima da foto; ao fechar, a foto permanece disponível. O estilo computado foi conferido antes e depois: vídeo de `auto` para `1`, foto em `auto`. A câmera física não foi acionada nessa validação.

A troca de pedido na revisão limpa a justificativa ainda não registrada e ajusta a prioridade ao caso escolhido. O cenário foi conferido no navegador. O atalho de teclado para pular a navegação mantém a área atual.

O redimensionamento do mapa também foi corrigido para preservar o centro ao reabrir uma área antes oculta. A conferência final verificou o marcador selecionado dentro da área visível depois de sair e voltar da revisão. A decisão anterior passou a aparecer com sua justificativa, identificada como histórica após a contestação.

## Arquivos e limites

- [Evidência dos registros pela API local](zelabairro-v2-2026-11-14.json).
- [Central com mapa](../../output/screenshots/zelabairro-central-v2.jpg).
- [Interface móvel](../../output/screenshots/zelabairro-mobile-v2.jpg).
- [Revisão e contestação](../../output/screenshots/zelabairro-revisao-v2.jpg).

Leaflet e Archivo foram incorporados com licença em `web/vendor`. Os mapas usam tiles visíveis do OpenStreetMap, com atribuição e cache normal do navegador. O service worker conserva apenas o conjunto estático local: não guarda tiles, fotos, dados da API ou chave de revisão. A área visualizada é recebida pelo provedor de mapas; os relatos e as fotos ficam na central.

Câmera ao vivo e GPS reais, instalação em smartphone, uso por pessoas e desempenho em redes móveis não foram verificados. Os testes de tamanho de tela não equivalem a teste em aparelho físico. A central continua local, sem acesso HTTPS externo publicado e sem abertura de chamado municipal.

O relatório acadêmico, a conclusão e o vídeo não foram alterados nesta implementação.
