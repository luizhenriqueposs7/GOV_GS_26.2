# Felipe Stefani Honorato · RM563380

Seu trecho vai de 02:45 a 04:25. As ferramentas ficam em Projeto e abrem uma por vez. Receba o ID do pedido do Luiz; vincule somente o que for pertinente.

## 02:45–03:20 · Generative AI

**Ações:** em Projeto → Vincular uma consulta a um pedido, selecionar o caso se a pergunta tratar dele. Abrir Consultar um serviço municipal e perguntar, por exemplo, “Como solicitar manutenção de uma calçada danificada em praça pública de São Paulo?”. Executar e mostrar resposta/fonte atuais.

**Fala base:** “O assistente consulta as fontes dos serviços municipais e apresenta a orientação com sua origem. Esta é uma resposta da execução atual. A versão online usa o adaptador Groq; o modelo original local permanece nos materiais. Essa orientação ajuda a conferir o encaminhamento, mas não abre uma solicitação na prefeitura.”

Não apresentar os 16/16 casos conhecidos do modelo local como acurácia do adaptador online. Na falha, mostrar indisponibilidade ou gravar outra tomada atual quando o serviço voltar.

## 03:20–03:50 · PLN

**Ações:** abrir Pesquisar prevenção de desastres e pesquisar “enchentes”. Mostrar trecho e origem com página/seção. Vincular ao pedido somente se houver relação com o problema; para calçada sem contexto de desastre, consultar sem vínculo.

**Fala base:** “O PLN permite consultar o corpus de prevenção de desastres e recuperar a origem de cada trecho. Não é um alerta sobre a situação atual do bairro. Se o conteúdo ajudar a analisar um pedido, ele pode ser vinculado ao histórico. Neste caso, não vamos forçar uma relação que o relato não sustenta.”

O corpus ainda tem 39 registros sem decisão humana na planilha de revisão. Não apresentá-lo como integralmente validado.

## 03:50–04:25 · Visão Computacional

**Ações:** selecionar Consultar sem vínculo se usar recorte independente. Abrir Verificar sinal de fissura, escolher `materiais/visao/data/recortes/017_1135_2497.jpg`, executar e mostrar saída atual. Abrir parâmetros somente quando ajudar a explicação.

**Fala base:** “Este é o modelo de Visão entregue na disciplina, aplicado a um recorte de concreto do acervo original. A central executa a inferência e mostra o resultado. Ele sinaliza fissuras dentro desse escopo; não mede buracos, não determina risco estrutural e não certifica acessibilidade. Essa imagem também não representa um reparo do pedido fotografado pelo Luiz.”

Descreva o rótulo que apareceu. Só use a foto móvel se for pertinente a concreto/fissuras; não aplicar ao asfalto ou a outro local. O relato automático do cadastro usa outro modelo e não substitui esta integração.

**Passagem:** “Essas ferramentas fornecem apoio e evidências. A decisão e o acompanhamento continuam sob conferência humana.”
