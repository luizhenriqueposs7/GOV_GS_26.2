# Cluster e Quântica — 17/11/2026

## Origem e ampliação

Cluster reutiliza o pipeline RPA entregue e adapta o Round Robin com 2/4 workers do relatório e modelos iSPD. Originais permanecem intactos. O experimento iSPD de 12.000 relatos é hipotético; a importação com workers limita a persistência a 50 registros aceitos/1 MiB. O helper de processamento aceita até 1.000 registros e rejeita excesso; não representa a escala operacional da hospedagem.

O material de Quântica (páginas 4–5) propõe otimização da revisão com revisor e horário. A implementação nova é um recorte explícito: seleção de até oito casos, pesos informados pelo gestor, minutos estimados e capacidade. Não executa o modelo completo de agenda. Mantém referência por prioridade/antiguidade, referência exata e QAOA p=1 simulado, conforme a [definição original do algoritmo](https://arxiv.org/abs/1411.4028).

## Execução de Cluster

Cada ID é atribuído ao mesmo worker para preservar a primeira ocorrência válida e a deduplicação. Zeros iniciais e rejeitados mantêm o contrato original. Respostas são conferidas por execução, worker, hash, conteúdo esperado e contagens. O booleano review_required é convertido estritamente; a central utiliza a análise do worker, sem substituí-la por outra triagem serial.

Todos os workers terminam antes da persistência. Qualquer falha impede resultados parciais. O banco grava a importação e as evidências em uma transação, com rollback comprovado em SQLite e PostgreSQL. Reaplicações conservam complementos/revisão quando a origem não muda. Campos ou classificações do CSV não podem forjar a análise original.

Localmente são threads. Na Vercel, requisições HTTPS concorrentes ao endpoint fixo /api/cluster/worker, autenticadas com a chave de gestão mantida no servidor. Nenhum cliente escolhe URL de destino. UUID da instância identifica processo; não comprova máquinas físicas diferentes. O modo com workers mede coordenação/RPA, gravação e total; não promete reproduzir a redução de 49,72% do iSPD.

## Execução do planejamento

Energia diagonal: menos benefício dos selecionados, acrescido de penalidade por excesso de capacidade e omissão de obrigatórios. Penalidade maior que a soma dos benefícios. Essa função não é apresentada como QUBO. O estado começa uniforme; aplica-se fase de custo e mixer Rx em cada qubit. Uma grade clássica de 12 × 12 ajusta gamma e beta. São no máximo 256 amplitudes.

O candidato QAOA é o estado factível de maior probabilidade após o ajuste. A referência exata não participa dessa escolha. Probabilidades são calculadas do vetor de estado, sem shots ou medições de QPU. A solução pode ser inferior à referência ou até vazia; método vazio não pode ser aprovado. A insuficiência para obrigatórios gera erro explícito.

O servidor usa pedidos reais pendentes, ignora scores/probabilidades fornecidos pelo cliente, recomputa o resultado ao aprovar e compara o snapshot. Alteração, revisão ou contestação exige recalcular. A decisão registra método, estimativas, parâmetros, recorte, adiados, snapshot e justificativa nos casos considerados; não aprova pedidos nem modifica sua prioridade. Os casos escolhidos são exibidos por prioridade/antiguidade para abrir a revisão existente.

## Verificações

Testes de domínio comparam serial/2/4, duplicatas, primeira ocorrência inválida, zeros iniciais, linha rejeitada original, CSV malformado, limites e adulteração/falha de worker. Há teste de exatamente 1 MiB sem terminador final. Matemática conferida por evolução analítica, norma, probabilidades reconstruídas, referência independente e restrições de capacidade/obrigatórios.

Navegador: desktop 1440 × 1000 e mobile 412 × 839. Importação com 2/4 preservou IDs; plano clássico selecionou dois pedidos em 20 minutos estimados, benefício experimental 5; registro preservou revisão pendente; botão abriu o pedido correto. Nenhum erro de JavaScript. Dados de demonstração, sem atendimentos reais.

Não há hardware quântico, cluster dedicado, estimativas de duração validadas em campo, integração municipal ou ganho social medido. A conclusão do relatório e o vídeo integrado continuam pendentes.

## Conferência pelo HTTPS

Na Vercel, o mesmo CSV de oito exemplos foi executado com 2 e 4 workers HTTP, preservando os IDs. Coordenação/RPA levou cerca de 397 ms e 151 ms; gravação, 14,7 s e 12,6 s; totais, 15,1 s e 12,7 s. São duas execuções com condições de inicialização diferentes, sem prova de aceleração. A medição motivou limitar a gravação a 50 aceitos por minilote, com teste de rejeição antes de qualquer persistência.

O plano QAOA considerou três casos, com 20 minutos estimados e um obrigatório. QAOA e referência exata atingiram benefício experimental 5 nesse exemplo. Houve 8 estados no simulador e cerca de 8,8 ms de cálculo QAOA. O plano foi persistido sem concluir revisões; repetição com a mesma base foi rejeitada (409). Nenhum órgão externo recebeu solicitação. Suíte final: 192 testes Python e 29 JavaScript aprovados.
