# Cluster e Quântica operacionais — Implementation Plan

> Executar com superpowers:executing-plans. Especificação: docs/superpowers/specs/2026-11-17-cluster-quantica-operacionais.md.

**Goal:** Processar lotes com workers e apoiar a seleção de revisões por capacidade.

**Architecture:** Reutilizar pipeline RPA, repositórios/eventos e revisão. Cluster coordena workers; planejamento calcula sobre snapshot e persiste decisão humana. Sem tabelas/dependências novas.

**Tech Stack:** Python, FastAPI, HTTPX, NumPy, SQLite/Postgres e módulos JS existentes.

- [x] RED/GREEN: partição por ID, equivalência serial, rejeitados/duplicados, falha de worker e autenticação; gravar lote atomicamente nos repositórios existentes.
- [x] RED/GREEN: evolução unitária, normalização, estado factível, orçamento/obrigatórios, comparação clássica, snapshot e persistência de plano sem decidir casos.
- [x] Interface responsiva, acesso pelos módulos, controles protegidos e continuidade para revisão. Atualizar catálogo/cache/versão.
- [x] Testes de domínio/API/Postgres e navegador; revisão independente; documentação/relatório de 14 páginas com limites explícitos.
- [ ] Publicar GitHub/Vercel e testar workers HTTP e planejamento no HTTPS.
