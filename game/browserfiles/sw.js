var cacheName = "clue-card-v{{version}}";
function log_message(message, color, object) {
    console.log(
        "%c sw.js: %c" + message,
        "color: orange;",
        "color: " + color,
        object || ""
    );
}
log_message("👋 Hello there!", "green");
self.addEventListener("install", (e) => {
    if (navigator.onLine) {
        log_message("⏭️ Online, not waiting.", "darkslateblue");
        self.skipWaiting();
    }
    log_message("🔻 Installing...", "yellow");
    e.waitUntil(
        caches.open(cacheName).then((cache) => {
            var cache_urls = eval("[{{urls}}]");
            log_message("⬇ Caching caches...", "coral", cache_urls);
            return cache.addAll(cache_urls);
        })
    );
    e.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(
                keyList.map((key) => {
                    if (key !== cacheName) {
                        log_message("👋 See you later " + key, "coral");
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    log_message("✅ Done installing!", "green");
});
self.addEventListener("fetch", function (event) {
    var shouldCache =
        !event.request.url.includes("makeid") &&
        !event.request.url.includes("addid") &&
        !event.request.url.includes("gids") &&
        !event.request.url.includes("cardstatus");
    log_message(
        "🌎 We got a (no, not fish) fetch! " + shouldCache
            ? "Caching it for later use."
            : "Not caching API call.",
        "slateblue",
        event.request
    );
    if (shouldCache) {
        caches
            .open(cacheName)
            .then(function (cache) {
                cache.add(event.request.url);
            })
            .catch(function () {
                log_message("❌ Error caching", "red", event.request.url);
            });
    }
    event.respondWith(
        fetch(event.request).catch(function () {
            log_message("↩ Returning cache for", "blue", event.request.url);
            return caches.match(event.request.url).then(function (resty) {
                if (!resty) {
                    log_message("❌ Page not found:", "red", event.request.url);
                    return caches.match("/404");
                }
            });
        })
    );
});
