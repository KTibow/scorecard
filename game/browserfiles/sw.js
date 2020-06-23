var cacheName = 'clue-card-v{{version}}';
console.log('Service Worker: Hello there!');
self.addEventListener('install', (e) => {
    if (navigator.onLine) {
        console.log('Online, skip wait');
        self.skipWaiting();
    }
    console.log('Service Worker: Installing...');
    e.waitUntil(
        caches.open(cacheName).then((cache) => {
            console.log('Service Worker: Caching caches...');
            return cache.addAll([{{urls}}]);
        })
    );
    e.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== cacheName) {
                    console.log('Service Worker: Bye-Bye', key);
                    return caches.delete(key);
                }
            }));
        })
    );
    console.log('Service Worker: Done installing!');
});
self.addEventListener('fetch', function(event) {
    console.log('Service Worker: We got a (no, not fish) fetch!', event.request);
    if (!event.request.url.includes("makeid")) {
        caches.open(cacheName).then(function(cache) {
            console.log('Service Worker: Trying to cache', event.request.url + '...');
            cache.add(event.request.url);
        }).catch(function() {
            console.log('Error caching', event.request.url);
        });
    }
    event.respondWith(
        fetch(event.request).catch(function() {
            console.log('Service Worker: Returning cache for', event.request, '...');
            return caches.match(event.request.url).then(function(resty) {
                if (!resty) {
                    console.log("Not found");
                    return caches.match("/404")
                }
            })
        })
    );
});
