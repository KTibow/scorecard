var cacheName = "escore-v5";
self.addEventListener('install', (e) => {
  console.log('[Service Worker] Install');
  e.waitUntil(
    caches.open(cacheName).then((cache) => {
      console.log('[Service Worker] Caching caches');
      return cache.addAll(['/', '/welcome.css', '/install.js',
                           '/sw.js', '/favicon.ico',
                           '/manifest.json', '/maskable_icon.png',
                           '/android-icon-192x192.png', '/ms-icon-310x310.png',
                           '/ms-icon-150x150.png', '/favicon-96x96.png',
                           '/favicon-16x16.png', 'favicon-32x32.png']);
    })
  );
});
self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((r) => {
          console.log('[Service Worker] Fetching resource: '+e.request.url);
      return r || fetch(e.request).then((response) => {
                return caches.open(cacheName).then((cache) => {
          console.log('[Service Worker] Caching new resource: '+e.request.url);
          cache.put(e.request, response.clone());
          return response;
        });
      });
    })
  );
});
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keyList) => {
          return Promise.all(keyList.map((key) => {
        if(key !== cacheName) {
          return caches.delete(key);
        }
      }));
    })
  );
});
