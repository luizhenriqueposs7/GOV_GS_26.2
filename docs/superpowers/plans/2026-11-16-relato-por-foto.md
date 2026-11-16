# Relato por foto — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Executar neste chat, pois a implementação e publicação já foram solicitadas.

**Goal:** Foto e GPS geram uma prévia editável, registrada somente após confirmação.

**Architecture:** FastAPI analisa a imagem pelo Groq e assina a sugestão sem persistir dados. O navegador obtém GPS e região, e reutiliza o envio com anexo. O domínio existente conserva sugestão, correções e decisões no JSON já persistido, sem migração.

**Tech Stack:** Python, FastAPI, Pillow, HTTPX/urllib existentes; JavaScript nativo; Vercel e Supabase existentes.

**Spec:** docs/superpowers/specs/2026-11-16-relato-por-foto.md

## Global Constraints

- Somente serviços gratuitos; sem alteração de pesos ou materiais originais.
- Uma única confirmação final; nenhum pedido salvo durante geração.
- Região aproximada, sem inventar rua/número; acesso externo somente para GPS atual autorizado.
- Manter revisão, confirmação, contestação, rascunho e reenvio idempotente.

## Review Focus

- Imagem inconclusiva exige descrição humana e não fabrica ocorrência.
- Resposta atrasada após cancelar/trocar foto/tela não altera campos.
- GPS negado ou consulta indisponível preserva relato e permite correção manual.
- Prévia adulterada ou de outra foto é rejeitada antes da persistência.
- Modelo, texto original e foto ficam rastreáveis mesmo quando a pessoa corrige o relato.

## Task 1: Prévia de imagem e origem

Files: central/relato_foto.py, central/app.py, central/registros.py, tests/test_relato_foto.py.

- [x] Escrever testes para prévia sem gravação, EXIF removido, contratos, abstenção, falha e assinatura vinculada à foto; observar falhas.
- [x] Implementar gerar(conteudo), assinar/validar e /api/relato-foto. Guardar sugestao_foto no JSON/histórico pelo envio existente, rejeitando assinatura/foto divergentes.
- [x] Rodar testes novos e de cadastro/revisão/contestação.

## Task 2: Captura e conferência

Files: web/automatico.mjs, web/app.js, web/mobile.mjs, web/index.html, web/style.css, web/sw.js, tests/automatico.test.mjs.

- [x] Escrever testes para GPS atual, região, falha/negação, cancelamento e rascunho; observar falhas.
- [x] Implementar duas etapas, geração após foto, ponto/região corrigíveis e uma confirmação final. Preservar modo manual e edição; cancelar leituras anteriores e manter origem da prévia no rascunho.
- [x] Rodar testes Node/Python pertinentes e conferir no navegador móvel.

## Task 3: Verificação e publicação

Files: docs/publicacao-vercel.md, docs/teste-celular.md, docs/relatorio-base.md, README.md, docs/evidencias/relato-foto-2026-11-16.json.

- [x] Executar modelo real com imagem existente sem dados pessoais; verificar fluxo completo e casos de falha pelo navegador.
- [x] Revisar diff, rodar verificações relevantes e atualizar documentação/relatório mantendo 14 páginas e conclusão reservada.
- [x] Commit/push e acompanhar build. Verificar HTTPS com senha, sem bypass, e nova geração real; informar limites do teste físico.

Execução: 139 Python com PG/TLS e 25 Node; navegador móvel sintético e HTTPS com modelo real. Revisão independente confirmou correções de cancelamento, rascunho e leitura tardia. Evidências em docs/evidencias/relato-foto-local e relato-foto-https. Câmera/GPS físicos seguem com o integrante.
