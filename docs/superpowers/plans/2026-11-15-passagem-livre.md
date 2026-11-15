# Passagem Livre Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Demonstrar o efeito conjunto de reparos num percurso, ligado aos pedidos e à governança existentes.

**Architecture:** Avaliação determinística no servidor sobre quatro trechos e pedidos associados. Planos imutáveis na mesma base SQLite, com assinatura das entradas para detectar obsolescência. Interface responsiva reutiliza componentes, mapa Leaflet, câmera e rascunho atuais.

**Tech Stack:** Python/FastAPI/SQLite, JavaScript, Leaflet existente, unittest e node:test.

**Spec:** docs/superpowers/specs/2026-11-15-passagem-livre.md

## Global Constraints

- Sem novas dependências, rotas arbitrárias ou garantia de acessibilidade.
- Sem alteração destrutiva dos pedidos existentes ou preenchimento fictício de integração executável.
- Simulação não registra reparo nem muda a triagem/revisão dos pedidos.
- Preservar nove disciplinas, limites, roteiro de 6min30s e conclusão conjunta.

## Review Focus

- Trecho desconhecido não pode virar livre por um reparo selecionado.
- Contestação, edição ou nova revisão invalida a base do plano; salvamento concorrente deve rejeitar assinatura antiga.
- Pedido sem vínculo continua compatível; formulário, edição e rascunho conservam ou retiram o vínculo explicitamente.
- Preparar a demonstração repetidamente não duplica pedidos nem restaura conteúdo contestado.
- Em 390px, mapa e lista têm as mesmas condições textuais e controles operáveis por teclado.

### Task 1: Domínio, vínculo e plano auditável

**Files:** criar central/passagem.py, tests/test_passagem.py; modificar central/app.py e central/registros.py.

**Interfaces:** avaliar(casos: list[dict], reparos: list[str]) -> dict; validar_vinculo(vinculo: dict | None) -> dict | None. GET /api/passagem, POST /api/passagem/simular, /api/passagem/demonstracao e /api/passagem/planos. Campo opcional passagem nos pedidos. Planos com assinatura SHA-256 das entradas pertinentes e geometria do cenário.

- [x] Escrever testes: duas barreiras, reparo individual, conjunto, desconhecido, relatos repetidos, vínculo inválido, cenário sem pedidos e simulação sem efeitos colaterais.
- [x] Executar e observar falha; implementar o cálculo mínimo.
- [x] Escrever testes API com banco temporário: chave, seed idempotente, upload/edição/vínculo, revisão obrigatória, persistência, contestação e base obsoleta.
- [x] Executar e observar falha; implementar contratos, persistência e controle transacional.
- [x] Executar testes Python pertinentes e registrar resultado.

### Task 2: Central e mobile

**Files:** criar web/passagem.mjs; modificar web/index.html, app.js, mapa.mjs, mobile.mjs, style.css, sw.js; ampliar tests/mobile.test.mjs e tests/sw.test.mjs conforme necessário.

**Interfaces:** novo painel #passagem com lista acessível, trechos no mapa, seleção de reparos, comparação, decisão e histórico de planos. Formulário usa passagem-trecho e passagem-condicao; associação no resumo, edição e rascunho. Cache estático versionado inclui o módulo novo, sem cache de dados.

- [x] Testar antes a conservação dos campos no rascunho e conversão do vínculo opcional.
- [x] Implementar painel e mapa com identidade existente, sem inferência espacial automática.
- [x] Integrar vínculo ao envio, recibo, revisão, edição e recuperação de rascunho.
- [x] Conferir sintaxe e testes Node; testar no navegador desktop/390px o percurso completo e contestação.

### Task 3: Evidências e entrega

**Files:** README.md, docs/roteiro-video.md, docs/relatorio-base.md, docs/teste-celular.md, docs/progresso.md, docs/evidencias/passagem-livre-2026-11-15.md e relatório de trabalho se sua geração permanecer no limite de páginas.

- [x] Atualizar matriz de integração e roteiro mantendo todas as nove disciplinas e 6min30s.
- [x] Executar suíte existente, verificação funcional de HTTP e salvar capturas das telas reais.
- [x] Obter uma revisão final do conjunto por outro agente, corrigir achados relevantes e repetir apenas verificações afetadas.
- [x] Conferir diff e estado dos dados; registrar limites físicos e links ainda pendentes.

## Registro de execução

Ruling: executar na branch existente codex/central-citizentech — o pedido amplia a central já em preparação e o estado inicial está limpo; evita duplicar ambientes e bases locais.

Ruling: percurso didático esquemático, em vez de rota real levantada — não há inspeção de calçadas nem percurso fornecido; o aviso é permanente e a condição é sempre do cenário.

Execução: 71 testes Python, 19 Node, 4 validações PowerShell e sete verificações atuais das integrações passaram. CUA conferiu desktop e 390px, foto do acervo, ponto manual, rascunho, plano, contestação e foco. Quatro achados da revisão final corrigidos; evidências em docs/evidencias/passagem-livre-2026-11-15.md. Relatório regenerado com 14 páginas.
