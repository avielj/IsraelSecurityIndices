// Service Worker — Israel Security Indices Android PWA
// Provides minimal offline support and enables PWA install prompt.

const CACHE = "indices-v1";

// On install: cache the shell
self.addEventListener("install", event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE).then(cache =>
      cache.addAll(["./widget.html", "./manifest.json"])
    )
  );
});

// On activate: clean up old caches
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch strategy:
//   - data.json → network-first (always want fresh data)
//   - everything else → cache-first
self.addEventListener("fetch", event => {
  const url = event.request.url;

  if (url.includes("raw.githubusercontent.com")) {
    // Network-first for live data
    event.respondWith(
      fetch(event.request).catch(() =>
        caches.match(event.request)
      )
    );
    return;
  }

  // Cache-first for shell assets
  event.respondWith(
    caches.match(event.request).then(cached =>
      cached || fetch(event.request).then(response => {
        const clone = response.clone();
        caches.open(CACHE).then(cache => cache.put(event.request, clone));
        return response;
      })
    )
  );
});
