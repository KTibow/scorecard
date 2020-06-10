var cacheName = "clue-card-vINSERT VERSION";
console.log("Service Worker: Hello there!");
var alreadyinstalled = false;
self.addEventListener('install', (e) => {
    alreadyinstalled = true;
    console.log('Service Worker: Installing...');
    e.waitUntil(
        caches.open(cacheName).then((cache) => {
            console.log('Service Worker: Caching caches...');
            return cache.addAll([INSERT URLS]);
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
if (!alreadyinstalled) {
    console.log('Service Worker: Cache stuff...');
    caches.open(cacheName).then((cache) => {
        console.log('Service Worker: Caching caches...');
        return cache.addAll([INSERT URLS]);
    })
    if (!alreadyinstalled) {
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== cacheName) {
                    console.log("Service Worker: Bye-Bye " + key);
                    return caches.delete(key);
                }
            }));
        })
        console.log("Service Worker: Done with cache stuff!");
    }
}
