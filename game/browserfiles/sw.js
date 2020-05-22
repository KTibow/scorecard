var cacheName = "clue-card-v1";
self.addEventListener('install', (e) => {
    console.log('Service Worker: Installing...');
    e.waitUntil(
        caches.open(cacheName).then((cache) => {
            console.log('Service Worker: Caching caches...');
            return cache.addAll(['/', '/welcome.css', '/install.js',
                '/sw.js', '/favicon.ico', '/manifest.json',
                '/maskable_icon.png', '/r_maskable_icon(1).png',
                '/r_maskable_icon(2).png', '/r_maskable_icon.png',
                '/favicon-16x16.png', 'favicon-32x32.png'
            ]);
        })
    );
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
self.addEventListener('activate', (e) => {
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
});
