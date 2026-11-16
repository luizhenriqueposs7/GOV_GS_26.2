# Publicação completa do ZelaBairro na Vercel

## Objetivo autorizado

Publicar a central e a jornada móvel no projeto existente `gov26.2`, na equipe `luizinhos-projects-e1726c23`. Usar somente serviços gratuitos. Preservar a execução local e os materiais entregues pelas nove disciplinas.

## Comportamento necessário

- Pedidos, decisões, contestações, evidências e planos persistem em Postgres, inclusive entre instâncias e implantações. Nenhum banco temporário é usado como persistência na nuvem.
- Fotos normalizadas, sem EXIF, ficam em bucket privado do Supabase. O servidor autentica a leitura. A foto é armazenada antes de vincular o pedido.
- A revisão, a confirmação pela rotina original do Frontend e o vínculo na central usam uma única transação. Escritas concorrentes preservam a revisão e a base do Passagem Livre.
- A demonstração pública exige autenticação; a chave de gestão continua separada. Chaves e senhas ficam apenas em variáveis do servidor ou arquivos locais ignorados.
- A versão online usa Groq gratuito, modelo `qwen/qwen3.8-27b`, para selecionar os trechos do assistente original. O Qwen3-4B original continua local. A mudança é identificada e não herda as métricas históricas.
- Visão usa o mesmo checkpoint ResNet18 convertido para ONNX, com verificação numérica e das decisões. Não detecta buracos nem certifica acessibilidade.
- RPA, PLN e Frontend reutilizam o código entregue. IoT permanece externo; Cluster é histórico; Quântica é conceitual.
- Falta de configuração ou falha externa retorna indisponibilidade explícita. Não há respostas históricas apresentadas como inferência atual.
- A conta/organização do Supabase depende da escolha do usuário. Nenhum projeto existente será alterado e dados locais pessoais não serão copiados automaticamente.

## Critérios de conclusão

Decisão de implementação, 16/11: o build validou os modelos no Linux, mas a publicação do pacote de 603,20 MB foi rejeitada pelo limite efetivo da conta, mesmo com Fluid e Large Functions configurados. A versão passa a usar o empacotamento padrão e obter os mesmos pesos por revisão e SHA fixos, com cache temporário apenas de modelos. Os dados da aplicação permanecem no Postgres e Storage. A primeira inferência precisa de teste de tempo e recuperação de falhas no download.

Testes locais existentes preservados; testes de autenticação e falhas externas; transações reais em Postgres; foto recuperada por outra instância; percurso com revisão, plano e contestação; implantação pronta e fluxo real pelo HTTPS. Câmera e GPS físicos dependem da conferência do usuário no celular. Sem credenciais ou acesso ao serviço, registrar a pendência e não declarar publicação completa.
