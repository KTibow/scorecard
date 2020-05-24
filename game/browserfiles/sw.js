var cacheName = "clue-card-v4";
console.log("Service Worker: Hello there!");
self.addEventListener('install', (e) => {
    console.log('Service Worker: Installing...');
    e.waitUntil(
        caches.open(cacheName).then((cache) => {
            console.log('Service Worker: Caching caches...');
            return cache.addAll(['/', '/open-sans.woff',
                '/open-sans.woff2', '/open-sans.svg', '/open-sans.eot',
                '/open-sans.ttf', '/sw.js', '/favicon-64x64.png',
                '/android-icon-144x144.png', '/ms-icon-310x310.png',
                '/android-icon-96x96.png', '/favicon-512x512.png',
                '/android-icon-192x192.png', '/apple-icon.png',
                '/favicon-32x32.png', '/manifest.json',
                '/android-icon-36x36.png', '/favicon-118x118.png',
                '/favicon-96x96.png', '/apple-icon-76x76.png',
                '/favicon-16x16.png', '/ms-icon-150x150.png',
                '/favicon-80x80.png', '/ms-icon-144x144.png',
                '/apple-icon-152x152.png', '/favicon-1000x1000.png',
                '/apple-icon-120x120.png', '/apple-icon-precomposed.png',
                '/apple-icon-114x114.png', '/apple-icon-60x60.png',
                '/apple-icon-72x72.png', '/apple-icon-57x57.png',
                '/robots.txt', '/ms-icon-70x70.png',
                '/apple-icon-180x180.png', '/android-icon-48x48.png',
                '/browserconfig.xml', '/favicon.ico',
                '/android-icon-72x72.png', '/apple-icon-144x144.png',
                '/welcome.css'
            ]);
        })
    );
    e.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== cacheName) {
                    console.log("Service Worker: Bye-Bye " + key);
                    return caches.delete(key);
                }
            }));
        })
    );
    console.log("Service Worker: Done installing!");
});
self.addEventListener('fetch', function(event) {
    console.log("Service Worker: We got a (no, not fish) fetch! " + event.request.url);
    caches.open(cacheName).then(function(cache) {
            console.log('Service Worker: Trying to cache ' + event.request.url + '...');
            cache.add(event.request.url);
        }).catch(function() {return;});
    event.respondWith(
        fetch(event.request).catch(function() {
            console.log('Service Worker: Returning cache ' + event.request.url + '...');
            return caches.match(event.request);
        })
    );
});
addEventListener('message', messageEvent => {
  if (messageEvent.data === 'skipWaiting') return skipWaiting();
});
