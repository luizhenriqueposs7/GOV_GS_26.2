'use strict';
// Atualize a versão ao publicar mudanças no conjunto estático abaixo.
const CACHE = 'citizentech-formulario-v18';
const ARQUIVOS = ['/', '/web/style.css', '/web/app.js', '/web/mobile.mjs', '/web/automatico.mjs', '/web/mapa.mjs', '/web/passagem.mjs', '/web/atendimento.mjs', '/web/ouviai.mjs', '/web/brand.svg', '/web/vendor/leaflet.js', '/web/vendor/leaflet.css', '/web/vendor/archivo-regular.ttf', '/web/vendor/archivo-bold.ttf', '/web/manifest.webmanifest', '/web/icon-192.png', '/web/icon-512.png'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ARQUIVOS)));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(chaves => Promise.all(chaves.filter(k => k.startsWith('citizentech-formulario-') && k !== CACHE).map(k => caches.delete(k)))));
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  // Somente o formulário estático: nenhuma API, foto ou resposta fica no cache.
  if (event.request.method !== 'GET' || url.origin !== self.location.origin || url.search || !ARQUIVOS.includes(url.pathname)) return;
  event.respondWith(caches.open(CACHE).then(cache => cache.match(url.pathname))
    .then(resposta => resposta || fetch(event.request)));
});
