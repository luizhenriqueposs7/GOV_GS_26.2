# OuviAí com áudio Implementation Plan

> **For agentic workers:** usar execução sequencial; manter o trabalho nesta conversa.

**Goal:** captar áudio de verdade e transformá-lo em avisos visuais locais, identificando o modelo alternativo.

**Architecture:** Web Audio + AudioWorklet captura PCM; worker executa MediaPipe/YAMNet hospedado no mesmo site. UI mantém eventos locais e separa simulação manual.

**Tech Stack:** JavaScript nativo, WebAssembly, FastAPI estático, Node test e Playwright CLI.

**Spec:** docs/superpowers/specs/2026-11-17-ouviai-audio-design.md

## Restrições e pontos de revisão

Sem áudio transmitido/armazenado. Sem custos. Sem chamar o modelo alternativo de CNN original. Sem alterar pedidos ou APIs de escrita. Escuta encerra inclusive em permissão tardia, navegação, aba oculta, falha de worker e retirada do microfone. Resultado ambíguo não vira alerta positivo.

## Execução

- [x] Criar testes de interpretação de categorias, pontuações inválidas e ambiguidade; executar falha antes do código em tests/ouviai-audio.test.mjs.
- [x] Implementar web/ouviai-audio.mjs, web/ouviai-worker.js e web/ouviai-captura.js; assets oficiais fixados com licença e hash em public/ouviai, entregues pela CDN.
- [x] Integrar escuta/parada, status e diário em web/ouviai.mjs e HTML/CSS; cancelar no navegar de web/app.js. Preservar simularSom/conectar e seus testes.
- [x] Permitir compilação WASM na CSP; manter script-src sem unsafe-eval; atualizar SW e versão.
- [x] Testar modelo real com áudio identificado e microfone virtual no Chrome, negativa de permissão e parada/navegação. Conferir layout móvel. WebKit Windows sem APIs de áudio: conferida orientação de indisponibilidade, sem alegar inferência ou teste físico no iPhone.
- [x] Atualizar catálogo e materiais que descrevem simulação, roteiro de Luis e empacotamento. Não substituir o clipe antigo com legenda de execução real.
- [ ] Rodar suites adequadas, revisão focada, publicar e verificar modelo/fluxo no HTTPS oficial.
