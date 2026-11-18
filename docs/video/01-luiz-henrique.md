# Luiz Henrique Poss · RM562177

Você apresenta Generative AI, Governança e Business Analytics, PLN e Cluster. Frontend/mobile, abertura e encerramento permanecem com você para conduzir o mesmo pedido. Suas cenas somam **4min**, intercaladas com os colegas. Use as falas como base, acompanhando os cliques.

## 00:00–00:15 · O problema

**Tela:** ZelaBairro → Registrar.

**Fala base:** “Encontrar uma calçada danificada é só o começo. Ainda é preciso explicar o problema, encontrar o canal e acompanhar a resposta. O ZelaBairro organiza esse caminho. Vamos mostrar um pedido passando pela solução.”

## 00:15–01:00 · Frontend e celular

**Ações:** tirar foto ou selecionar imagem; permitir GPS; aguardar preparação; conferir relato, ponto e região; completar referência e contexto quando souber; confirmar; enviar. Mostrar recibo e guardar o ID. Foto fora do percurso didático deve ficar sem vínculo.

**Fala base:** “A foto ajuda a preparar o relato e o celular informa a posição, com minha permissão. Eu confiro o ponto e ajusto o texto antes de enviar. A sugestão não mede o problema nem determina sua gravidade. Agora o pedido foi salvo com este identificador; os colegas vão continuar a partir dele.”

Se a foto/GPS falhar, mostre a alternativa manual e diga isso. A cena precisa do envio atual e do recibo, não apenas da prévia. Envie o ID aos colegas e evite editar em paralelo.

## 01:24–01:54 · Cluster Computing

**Preparação:** a captura do Cluster será feita em base local de teste isolada, com o mesmo pipeline e `docs/exemplos/cluster-revisoes.csv`. Não é execução HTTP na Vercel. A chave sintética não é a chave da central oficial. Felipe já terá explicado a triagem original do pedido.

**Ações:** Gestão → Importar lote. Selecionar o CSV, executar com 2 workers e mostrar aceitos/rejeitados, workers e tempos. Repetir com 4 e conferir as contagens. Os IDs preservados estão no manifesto da captura. Registrar as duas execuções atuais; cortar apenas a espera, identificando o corte.

**Fala base:** “Neste ensaio local, o Cluster distribui o pipeline do RPA entre dois ou quatro workers lógicos, mantendo o mesmo ID no mesmo worker. Depois, a central valida e grava o conjunto. Aqui estão os workers e os tempos desta execução. Isso não comprova máquinas físicas distintas nem que quatro workers sempre sejam mais rápidos.”

Não comparar a latência da Vercel diretamente com os 49,72% históricos do iSPD. Reimportar o mesmo CSV preserva IDs; mudar descrição/bairro invalida revisões anteriores. Gravar as operações completas e selecionar os resultados para os 30 segundos, sem sugerir resposta instantânea.

**Passagem:** “O lote foi processado. O Luis vai mostrar como organizar a capacidade de revisão.”

## 02:49–03:19 · Generative AI

**Ações:** em Projeto → Vincular uma consulta a um pedido, selecionar o caso se a pergunta tratar dele. Abrir Consultar um serviço municipal e perguntar, por exemplo, “Como solicitar manutenção de uma calçada danificada em praça pública de São Paulo?”. Executar e mostrar resposta/fonte atuais.

**Fala base:** “O assistente consulta as fontes dos serviços municipais e apresenta a orientação com sua origem. Esta é uma resposta da execução atual. A versão online usa o adaptador Groq; o modelo original local permanece nos materiais. Essa orientação ajuda a conferir o encaminhamento, mas não abre uma solicitação na prefeitura.”

Não apresentar os 16/16 casos conhecidos do modelo local como acurácia do adaptador online. Na falha, mostrar indisponibilidade ou gravar outra tomada atual quando o serviço voltar.

## 03:19–03:44 · PLN

**Ações:** abrir Pesquisar prevenção de desastres e pesquisar “enchentes”. Mostrar trecho e origem com página/seção. Vincular ao pedido somente se houver relação com o problema; para calçada sem contexto de desastre, consultar sem vínculo.

**Fala base:** “O PLN permite consultar o corpus de prevenção de desastres e recuperar a origem de cada trecho. Não é um alerta sobre a situação atual do bairro. Se o conteúdo ajudar a analisar um pedido, ele pode ser vinculado ao histórico. Neste caso, não vamos forçar uma relação que o relato não sustenta.”

O corpus ainda tem 39 registros sem decisão humana na planilha de revisão. Não apresentá-lo como integralmente validado.

## 04:55–06:15 · Governança e Business Analytics

**Ações:**

1. Gestão → Revisar pedido. Selecione o mesmo ID; confira foto, triagem e contexto. Informe responsável, prioridade, justificativa e chave. Registre a decisão.
2. Confirme o registro local e mostre o resultado. Isso não gera protocolo municipal.
3. Abra o pedido. Em Encaminhar e acompanhar, mostre responsável/canal e abra Ficha, foto e passos para encaminhar.
4. Abra Anotar protocolo ou iniciar demonstração. Mantenha modo demonstração e número SIM; inicie o acompanhamento.
5. Registre retorno de demonstração. Se mostrar correção informada, use imagem identificada como cenário e conferência humana justificada, sem alegar obra real.
6. Mapa → Passagem Livre: captura breve do cenário ensaiado, mostrando que outra barreira/condição desconhecida pode permanecer. Não vincule a ocorrência real de outro lugar ao desenho.
7. Pedidos → mesmo registro. Abra Discorda da decisão? Peça uma nova análise, explique o motivo e solicite revisão. Abra Ver histórico completo do pedido para mostrar decisão preservada e reabertura.

**Fala base:** “A sugestão do sistema continua separada da decisão humana. Aqui registro a prioridade e o motivo, depois confirmo o cadastro local. A ficha mostra quem deve receber e por qual canal. O envio ao órgão ainda é feito pela pessoa; para o vídeo usamos um protocolo de demonstração. O retorno também precisa ser conferido, e uma foto não comprova uma obra. No percurso, uma barreira resolvida não libera automaticamente todo o caminho. Se a decisão for contestada, a revisão é reaberta e a anterior fica no histórico. Os indicadores contam essas situações, sem confundir teste com atendimento municipal. No OuviAí, usamos YAMNet; a CNN original permaneceu externa.”

Ensaie: esta é a cena mais densa. Grave a operação inteira e corte digitação/espera. Se não couber a conferência da correção em 80 segundos, priorize revisão, confirmação, destino/protocolo, contestação e histórico. Não acelerar a fala até ficar incompreensível.

## 06:15–06:30 · Encerramento

**Tela:** histórico e endereço do GitHub.

**Fala base:** “Demonstramos o pedido sendo registrado, planejado, revisado e contestado, com as evidências preservadas. Não comprovamos reparos nem impacto no bairro. O dispositivo de IoT e a validação em campo continuam pendentes. Os materiais estão no GitHub.”

Esse fechamento do vídeo não substitui a conclusão do relatório, que será escrita em conjunto.
