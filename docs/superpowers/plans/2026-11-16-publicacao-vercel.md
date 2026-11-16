# Publicação completa na Vercel — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Disponibilizar a central e o mobile por HTTPS com persistência, fotos privadas e inferências atuais.

**Architecture:** Reutilizar o domínio existente, mantendo SQLite local e acrescentando Postgres em produção. Adaptar os modelos para CPU no servidor e seleção remota de evidências no Groq gratuito. A aplicação escolhe o modo explicitamente e não grava dados persistentes no sistema de arquivos da função.

**Tech Stack:** FastAPI, psycopg, Supabase Postgres/Storage, ONNX Runtime, Groq, Vercel Python.

**Spec:** `docs/superpowers/specs/2026-11-16-publicacao-vercel.md`

## Global Constraints

- Usar somente serviços gratuitos.
- Preservar a execução local e os materiais entregues pelas nove disciplinas.
- Chaves e senhas ficam apenas em variáveis do servidor ou arquivos locais ignorados.
- Nenhum projeto existente será alterado e dados locais pessoais não serão copiados automaticamente.
- Não há respostas históricas apresentadas como inferência atual.

## Review Focus

- Confirmação concorrente com contestação: nenhuma gravação parcial ou decisão antiga aceita.
- Reenvio de foto/pedido após perda de conexão: mesma identidade, sem duplicar o pedido.
- Falta de chave/serviço externo: erro claro sem persistência temporária ou inferência inventada.
- Troca de instância: decisão, foto e plano continuam disponíveis.
- Acesso anônimo: APIs, fotos e interface não expõem dados da demonstração.

### Task 1: Persistência Postgres e confirmação atômica

**Files:** `central/postgres.py`, `central/registros.py` (apenas nomes explícitos de colunas), `tests/test_postgres.py`, migração criada por CLI em `supabase/migrations/`.

**Interfaces:** `RepositorioPostgres(dsn)` herda os métodos de `Repositorio`; `confirmar_frontend(identificador)` valida e confirma na mesma transação. A conexão adapta os parâmetros SQL usados pelas rotinas existentes. Um advisory lock transacional serializa todas as escritas e protege o planejamento.

- [x] Escrever e executar testes que exponham dialeto, rollback, revisão invalidada e confirmação idempotente.
- [x] Implementar adaptador e schema privado, reutilizando a validação e a persistência original do Frontend em módulo isolado por chamada.
- [x] Verificar em Postgres real quando houver conta autorizada, inclusive concorrência de contestação/plano.

### Task 2: Modelos no servidor

**Files:** `central/ia_online.py`, `central/visao_online.py`, `scripts/preparar_modelos_online.py`, `tests/test_ia_online.py`, `tests/test_visao_online.py`, artefatos convertidos fora de `materiais/`.

**Interfaces:** `perguntar(texto, anterior=None) -> dict` retorna o contrato original, com modelo/modo identificados; `analisar_imagem(conteudo: bytes) -> dict` preserva o contrato do checkpoint. O script prepara artefatos reproduzíveis sem inserir chaves ou alterar os materiais originais.

- [x] Testar seleção estruturada, limites, indisponibilidade, escopo e rastreabilidade das respostas.
- [x] Implementar Groq com injeção da função de seleção no Assistente original e preservar a busca híbrida quando couber no pacote.
- [x] Exportar o checkpoint para ONNX e comparar escores/decisões com o original em imagens reais e controles.
- [x] Medir dependências e artefatos do pacote; validar inferência online somente com chave configurada.

### Task 3: Aplicação, fotos e implantação

**Files:** `central/app.py`, `central/imagens.py`, `central/storage.py`, `central/modulos.py`, requisitos/configuração Vercel, arquivos web de estado, testes, documentação e relatório.

**Interfaces:** `StorageFotos(url, chave).guardar(conteudo) -> dict` e `.ler(sha) -> bytes`, bucket privado `zelabairro-fotos`. Modo `GOV_RUNTIME=vercel`; banco `GOV_DATABASE_URL`; chave de gestão `GOV_MANAGER_KEY`; acesso privado `GOV_ACCESS_USER`/`GOV_ACCESS_PASSWORD`; `SUPABASE_URL`/`SUPABASE_SECRET_KEY`; `GROQ_API_KEY`.

- [x] Testar autenticação e modo nuvem sem configurações, sem criar pastas/bancos locais.
- [x] Integrar Postgres, fotos privadas e inferências; ajustar mensagens e estado dos módulos.
- [x] Configurar entrada, dependências e exclusões de arquivos não executáveis na função; materiais acadêmicos aprovados continuam acessíveis pelo repositório.
- [x] Executar testes existentes e novos, revisar diferenças e atualizar documentação sem alegar validações ainda pendentes.
- [x] Com organização e credenciais disponíveis, provisionar recursos gratuitos e variáveis secretas, publicar, acompanhar logs e testar fluxo pelo HTTPS.
