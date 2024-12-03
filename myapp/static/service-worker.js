// myapp/static/js/service-worker.js
const CACHE_NAME = 'music-cache-v1';
const CACHE_TYPES = ['audio/mpeg', 'image/jpeg', 'image/png'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
});

self.addEventListener('fetch', event => {
  if (!event.request.url.includes('/media/')) return;

  event.respondWith(
    caches.match(event.request).then(response => {
      if (response) return response;

      return fetch(event.request).then(response => {
        if (!response || response.status !== 200) return response;
        
        const contentType = response.headers.get('content-type');
        if (CACHE_TYPES.some(type => contentType?.includes(type))) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      });
    })
  );
});