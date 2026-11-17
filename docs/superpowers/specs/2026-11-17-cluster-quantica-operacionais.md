# Cluster e Quântica no ZelaBairro

Solicitação: dar função operacional às duas disciplinas, aproveitando os trabalhos entregues e mantendo hospedagem gratuita.

Cluster utiliza as configurações de 2/4 workers e a divisão Round Robin do iSPD para processar lotes reais pelo RPA original. IDs repetidos ficam no mesmo worker, na ordem original. Cada worker produz registros/rejeitados e medição de tempo; a coordenação só grava após todos concluírem e validarem. Na Vercel são requisições concorrentes autenticadas à própria aplicação; não há garantia de máquinas distintas ou aceleração. Localmente usa threads, identificado como tal. Máximo na importação com workers: 1 MiB/100 registros/4 workers. O módulo de cálculo aceita até 1.000 registros; a central restringe a persistência para a hospedagem gratuita. Não usar os tempos históricos iSPD como desempenho do aplicativo.

Quântica estende o estudo de revisão humana com um piloto reduzido: selecionar até oito pedidos pendentes sob capacidade em minutos, com prioridades e durações conferidas pelo gestor. Obrigatoriedade é declarada; capacidade insuficiente gera erro, sem adiamento oculto. Cada caso fica selecionado ou explicitamente na fila. Comparar fila por prioridade/antiguidade, enumeração exata e QAOA p=1 simulado com fase de custo e mixer Rx. O Hamiltoniano diagonal penaliza excesso de capacidade e omissão de obrigatórios; não afirmar QUBO, agenda completa, QPU ou vantagem quântica.

O simulador usa NumPy instalado e até 256 estados; parâmetros em grade limitada. A proposta usa o estado factível mais provável, sem apresentá-lo como ótimo garantido. A referência exata permite avaliar perda. O gestor escolhe método e justifica o plano, guardado como evidência nos casos considerados. Mudanças/revisões/contestações exigem nova simulação. Abrir revisão não decide o caso automaticamente.

Interface: controles de Cluster junto do CSV existente; tela Planejar revisões acessível da Revisão, Materiais e Passagem Livre, com parâmetros, comparação e revisão dos escolhidos. Preservar identidade e navegação móvel; nenhuma dependência ou serviço pago adicional. Originais não serão editados.
