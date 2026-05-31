
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open("sports-pro-v1").then(cache => cache.addAll(["/", "/static/style.css", "/static/app.js"]))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
