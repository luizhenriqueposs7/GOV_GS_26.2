# Vídeo integrado: um pedido do registro à nova análise

Alvo: **6min30s**, contando abertura e encerramento. Entrega: entre 5 e 7 minutos, no YouTube como **Não Listado**. Este roteiro é planejamento, não uma gravação concluída.

| Integrante | Responsabilidade | Roteiro |
| --- | --- | --- |
| Luiz Henrique Poss, RM562177 | Generative AI, Governança e Business Analytics, PLN e Cluster; também abertura, Frontend/mobile e encerramento | [Luiz](video/01-luiz-henrique.md) |
| Luis Filipe Chaves Amorim, RM564706 | IoT e Computação Quântica | [Luis Filipe](video/02-luis-filipe.md) |
| Felipe Stefani Honorato, RM563380 | RPA e Visão Computacional | [Felipe](video/03-felipe-stefani.md) |

As nove disciplinas são distribuídas entre os três conforme a divisão solicitada. Frontend/mobile, que não recebeu outro responsável nessa divisão, permanece com Luiz. O tempo de fala fica em 4min20s para Luiz, 1min15s para Luis Filipe e 55s para Felipe. Governança recebe mais tempo porque fecha o fluxo e é a disciplina desta entrega. Luiz aparece na abertura e retorna depois dos colegas. Não é necessário gravar os três juntos nem mostrar rosto e tela simultaneamente.

## O que demonstrar

Uma pessoa fotografa um problema, confere relato/local e registra o pedido. O mesmo identificador chega ao planejamento e à revisão. Consultas são vinculadas quando pertinentes. A ficha mostra quem recebe e por qual canal; o acompanhamento usa protocolo de demonstração e permite contestar. O protótipo não envia solicitações à prefeitura nem executa reparos.

O vídeo deve mostrar a continuidade entre foto, sugestão, correção humana, fonte, prioridade, justificativa e contestação. No Passagem Livre, resolver um ponto não garante que todo o percurso esteja acessível. Esse percurso é didático.

## Linha do tempo

| Tempo | Quem | Tela e resultado |
| --- | --- | --- |
| 00:00–00:15 | Luiz | Registrar: explicar problema e propósito. |
| 00:15–01:00 | Luiz | Foto no celular, GPS, conferência, envio e recibo. Guardar ID. |
| 01:00–01:20 | Felipe | Pedidos → triagem original do pedido: categoria, prioridade e indicação de revisão. |
| 01:20–01:55 | Luiz | Gestão → Importar lote: CSV com 2/4 workers, IDs e tempos atuais. |
| 01:55–02:45 | Luis Filipe | Planejar revisões: pedido móvel e dois pendentes, capacidade, comparação e plano justificado. |
| 02:45–03:20 | Luiz | Projeto → Consultar um serviço municipal: resposta atual e fonte. |
| 03:20–03:50 | Luiz | Pesquisar prevenção de desastres: trecho, origem e página/seção. |
| 03:50–04:25 | Felipe | Verificar sinal de fissura: inferência atual sobre recorte de concreto. |
| 04:25–04:50 | Luis Filipe | Projeto → OuviAí: campainha e aviso, identificados como simulação. |
| 04:50–06:15 | Luiz | Revisão, confirmação local, destino/ficha, protocolo SIM, retorno, contestação e histórico. Passagem Livre em captura breve do cenário. |
| 06:15–06:30 | Luiz | Histórico do mesmo pedido e GitHub: resultado demonstrado e limites. |

O alvo deixa 30 segundos até o teto. Grave cada operação até aparecer o resultado e corte apenas espera/digitação repetitiva, sem alterar a ordem ou esconder uma falha. Os arquivos individuais podem ser maiores; a montagem final precisa ter de 5 a 7 minutos.

## Preparar

1. Abrir [a central oficial](https://gov262.vercel.app/#pedido) no Safari/Chrome. Fechar abas antigas para atualizar. A entrada não pede login; a gestão exige chave.
2. Ensaiar câmera, GPS, som e legibilidade no aparelho. Anotar aparelho/navegador/resultado. O teste físico permanece pendente até ser executado pelo integrante.
3. Usar imagem sem pessoas, placas ou documentos. Não entrar na via nem se aproximar do risco para fotografar. Uma foto real não comprova dimensão, causa ou gravidade.
4. Identificar encenação como demonstração. GPS real deve ser descrito como posição conferida pelo integrante, não como coordenada sintética. Não associar foto de outro local ao percurso didático.
5. Digitar a chave em campo de senha, sem filmar seu arquivo, configurações ou cabeçalhos de rede.
6. Separar `docs/exemplos/cluster-revisoes.csv` e `materiais/visao/data/recortes/017_1135_2497.jpg`. O CSV é fictício; o recorte não é uma foto da ocorrência móvel.
7. Testar uma consulta GenAI e uma inferência para conferir disponibilidade. Esse aquecimento não deve aparecer como resultado da tomada atual. Online usa Groq, diferente do modelo local original.
8. Luiz passa o ID aos colegas e vincula somente consultas GenAI/PLN pertinentes. Felipe mostra a triagem do mesmo pedido; Luis Filipe o inclui no planejamento. Um recorte independente de Visão fica sem vínculo. Evitar alterações simultâneas no mesmo pedido.
9. Ensaiar o Passagem Livre com os pedidos fictícios preparados pelo controle disponível. Outros registros podem manter barreiras; não prometer que marcar dois sempre libera o caminho.
10. Se encenar correção, separar uma segunda imagem e declarar cenário sem obra real. Não apresentar foto de outro lugar como prova de reparo.

## Falar enquanto faz

Cada pessoa abre apenas suas telas e usa o roteiro individual como lembrete. Explicar uma ideia por resultado; não ler o relatório. Nome, RM, disciplina, abertura e transições também contam no tempo.

Gravar primeiro a criação, depois lote/plano, consultas e, por último, revisão/contestação. Conservar o ID nas cenas. A fala deve acompanhar cliques e resultados reais. Não afirmar que uma simulação ou evidência antiga é execução atual.

## Contingências

| Se acontecer | Como demonstrar honestamente |
| --- | --- |
| GPS negado/sem sinal | Preencher referência ou ponto manual e identificar a escolha. |
| Foto inconclusiva | Mostrar que a pessoa precisou escrever o relato. |
| Groq indisponível/sem cota | Mostrar falha e alternativa manual, ou gravar outra tomada atual quando voltar. |
| Visão com resultado inesperado | Explicar o resultado e seu limite, sem trocar o rótulo na edição. |
| Pedido alterado durante planejamento | Atualizar, conferir e comparar novamente. |
| Confirmação local bloqueada | Mostrar pendência de contexto/enquadramento; usar caso elegível para demonstrar confirmação. |
| Percurso ainda interrompido | Mostrar outra barreira ou condição desconhecida. |

## Conferir antes de enviar

- Todas as nove disciplinas aparecem com função e limite.
- Há execução atual de envio, revisão e contestação, além de destino/canal visível.
- IoT simulado, QAOA em CPU, dados fictícios e protocolo SIM estão identificados.
- Nenhuma chave ou informação pessoal aparece.
- O arquivo final tem entre 5 e 7 minutos, tela legível e áudio compreensível, sem leitura massiva.
- Publicar como Não Listado, testar o link sem login e inserir o mesmo endereço no relatório e no README.
- Concluir o relatório com os integrantes e preservar o commit correspondente à submissão.
