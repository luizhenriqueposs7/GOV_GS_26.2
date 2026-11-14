# ZelaBairro: implementação do visual e mapa

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Aplicar os mockups aprovados à central e à jornada móvel, com mapa e fluxo persistente de foto, localização, revisão e contestação.

**Architecture:** Manter FastAPI, SQLite e os contratos existentes. Adicionar Leaflet local para os mapas; coordenadas escolhidas no mapa são manuais e exigem confirmação. Reutilizar envio idempotente, redução de foto, rascunhos e decisões existentes.

**Tech Stack:** HTML/CSS, módulos JavaScript, Leaflet 1.9.4, FastAPI, SQLite.

**Spec:** ../../mockups-zelabairro-v2-2026-11-14.md; aprovação explícita do usuário nesta conversa em 14/11/2026.

## Global Constraints

- Manter os pedidos e os históricos existentes.
- Dados fictícios; nenhuma confirmação municipal ou detecção de buraco comprovada.
- Alternativas de texto, coordenadas digitadas e endereço sem GPS devem continuar disponíveis.
- Apenas tiles visíveis do OpenStreetMap, atribuição visível, sem cache offline ou prefetch de mapas.
- Reutilizar backend, proteção por chave e cache conjunto do formulário; não publicar acesso externo.

## Review Focus

- Mapa indisponível não impede preenchimento manual.
- Mudar coordenadas, arrastar ponto, editar ou recuperar rascunho exige confirmar o local outra vez.
- Pedido sem foto ou sem coordenadas continua acessível na lista e na revisão.
- Captura negada ou indisponível conserva a seleção de arquivo e o relato.
- Contestação conserva o histórico e bloqueia a confirmação até nova revisão.

### Task 1: localização e mapa

**Files:** web/mapa.mjs, web/vendor/leaflet.*, tests/mapa.test.mjs, central/app.py.
**Interfaces:** coordenadas confirmadas existentes; distanciasProximas(caso, casos, raio=100) retorna casos com distância em metros; mapa renderiza marcadores de pedidos reais.

- [x] Testar exclusão de coordenadas inválidas/ausentes, distância, limite, seleção e filtros.
- [x] Incorporar Leaflet com licença e CSP restrita ao tile.openstreetmap.org; manter Referer de origem.
- [x] Implementar seleção por clique/arraste e sincronização com coordenadas digitadas.

### Task 2: interface e jornada

**Files:** web/index.html, web/style.css, web/app.js, web/manifest.webmanifest, web/sw.js, web/brand.svg e ícones.
**Interfaces:** manter IDs e endpoints do app; três etapas Foto e relato, Localização, Conferência; mapa seleciona pedido e abre revisão/histórico.

- [x] Aplicar marca, tipografia, câmera com fallback e etapas navegáveis com validação.
- [x] Implementar central orientada ao mapa com busca, lista acessível e relatos próximos por distância, sem fusão automática.
- [x] Reorganizar revisão e acompanhamento em evidência, decisão e histórico, preservando consultas e lotes.
- [x] Atualizar PWA e cache conjunto, sem fotos/APIs/tiles no service worker.

### Task 3: verificação

**Files:** tests/test_mobile.py, tests/sw.test.mjs, docs/evidencias e nota de implementação.

- [x] Executar testes Python e Node apropriados.
- [x] Conferir desktop e mobile no navegador: upload, mapa, confirmação, revisão, ZelaBairro, contestação, nova revisão, edição e rascunho.
- [x] Conferir falhas de mapa, responsividade, foco e console. Registrar resultados e limites sem alegar teste em aparelho físico.

Execução nativa nesta sessão. Nenhuma migração de dados necessária. O relatório e a conclusão continuam fora desta revisão.

Verificação em 14/11/2026: 57 testes Python e 12 Node aprovados. Fluxo desktop/mobile e correções documentados em docs/evidencias/zelabairro-v2-2026-11-14.md. Revisão independente realizada; dois achados corrigidos.
