# Clareza da jornada e gravação

O usuário pediu organizar a plataforma, explicar o problema atendido e preparar roteiro para Luiz Henrique Poss (RM562177), Luis Filipe Chaves Amorim (RM564706) e Felipe Stefani Honorato (RM563380). A identidade Quadra aberta já aprovada permanece. A mudança reorganiza informação e ações existentes; não cria serviço municipal, integração de IoT ou resultado de campo.

## Decisões de implementação

- Uma entrada para todos: Registrar. Explicar que foto/local preparam pedido para revisão e acompanhamento, sem envio automático ao órgão.
- Cinco destinos principais: Registrar, Pedidos, Mapa, Gestão, Projeto. Passagem Livre é uma visão do mapa; planejamento e lote pertencem à gestão. URLs anteriores continuam válidas.
- Pedido aberto prioriza relato/foto, destino, acompanhamento e próxima ação. Dados técnicos, contestação e histórico ficam em detalhes acessíveis. Recolher não elimina conteúdo nem controles.
- Projeto oferece consultas separadas e recolhidas de orientação, PLN e Visão, trabalhos originais e OuviAí. Não abrir simultaneamente todos os formulários na primeira visita.
- Cores e fonte existentes: #20282a, #F67024, #f4f4f0, branco, cinza. Archivo para texto e títulos. Navegação contextual com indicação de seleção e foco visível. Campos móveis conservam 16 px.

## Alternativas consideradas

Manter seis abas e só encurtar textos não resolve a mistura entre cidadão, gestão e disciplinas. Criar outra página inicial e perfis aumenta passos sem necessidade. Minha escolha é reorganizar as telas existentes com navegação contextual e abertura progressiva dos detalhes, dentro do pedido de simplificação.

## Alcance

HTML/CSS, seleção de navegação em app.js, apresentação do detalhe e acompanhamento, cache/versão, roteiro geral e falas individuais. Mesmos endpoints, validações, chave de gestão, persistência, confirmação explícita e contestação. Testar navegador estreito, paisagem e desktop, abas antigas, fluxo completo e respostas tardias. Conclusão final do relatório permanece para redação conjunta.
