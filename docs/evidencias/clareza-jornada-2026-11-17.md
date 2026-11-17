# Reorganização da jornada

Versão preparada: 0.6.3; cache v22. Objetivo: reduzir informação simultânea e explicar registro, conferência, encaminhamento e acompanhamento sem alterar o domínio.

## Alterações

Menu principal com Registrar, Pedidos, Mapa, Gestão e Projeto. Entrada em Registrar em qualquer largura. Passagem Livre passa à navegação do Mapa; planejamento/lote à Gestão; consultas e IoT ao Projeto. Os hashes anteriores continuam válidos.

Consultas abrem individualmente. Os nove trabalhos e a importação CSV começam recolhidos. O detalhe destaca relato/foto e destino, conservando dados técnicos, ficha, protocolo, contestação e histórico em detalhes acessíveis. A revisão mostra pedido e decisão em duas colunas no desktop, com histórico recolhido abaixo. As restrições e confirmações continuam explícitas.

O atalho de Cluster reutiliza a mesma abertura de lote da Gestão. O botão do mapa passou a dizer Acompanhar pedido, correspondendo ao destino. A cópia de orientação de câmera foi reduzida após inspeção visual, evitando sobreposição de texto com a legenda.

## Conferência

- Teste de navegação falhou antes da implementação e passou em Chrome e WebKit após a mudança. Verifica entrada, cinco destinos, seleção contextual, abertura exclusiva das consultas, nove trabalhos, ambos os atalhos de lote, hash Passagem Livre e preservação do texto do pedido.
- Ciclo completo com foto, localização, prévia, envio, revisão, confirmação, protocolo SIM, retorno/foto posterior, conferência, contestação e persistência passou nos dois motores, com sete eventos no histórico e nenhuma exceção JavaScript. Foram usados modelo/GPS controlados e base isolada de QA.
- CSV com 2/4 workers preservou oito IDs; comparação fila/exato/QAOA e registro do plano passaram, sem decidir revisões automaticamente.
- WebKit: 32 combinações de oito telas com larguras 320, 390, 768 e 844 px, incluindo paisagem. Sem overflow horizontal ou campos de texto visíveis abaixo de 16 px. Menu móvel em 12,8 px.
- 34 testes JavaScript e 192 Python, incluindo PostgreSQL temporário, passaram. Revisão independente conferiu callers, IDs e formulários; os dois atalhos apontados foram corrigidos.

O teste `tests/navegacao.browser.js` usa Playwright CLI, em origem local 127.0.0.1. O código do teste não importa lotes nem decide pedidos. Os cenários extensos permanecem na pasta temporária de QA.

Na conferência dos 30 itens do manifesto, foi identificado que o vídeo original de Frontend estava excluído por uma regra de `.gitignore` herdada. Foi acrescentada exceção apenas para esse arquivo, sem alterar seu hash. Ele continua excluído do pacote de função Vercel e não substitui o vídeo integrado de Governança.

Os roteiros individuais têm falas/ações e a montagem de 6min30s, cobrindo nove disciplinas. O vídeo ainda precisa ser gravado e medido; câmera/GPS físicos, IoT real e validação em campo não foram demonstrados por esses testes. A conclusão do relatório permanece para redação conjunta.
