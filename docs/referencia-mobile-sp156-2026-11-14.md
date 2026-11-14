# Jornada móvel e acessibilidade: comparação de escopo

Conferência em 14/11/2026, durante a elaboração conjunta da conclusão. O usuário apontou a ausência de um fluxo no celular que reúna foto, localização e solicitação.

## O que já foi documentado no SP156

- A descrição do aplicativo publicada pelo fornecedor informa georreferenciamento, foto pela câmera ou galeria e abertura de solicitações. A página consultada indica atualização em 30/09/2026.
- A Prefeitura anunciou em 16/06/2025 o reconhecimento de imagens para sugerir serviços. A relação inicial inclui tapa-buraco, tapa-buraco em corredor de ônibus e outros quatro serviços.
- Essas fontes documentam recursos existentes ou anunciados. Não foi feito um teste operacional do aplicativo SP156 em um aparelho nesta pesquisa.
- As fontes não permitem presumir que uma foto, sozinha, abra automaticamente qualquer solicitação, sem formulário, identificação ou confirmação.

Fontes: [aplicativo SP156 no Google Play](https://play.google.com/store/apps/details?id=com.pmsp.sp156&hl=pt_BR); [comunicado da Prefeitura sobre reconhecimento de imagem](https://prefeitura.sp.gov.br/web/prefeitura-de-sao-paulo/w/com-nova-funcionalidade-aplicativo-sp156-passa-a-utilizar-intelig%C3%AAncia-artificial-para-agilizar-atendimentos); [orientações oficiais para abertura de solicitações](https://prefeitura.sp.gov.br/web/inovacao/w/acesso_a_informacao/350229).

## Situação antes da ampliação

A interface se adapta a telas pequenas. O formulário principal solicita descrição, bairro, referência e contexto. O envio de imagem está na área de análise de Visão, separado do cadastro do pedido. Não há uso da API de geolocalização no cliente, captura integrada da foto no formulário principal ou abertura de protocolo municipal. O modelo visual entregue sinaliza fissuras em concreto; não existe um detector de buracos validado no projeto.

Portanto, câmera e localização não devem ser apresentadas como novidade do projeto ou como funções já integradas. A evolução discutida consiste em reunir a coleta móvel e a confirmação do usuário com o fluxo de revisão e contestação que foi executado.

## Acessibilidade a considerar

O uso no celular, por si só, não demonstra acessibilidade. Como referência, o tutorial de formulários da W3C WAI orienta rótulos associados aos campos, instruções, validação, confirmação das entradas e mensagens de erro compreensíveis. Também discute uso por leitores de tela e por pessoas com limitações de destreza. Uma coleta por foto e GPS deve manter alternativas para quem não puder utilizar esses recursos; esta última escolha é uma proposta de produto, não um recurso já implementado.

Fonte: [W3C WAI - Forms Tutorial](https://www.w3.org/WAI/tutorials/forms/).

Em 14/11/2026, o usuário autorizou ampliar o protótipo, com prazo até 16/11. O plano e as verificações da implementação estão em plano-mobile-2026-11-14.md. Esta descrição registra a situação anterior, não o estado final da ampliação.
