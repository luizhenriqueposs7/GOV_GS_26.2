# Referências visuais para a Central CitizenTech

Pesquisa em 14/11/2026, solicitada pelo grupo após avaliar a interface como básica e sem identidade suficiente. Esta nota reúne observações de design e propostas do assistente. Não registra aprovação de um novo desenho.

## Diagnóstico da central

A interface atual concentra foto, descrição, contexto, localização, confirmações e avisos em um formulário longo. Marca, títulos e áreas de conteúdo usam poucas variações de peso visual. O cabeçalho escuro e as divisórias dão organização, mas a experiência ainda se aproxima de um cadastro administrativo. A ampliação móvel acrescentou funções sem redesenhar a sequência inteira da tarefa.

Mudar somente cores e arredondamentos não resolve essa composição. Uma revisão precisa tratar marca, tipografia, imagens, tamanho das ações, sequência do cadastro e apresentação do acompanhamento.

## Referências observadas

### Colab: identidade próxima do cidadão

Fonte: https://www.colab.com.br/sou-cidadao/

Observação visual: títulos com desenho arredondado, laranja e roxo de alta presença, fotografia de pessoas e grafismos curvos. As chamadas explicam ações cotidianas. A fonte dos títulos apareceu como Cocogoose-bold no estilo computado da página observada. Isso descreve o site; não recomenda licenciar ou copiar essa fonte.

Aplicação proposta: uma marca mais reconhecível, título de abertura direto, uma ação principal evidente e fotografia contextual. Preservar o laranja CitizenTech, em vez de reproduzir a paleta do Colab. As curvas e os grafismos poderiam dar lugar a uma linguagem própria de quadras, percursos e travessias.

Limite: foi examinada a apresentação pública ao cidadão. A página não equivale ao aplicativo operado com uma conta.

Captura: [Colab, apresentação ao cidadão](../output/design-research/colab-cidadao.jpg).

### SeeClickFix / CivicPlus: estados e trabalho do revisor

Fontes: https://www.civicplus.com/seeclickfix-311-crm/ e https://www.civicplus.com/seeclickfix-311-crm/unified-platform/

Observação visual: a apresentação do produto mostra localização no aplicativo móvel. A página da plataforma unificada apresenta estados em sequência, comentários com distinção entre público e interno e uma tabela de gestão. Há separação visual entre o que a pessoa relata e o que a equipe administra.

Aplicação proposta: acompanhamento centrado no pedido, com foto, referência, situação atual e histórico compreensível. Para o revisor, fila mais compacta e decisão em destaque. Os estados usados devem continuar correspondendo aos eventos reais da central, sem sugerir que a prefeitura recebeu ou resolveu o chamado.

Limite: as telas de gestão são imagens demonstrativas publicadas pelo fornecedor. Não houve acesso ao sistema autenticado.

Capturas: [apresentação móvel](../output/design-research/seeclickfix-apresentacao.jpg) e [operação apresentada pelo fornecedor](../output/design-research/seeclickfix-operacao.jpg).

### Go Vocal: papéis e fases com hierarquia

Fonte: https://www.govocal.com/platform-online-engagement-toolbox

Observação visual: superfícies claras, violeta escuro, títulos com mais espaço e ilustrações que distinguem atividades. Os exemplos de interface exibem papéis, fases do projeto e ações locais. A página agrupa ferramentas por finalidade, evitando apresentar tudo no mesmo nível.

Aplicação proposta: dar hierarquia diferente ao cadastro cidadão, à revisão e ao acervo acadêmico. A análise original, a decisão e as fontes podem ocupar áreas próprias, mantendo uma identidade comum. A área de materiais não precisa disputar a ação principal de registrar uma ocorrência.

Limite: a finalidade central é participação pública, mais ampla que atendimento de ocorrências. A comparação é de organização e apresentação, não de equivalência funcional ou de desempenho.

Captura: [exemplos de gestão publicados pelo Go Vocal](../output/design-research/go-vocal-gestao.jpg).

### Decidim / Metadecidim: identidade e processo visíveis

Fontes: https://meta.decidim.org/en/processes/roadmap e https://docs.decidim.org/en/develop/features/general-description.html

Observação visual: marca expressiva, uso de cores de destaque e imagem por processo. A página pública do roadmap informa a fase atual, o período e as formas de participação. A informação sobre o processo aparece antes do conteúdo detalhado.

Aplicação proposta: deixar explícito em qual etapa o pedido está, qual decisão foi registrada e o que ainda depende de revisão. A justificativa deve ser uma parte importante da apresentação, não somente um detalhe escondido no histórico.

Limite: participação, votação e eventos não fazem parte do escopo atual da central. A referência não é uma proposta para acrescentar essas funções.

Capturas: [identidade da comunidade](../output/design-research/decidim-identidade.jpg) e [página pública de processo](../output/design-research/decidim-processo.jpg).

## Direção recomendada pelo assistente

Uma plataforma de bairro com identidade urbana, combinando a proximidade visual do Colab e a clareza de acompanhamento do SeeClickFix. Uma única marca, com duas densidades: cadastro simples para o cidadão e leitura mais compacta para o revisor.

- Marca: estudar um símbolo próprio associado a uma quadra aberta ou a um percurso. O bloco com as letras CT ainda é genérico.
- Cor: laranja #F67024 como assinatura, grafite para o texto e superfícies claras. A combinação precisa ter contraste verificado antes de implementação. Azul pode permanecer em funções de apoio, sem dominar todo o cabeçalho.
- Tipografia: títulos com personalidade e corpo de leitura simples. A família será escolhida no desenho seguinte, sem assumir que Bahnschrift deve continuar.
- Cadastro: dividir visualmente a tarefa em foto, contexto/local e conferência. Foto opcional e alternativa textual devem continuar disponíveis.
- Acompanhamento: foto e situação no centro da composição, com referência, justificativa e histórico próximos.
- Revisão: fila, evidência e decisão com hierarquia própria; acervo acadêmico em acesso secundário.
- Grafismo: linguagem de ruas, quadras e circulação, com função de orientar. Evitar contagens decorativas, fotografias genéricas e elementos visuais sem relação com a tarefa.

Essa direção ainda é uma recomendação. O passo seguinte é comparar propostas visuais da própria CitizenTech antes de alterar a aplicação.

## Alcance da pesquisa

As capturas foram feitas em páginas públicas, sem entrar em contas, publicar pedidos ou solicitar demonstrações comerciais. Foram recusados cookies opcionais quando o aviso apareceu. A central em execução não foi alterada nesta etapa.

O FixMyStreet foi consultado documentalmente, mas sua abertura no navegador retornou HTTP 429; não foi usado como captura visual. A instância Decidim Barcelona apresentou erro de certificado, que não foi contornado. A comunidade Metadecidim, indicada pela documentação oficial, foi observada como referência própria. O acesso web automatizado ao roadmap posteriormente retornou 403, embora a página já tivesse sido observada no navegador; essa diferença não foi tratada como prova de disponibilidade geral.

Não foram feitos testes dos aplicativos com pessoas, avaliações de acessibilidade, medições de conversão ou comparações de desempenho. Expressões como “mais próximo” e “mais claro” nesta nota são julgamentos de design, não resultados de testes.
