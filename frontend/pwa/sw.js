// Service Worker — Projeto Cidadão PWA
const CACHE_NAME = 'pc-v1';
const STATIC_ASSETS = ['/app', '/app/manifest.json'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  const { request } = e;
  const url = new URL(request.url);
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(fetch(request).then((resp) => { const clone = resp.clone(); caches.open(CACHE_NAME).then((cache) => cache.put(request, clone)); return resp; }).catch(() => caches.match(request)));
    return;
  }
  e.respondWith(caches.match(request).then((cached) => cached || fetch(request)));
});