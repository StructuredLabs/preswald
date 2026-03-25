const CACHE_NAME = "preswald-pyodide-v1";
const PYODIDE_CDN = "cdn.jsdelivr.net/pyodide/";

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name.startsWith("preswald-pyodide-") && name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  );
});

self.addEventListener("fetch", (event) => {
  const url = event.request.url;

  if (!url.includes(PYODIDE_CDN)) {
    return;
  }

  const iscacheable =
    url.includes(PYODIDE_CDN) &&
    (url.endsWith(".wasm") || url.endsWith(".mjs") || url.endsWith(".js") || url.endsWith(".json"));

  if (!iscacheable) {
    return;
  }

  event.respondWith(
    caches.open(CACHE_NAME).then((cache) =>
      cache.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then((networkResponse) => {
          if (networkResponse.ok) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        });
      })
    )
  );
});
