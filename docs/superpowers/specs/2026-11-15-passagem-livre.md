# Passagem Livre

Implementação autorizada pelo pedido de 15/11/2026: planejamento de acesso na central e no mobile, com um percurso demonstrável e preservação das integrações da GS.

## Comportamento

Um percurso didático entre ponto de ônibus e unidade de saúde contém quatro trechos esquemáticos. Dois trechos têm condição livre declarada apenas no cenário; calçada e rampa começam sem verificação. Um comando do gestor prepara dois pedidos fictícios usando a triagem real do RPA, sem alterar os pedidos já existentes. A repetição do comando não duplica nem restaura decisões anteriores.

O formulário móvel permite associar um pedido a um trecho e informar passagem bloqueada, dificultada ou condição desconhecida. A associação é declarada pela pessoa e não comprova coincidência geográfica. Câmera, GPS, foto, rascunho, revisão, confirmação local e contestação continuam disponíveis. A referência geográfica do pedido é conservada separadamente do desenho didático.

A simulação compara a condição atual com a hipótese de remover integralmente as barreiras informadas dos trechos selecionados. Resolver apenas uma de duas barreiras não restabelece a continuidade. Condição explicitamente desconhecida não vira livre ao selecionar reparo. Sem observação, um trecho desconhecido também permanece desconhecido. Dois relatos do mesmo trecho contam como um trecho afetado, sem afirmar duplicidade entre relatos. A simulação nunca altera pedidos, libera navegação nem registra reparo executado.

O plano salva seleção, resultado calculado no servidor, justificativa, revisor e versões das entradas. Exige chave de gestão, revisão atual de todos os pedidos vinculados e a assinatura da base mostrada na tela. Mudança ou contestação torna o plano anterior desatualizado, preservando-o para consulta. Nenhum resultado calculado pelo cliente é aceito.

## Integrações e enunciado

RPA executa a triagem. Frontend conserva validação e persistência do ZelaBairro. Generative AI, PLN e Visão mantêm consultas reais e vínculo de evidência por pedido; o percurso não transforma essas saídas em certificação de passagem. IoT continua como execução externa do OuviAí. Cluster continua como simulação iSPD e Quântica como contribuição conceitual, sem novo ganho de otimização alegado. Governança registra revisão, justificativa, contestação e validade dos planos; Business Analytics compara trechos e cenários, sem inventar custos, beneficiários ou impacto medido.

As nove disciplinas permanecem no catálogo, no relatório e no roteiro de 6min30s. A conclusão fica reservada à elaboração conjunta. A versão entregue exige relatório de 10 a 15 páginas, GitHub e vídeo Não Listado de 5 a 7 minutos, ainda dependentes dos links finais.

## Limites

Sem novas dependências, rotas arbitrárias, contas individuais, integração municipal, detector de buracos ou garantia de segurança/acessibilidade. O percurso usa coordenadas ilustrativas em São Paulo, com aviso permanente de traçado esquemático e de ausência de inspeção em campo. Não recolhe diagnóstico de deficiência nem dados pessoais de deslocamento. O teste físico da câmera/GPS permanece pendente até ser realizado no aparelho.
