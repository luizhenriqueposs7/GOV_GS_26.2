# Clareza da jornada: plano de execução

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** explicar a finalidade da central e permitir gravar um pedido real do protótipo com menos informação simultânea.

**Architecture:** reutilizar telas, rotas por hash, helpers e detalhes nativos; não alterar regras de domínio.

**Tech Stack:** HTML, CSS, JavaScript nativo e backend FastAPI existente.

**Spec:** docs/superpowers/specs/2026-11-17-clareza-jornada-design.md.

## Restrições

Preservar as nove disciplinas, revisão e contestação. Manter identidade visual, chave de gestão, confirmação, rascunho e URLs. Sem dependências ou serviços novos. Roteiro de 6min30s, dividido entre os três integrantes, com execução atual e simulações identificadas.

## Verificação

Mudança de grupo conserva seleção; hash direto abre a mesma função; detalhes recolhidos continuam acessíveis; pedido não perde estado em navegação; mobile não excede a largura e conserva campos em 16 px.

- [x] Reorganizar navegação, textos, consultas e detalhes em web/index.html, web/app.js, web/atendimento.mjs e web/style.css.
- [x] Verificar seleção contextual, abertura de lote/ferramentas e ciclo do pedido no navegador, além das regressões JavaScript existentes.
- [x] Reescrever docs/roteiro-video.md e criar os três roteiros individuais, com tempos, falas, cliques, arquivos e contingências honestas.
- [x] Registrar revisão rigorosa da entrega atual, sem atribuir nota a vídeo inexistente nem redigir a conclusão final.
Publicação: versão/cache preparados; o encerramento deve verificar os arquivos por HTTPS e o commit no repositório autorizado.
