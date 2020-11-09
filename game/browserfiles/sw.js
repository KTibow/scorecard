var cacheName = 'clue-card-v{{version}}';
function log_message(message, color, object) {
  console.log(
    "%csw.js: %c" + message,
    object || "",
    "color: coral;",
    "color: " + color);
}
log_message("👋 Hello there!", "green");
self.addEventListener('install', (e) => {
    if (navigator.onLine) {
        log_message("⏭️ Online, not waiting.", "blue");
        self.skipWaiting();
    }
    log_message("⬇ Installing ...", "yellow");
    e.waitUntil(
        caches.open(cacheName).then((cache) => {
            log_message("⬇ Caching caches...", "coral", [{{urls}}]);
            return cache.addAll([{{urls}}]);
        })
    );
    e.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== cacheName) {
                    log_message("👋 See you later " + key, "coral");
                    return caches.delete(key);
                }
            }));
        })
    );
    log_message("✅ Done installing!", "green");
});
self.addEventListener('fetch', function(event) {
    log_message("🌎 We got a (no, not 🐟) fetch!", "blue", event.request);
    if (!event.request.url.includes("makeid") &&
        !event.request.url.includes("addid") &&
        !event.request.url.includes("gids") &&
        !event.request.url.includes("cardstatus")) {
        caches.open(cacheName).then(function(cache) {
            log_message("⬇ Caching for later use:", "green", event.request.url);
            cache.add(event.request.url);
        }).catch(function() {
            log_message("❌ Error caching", "red", event.request.url);
        });
    }
    event.respondWith(
        fetch(event.request).catch(function() {
            log_message("↩ Returning cache for", "blue", event.request.url);
            return caches.match(event.request.url).then(function(resty) {
                if (!resty) {
                    log_message("❌ Page not found:", "red", event.request.url);
                    return caches.match("/404")
                }
            })
        })
    );
});
