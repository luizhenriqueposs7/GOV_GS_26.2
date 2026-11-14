# Revisão da interface da central

Pedido do usuário: retirar a aparência de template e dar identidade própria à aplicação. A crítica se refere ao desenho, sem pedir mudança na finalidade da central.

## Direção adotada pelo assistente

Usar referências de sinalização urbana e de atendimento: assunto, endereço, registro e decisão. O formulário passa a abrir a tela. Cabeçalho horizontal compacto e índice de serviços substituem o banner promocional e os blocos decorativos. Esta é uma escolha de implementação do assistente, sujeita à avaliação do resultado pelo usuário.

Foram considerados um painel de operações, uma composição editorial e o atendimento direto. O primeiro ampliaria a ênfase em indicadores sem demanda real. O segundo poderia apenas substituir um template por outro. A direção de atendimento direto mantém a ação principal e usa os códigos e fontes dos serviços como identidade.

## Tokens

- Azul de sinalização: #203C55. Grafite do texto: #263746.
- Fundo: #F2F5F7. Superfície de preenchimento: #FFFFFF.
- Laranja CitizenTech: #F67024, usado para ação e posição atual.
- Divisores: #C8D2DA. Texto secundário: #566775.
- Bahnschrift nos títulos curtos e na marca, pela relação com sinalização; Segoe UI no corpo e nos campos. Fontes do sistema, sem dependências externas.

## Estrutura

Marca e navegação horizontal

    Novo pedido             Consulta do catálogo
    Descrição               Calçadas
    Bairro / referência     Iluminação
    Contexto                Situações que exigem confirmação
    Confirmação e ação

As telas de acompanhamento e revisão usam registros e faixas de informação, sem repetir cartões. O acervo das disciplinas vira uma lista com função, limite e nomes de materiais. Cabeçalhos explicam a ação; saem slogans, chamadas em caixa alta, números decorativos e setas acrescentadas aos botões.

## Alcance e verificação

Alterações em web/index.html, web/style.css e apresentação de web/app.js. Permanecem os contratos, IDs de formulários, rotas, dados existentes, validações e funções do backend. Os materiais originais não serão alterados.

Conferir sintaxe JavaScript, 44 testes existentes, tela inicial, navegação das quatro áreas e layout em larguras de computador e celular. Capturas serão feitas da aplicação em execução. Não são testes com pessoas nem validação em campo.

Sequência: atualizar marcação e textos; substituir a folha de estilo; adequar a apresentação dos resultados e dos materiais; recarregar a central, conferir e registrar capturas.
