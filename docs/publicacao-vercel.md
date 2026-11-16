# ZelaBairro na Vercel

## Situação em 16/11/2026

A versão online está em [gov262.vercel.app](https://gov262.vercel.app), com acesso privado por senha. A Vercel aceitou o pacote de 222,95 MB. Foto, reenvio, revisão, confirmação no Frontend, contestação e Visão passaram pelo HTTPS com Supabase real. O Groq retornou a fonte ILU.1 e passou nos controles de privacidade, escopo e falta de evidência. RPA, PLN, catálogo das nove disciplinas e Passagem Livre também foram verificados na nuvem. A execução local foi preservada.

Destino Vercel: `luizinhos-projects-e1726c23/gov26.2`. Projeto Supabase indicado pelo usuário: `rruiqrnahwbnrfwlgixz`. Nenhum projeto anterior foi modificado. Fotos, coordenadas e bancos locais não serão importados automaticamente.

## Entrada e pacote

`pyproject.toml` aponta para `central.app:app`, corrigindo a identificação ambígua entre aplicativos dos materiais. A raiz do projeto na Vercel deve ser a raiz deste repositório.

O build executa `python scripts/build_vercel.py`: confere o ONNX, o snapshot fixo do encoder e a compatibilidade do ranking com a referência original. Remove apenas testes e bytecode das bibliotecas na instalação isolada do build, com verificação de limites de caminho e uma nova conferência de imports/RPA/PLN. A versão Python está em `.python-version`.

O primeiro pacote completo chegou a 603,20 MB e foi recusado pelo limite efetivo da conta. A versão final usa o caminho padrão, com 222,95 MB, e baixa os pesos por revisão e SHA fixos para um cache temporário de aproximadamente 297 MB. Os dados da aplicação continuam no Supabase. A primeira consulta ao assistente levou 20,24 segundos nesta conferência. Os cinco arquivos do encoder compartilham um prazo de preparação de 50 segundos. Não houve mudança de plano.

Vídeos, PDFs, datasets de Visão, testes e pesos PyTorch não compõem a função. Materiais permitidos no manifesto continuam acessíveis pela revisão já publicada no GitHub. As fotos dos pedidos continuam privadas, com leitura pelo servidor.

## Variáveis do servidor

Configurar em Production e Preview. Não colocar segredos no navegador, no Git ou na conversa.

| Variável | Conteúdo |
| --- | --- |
| `GOV_RUNTIME` | `vercel`; `VERCEL=1` também ativa esse modo |
| `GOV_DATABASE_URL` | URL do pooler em transaction mode, com senha e TLS |
| `SUPABASE_URL` | URL HTTPS do projeto autorizado |
| `SUPABASE_SECRET_KEY` | Chave de servidor `sb_secret_…`; não usar publishable key |
| `GOV_MANAGER_KEY` | Chave estável de revisão com pelo menos 24 caracteres |
| `GOV_ACCESS_USER` | Usuário do acesso privado da demonstração |
| `GOV_ACCESS_PASSWORD` | Senha com pelo menos 16 caracteres |
| `GROQ_API_KEY` | Chave da conta Free do Groq |
| `VERCEL_SUPPORT_LARGE_FUNCTIONS` | `0`, após rejeição do pacote completo |
| `VERCEL_ANALYZE_BUILD_OUTPUT` | `1`, já configurado |
| `VERCEL_PYTHON_COMPILEALL` | `0`, para evitar bytecode opcional no pacote |

Sem configuração de persistência ou acesso, a aplicação não inicia em nuvem. Não cria banco temporário ou chave de gestão por instância. Sem Groq, a consulta do assistente informa indisponibilidade. Não há troca automática para serviço pago ou resposta histórica.

## Persistência, confirmação e fotos

As migrações em `supabase/migrations/` foram aplicadas no projeto autorizado após a inspeção de seu estado vazio. Criaram o esquema privado `citizentech`, sem grants públicos, com RLS e políticas para o papel exclusivo `zelabairro_runtime`. Ele não é superusuário, não cria bancos ou papéis e não ignora RLS. Não há DDL nas requisições.

O adaptador reutiliza o domínio, com trava transacional compartilhada entre instâncias. A confirmação valida o contrato original do Frontend e executa sua gravação, o vínculo e o evento na mesma transação. Contestação e mudança do pedido invalidam a revisão. Passagem Livre preserva a comparação da base antes de salvar o plano.

O bucket `zelabairro-fotos` é privado. O servidor remove EXIF, limita a imagem, calcula SHA-256 e armazena a foto antes de registrar a referência. Uma falha no upload impede o pedido. Reenvios verificam a integridade do objeto. O aparelho prepara imagens de até 3 MB para respeitar o limite de requisição da função.

O acesso usa HTTP Basic sobre HTTPS, inclusive para APIs, fotos e interface. A chave de revisão permanece separada. É uma demonstração compartilhada pelo grupo, sem contas individuais por solicitante. O service worker guarda apenas a interface, sem respostas de API, fotos ou mapas externos.

O domínio principal foi conferido sem bypass: sem senha retorna 401; com senha, interface e APIs respondem. O segredo temporário de automação usado para conferir a prévia foi revogado após autorização e teste. O acesso do grupo está apenas no arquivo local ignorado `data/acesso-zelabairro-online.txt`.

## Integrações

RPA reutiliza triagem e CSV; Frontend reutiliza validação e persistência; PLN consulta o corpus entregue. Generative AI mantém corpus, busca híbrida, filtros e respostas extrativas, com seleção online por `qwen/qwen3.8-27b` no Groq Free. O Qwen3-4B-2507 continua local e suas métricas históricas não avaliam o modelo online. Visão usa o mesmo checkpoint ResNet18 convertido para ONNX; não detecta buracos nem fornece laudo. IoT permanece externo, Cluster é simulação histórica e Quântica é contribuição conceitual. Governança registra revisão, contestação, evidências, indicadores e o planejamento didático.

## Conferência antes de gravar

Validar build pronto e autenticação HTTPS; enviar foto e ponto confirmado; revisar, confirmar no ZelaBairro e contestar. Repetir o envio, recuperar a foto em outra instância e testar um plano do Passagem Livre. Conferir Groq e Visão em execução atual.

Câmera e GPS físicos dependem do aparelho. O percurso não foi vistoriado, não é um roteador validado e não comprova reparos. O vídeo continua limitado a 5–7 minutos. Conclusão e link do vídeo serão concluídos com o grupo.

## Fontes técnicas

- [Vercel: entrada, build e estáticos FastAPI](https://vercel.com/docs/frameworks/backend/fastapi).
- [Vercel: limites e Large Functions](https://vercel.com/docs/functions/limitations).
- [Supabase: conexão e pooler](https://supabase.com/docs/guides/database/connecting-to-postgres).
- [Supabase: chaves públicas e secretas](https://supabase.com/docs/guides/getting-started/api-keys).
- [Groq: modelo escolhido](https://console.groq.com/docs/model/qwen/qwen3.8-27b).

Consulta em 16/11/2026. Sem contratação de serviços pagos.


## Relato por foto, 16/11/2026

A foto inicia a geração de uma descrição preliminar pelo mesmo Qwen3.8-27B, com resposta estruturada e abstenção. Em paralelo, o navegador solicita GPS e consulta a região diretamente na BigDataCloud, usando somente a posição atual autorizada. O endpoint gratuito não fornece endereço de rua. Ponto e texto são conferidos antes de enviar; falha de um serviço permite preenchimento manual, sem fingir sucesso.

A prévia não grava foto ou pedido. No envio, a assinatura do servidor é verificada contra o hash da foto antes de armazenar o anexo. Modelo, data e descrição original ficam no histórico, separados do texto conferido. Rascunho conserva essa origem e os campos automáticos, sem conservar a confirmação.

Passaram 136 testes Python com Postgres temporário e TLS e 25 testes JavaScript. O navegador móvel, com IA sintética, GPS controlado e região simulada, executou prévia, correção, envio, revisão, confirmação, contestação e recuperação de rascunho. Cancelamento durante preparo e região antiga após restaurar rascunho foram reproduzidos e corrigidos. O teste físico continua pendente.

Fontes técnicas: [imagens e saída estruturada no Groq](https://console.groq.com/docs/vision), [uso gratuito e consentido da região no próprio aparelho](https://www.bigdatacloud.com/docs/article/fair-use-policy-for-free-client-side-reverse-geocoding-api), [limite de região sem rua/número](https://www.bigdatacloud.com/reverse-geocoding).
