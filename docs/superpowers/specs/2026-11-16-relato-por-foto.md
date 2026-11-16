# Relato por foto

Fluxo aprovado pelo integrante em 16/11/2026: tirar foto, obter localização e gerar o relato; conferir e enviar. Revisão, confirmação e contestação permanecem na central. Publicar para teste no celular, usando somente serviços gratuitos.

## Decisões

- Duas etapas: foto e conferência editável. Capturar ou escolher uma imagem inicia a geração e solicita GPS. Uma única confirmação final cobre texto, foto, ponto e caráter de demonstração. Nenhum pedido é salvo durante a prévia.
- Reutilizar Qwen3.8-27B no Groq para descrever somente o que é visível, com resposta estruturada e abstenção para imagens inconclusivas. Não inferir endereço, propriedade da calçada, gravidade ou segurança. Categoria e prioridade do RPA continuam calculadas pelo módulo original.
- Consultar região pelo BigDataCloud gratuito diretamente no navegador, somente com posição atual obtida com permissão. O serviço não fornece rua/número; mostrar região aproximada e ponto, ambos corrigíveis. Não usar IP, coordenadas antigas ou manuais como se fossem GPS. Explicar o envio da foto e da posição antes da captura.
- Preservar a sugestão original, modelo, data e hash da foto no registro e histórico. Assinar a prévia no servidor com a chave existente e vinculá-la à foto enviada. Texto conferido pode divergir do original.
- Manter cadastro manual, edição, rascunho, reenvio idempotente, mapa, Passagem Livre e as nove disciplinas. Falhas de IA/GPS deixam os dados disponíveis para correção, sem sucesso fictício. Cancelamento e mudança de tela impedem respostas atrasadas de substituir o formulário.
- O ResNet18 entregue continua no módulo de Visão; a descrição multimodal é uma ampliação identificada, sem novas métricas de acurácia. Sem alteração de pesos ou materiais originais.

Alternativas: manter três etapas conserva o excesso de preenchimento; enviar automaticamente dispensa a conferência da pessoa. A opção aprovada é gerar uma prévia e pedir confirmação antes do envio.

## Aceite

Teste de navegador móvel com imagem, GPS controlado e região simulada: geração real do Groq, revisão humana do texto, envio, revisão de gestão, confirmação, contestação e persistência. Controles de imagem inconclusiva, falhas remotas, GPS negado, cancelamento, origem assinada e foto divergente. Publicação HTTPS com autenticação, sem bypass. Câmera/GPS físicos serão conferidos pelo integrante.
