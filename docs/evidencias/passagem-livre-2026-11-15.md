# Verificação do Passagem Livre · 15/11/2026

## O que foi executado

- API com banco temporário: cenário idempotente, vínculo opcional, criação via formulário com anexo, edição/desvínculo, revisão obrigatória, plano protegido e comparação da assinatura na transação. Resultado calculado pelo servidor, sem aceitar resultado fornecido pelo cliente.
- Cenário: nenhuma intervenção mantém duas barreiras; só calçada ou só rampa mantém uma; ambas removidas geram continuidade apenas na hipótese. Sem observação, trechos desconhecidos permanecem desconhecidos.
- Relatos de barreira e condição desconhecida no mesmo trecho: ambas as informações permanecem visíveis; marcar reparo não produz certeza. Dois relatos no mesmo trecho contam um trecho afetado, sem afirmar duplicidade.
- Navegador: preparação dos dois pedidos, revisão da calçada, persistência original do ZelaBairro, revisão da rampa, plano justificado, contestação e plano desatualizado. A rampa conserva pendência de enquadramento e sua confirmação local é bloqueada; isso não foi substituído por um encaminhamento inventado.
- Móvel em 390px: foto 017_1362_1816.jpg do acervo, coordenadas manuais -23.544150/-46.643600, contexto de área pública, vínculo à calçada, rascunho e envio completo. O ponto não foi ajustado automaticamente ao percurso. Recuperar o rascunho exigiu confirmar novamente as coordenadas.
- Teclado: após pressionar Space no checkbox e aguardar o recálculo, o foco continuou no controle correspondente. A lista mostrou condições atual e simulada iguais às do mapa. Largura do documento 375px em viewport de 390px; sem rolagem horizontal. Console sem erros.

## Correções decorrentes da revisão

1. A inclusão de passagem nula alterava o hash dos envios anteriores. O teste reproduziu HTTP 409 para o mesmo envio legado; a assinatura do servidor e a comparação do cliente foram compatibilizadas. O reenvio voltou ao mesmo ID e não criou evento.
2. A atualização de lote RPA podia retirar a associação ao trecho. O teste falhou antes da correção; agora preserva o vínculo e invalida a revisão após mudança na origem.
3. GET do percurso e POST da simulação podiam usar bases diferentes. O rótulo de validade de cada plano agora é comparado à base da simulação efetivamente mostrada.
4. Recriar a lista perdia foco e ocultava a condição simulada na alternativa textual. O foco é restaurado, e cada cartão mostra atual → hipótese, condição de cada relato e incerteza coexistente.

## Dados e integrações

A base principal tem seis pedidos: quatro anteriores preservados, com históricos de 7, 5, 4 e 4 eventos, e dois fictícios preparados explicitamente para o percurso. As revisões e a contestação do teste ficaram em base separada. O preparador passou nas sete verificações atuais em 15/11: Central, RPA, fluxo de registro/revisão/contestação, PLN, Visão, Generative AI e materiais das nove disciplinas. Diagnóstico resumido em passagem-livre-prontidao-2026-11-15.json.

71 testes Python, 19 JavaScript, quatro validações PowerShell e verificações de sintaxe/diff passaram. O relatório foi gerado com 14 páginas, com páginas renderizadas e inspeção da capa, miolo, quadro de integração e paginação. O roteiro preserva todas as nove disciplinas e o alvo de 6min30s.

## Capturas

- output/screenshots/passagem-livre-desktop-2026-11-15.jpg: central principal com o cenário preparado.
- output/screenshots/passagem-livre-conferencia-mobile-2026-11-15.jpg: foto e ponto manual na conferência do cadastro.
- output/screenshots/passagem-livre-mobile-2026-11-15.jpg: condições do trecho e controles por teclado em tela estreita.

## Limites preservados

Percurso, posições e condições são didáticos. A linha sobre OpenStreetMap é esquemática, sem levantamento de calçadas. Não há estimativa de pessoas beneficiadas ou custos, certificação de acessibilidade, reparo executado ou integração municipal. IoT é externo, Cluster é simulação iSPD e Quântica é estudo conceitual. Visão sinaliza fissura e não detecta buracos ou passagem segura. Câmera, GPS e instalação não foram testados em telefone físico; as capturas desta etapa usaram navegador e ponto manual. Conclusão conjunta, gravação/publicação e links finais continuam pendentes.
