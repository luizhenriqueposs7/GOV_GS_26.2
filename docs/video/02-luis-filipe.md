# Luis Filipe Chaves Amorim · RM564706

Seu trecho vai de 01:00 a 02:45. Aguarde o ID criado pelo Luiz e use pedidos pendentes antes de ele revisar. Use os tópicos como lembrete, sem ler blocos na gravação.

## 01:00–01:55 · RPA e Cluster

**Preparação:** separar `docs/exemplos/cluster-revisoes.csv`. A chave é digitada na Gestão, sem mostrar seu arquivo.

**Ações:** Gestão → Importar lote. Selecionar CSV, escolher 2 workers, executar e mostrar aceitos/rejeitados, IDs e tempos. Repetir com 4 e conferir IDs. Usar a triagem de um caso para explicar categoria/prioridade quando necessário. As duas execuções devem ser atuais, com cortes identificados nas esperas.

**Fala base:** “O RPA reaproveita o pipeline do trabalho original para validar o CSV e fazer a triagem. O Cluster distribui o lote entre dois ou quatro workers lógicos, mantendo o mesmo ID no mesmo worker. Depois, a central valida e grava o conjunto. Aqui estão os resultados e os tempos desta execução. Isso não comprova máquinas físicas distintas nem que quatro workers sempre sejam mais rápidos.”

Não comparar a latência da Vercel diretamente com os 49,72% históricos do iSPD. A confiança heurística do RPA não é probabilidade de acerto. Reimportar o mesmo CSV preserva IDs; mudar descrição/bairro invalida revisões anteriores.

## 01:55–02:45 · Computação Quântica

**Ações:** Gestão → Planejar revisões. Selecionar o pedido móvel e mais dois pendentes. Conferir prioridades, estimar 10 minutos por pedido e 20 minutos de capacidade. Marcar um obrigatório, comparar e mostrar selecionados/adiados. Escolher método, informar responsável/justificativa, confirmar e registrar plano. Mostrar que o pedido continua exigindo revisão.

**Fala base:** “Com a fila disponível, escolhemos o que cabe nesta rodada. As prioridades e os minutos são conferidos pelo responsável, não estimados automaticamente pela IA. Comparamos a fila, a solução exata e QAOA em simulador. O gestor vê também os casos adiados e justifica a escolha. O plano organiza a revisão, mas não aprova os pedidos. Esta execução usa CPU; não demonstramos vantagem quântica.”

Não prometer empate com a referência nem benefício 5 sem conferir o resultado atual. Trocar método exige conferir e confirmar novamente. Se um pedido mudar durante a cena, atualize e recalcule.

**Passagem:** “O pedido continua aguardando revisão. Agora vamos mostrar as ferramentas que ajudam a conferir o contexto.”

Inclua a passagem no tempo reservado, sem longa apresentação de código.
