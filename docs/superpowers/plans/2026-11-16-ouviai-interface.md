# Interface OuviAí — Implementation Plan

> Executar com superpowers:executing-plans, seguindo as tarefas abaixo.

**Goal:** Apresentar e demonstrar um possível dispositivo OuviAí na central e no mobile.

**Architecture:** Um módulo estático reutiliza os elementos e a navegação existentes. Estado demonstrativo fica somente na memória da aba; nenhuma API ou dependência nova.

**Tech Stack:** HTML, CSS, SVG e JavaScript ES modules; node:test e navegador real.

**Spec:** docs/superpowers/specs/2026-11-16-ouviai-interface.md.

- [x] Testar primeiro classes válidas, ambiente sem alerta, desconexão/reconexão, conservação de eventos e limite da lista.
- [x] Criar web/ouviai.mjs, tela e estilo responsivo; conectar entradas, hash e cache estático v18. Preservar os fluxos atuais.
- [x] Conferir desktop/mobile, teclado, aviso de simulação e ausência de POST/microfone. Atualizar descrição do material e instruções.
- [ ] Revisar, publicar e verificar a tela pelo HTTPS; entregar imagem de prévia e link direto.

Riscos a verificar: nenhum estado pode parecer telemetria real; ambiente não comprova ausência de perigo; conexão simulada não é conexão de hardware; tela sem rede não pode bloquear a navegação; textos longos não devem ultrapassar o celular.
