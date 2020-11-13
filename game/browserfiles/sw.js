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
            var cache_urls = Function("return ([{{urls}}])")();
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
    var shouldCache = event.request.url.includes(".");
    message_to_log = "🌎 We got a (no, not fish) fetch! ";
    if (shouldCache) {
        message_to_log += "Caching it for later use.";
    } else {
        message_to_log += "Not caching non-file call.";
    }
    message_to_log += "\n";
    log_message(message_to_log, "slateblue", event.request);
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
