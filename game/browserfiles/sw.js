var cacheName = "clue-card-v{{version}}";
function logMessage(message, color, object) {
    console.log(
        "%c sw.js: %c" + message,
        "color: orange;",
        "color: " + color,
        object || ""
    );
}
logMessage("👋 Hello there!", "green");
self.addEventListener("install", (e) => {
    if (navigator.onLine) {
        logMessage("⏭️ Online, not waiting.", "darkslateblue");
        self.skipWaiting();
    }
    logMessage("🔻 Installing...", "yellow");
    e.waitUntil(
        caches.open(cacheName).then((cache) => {
            var cacheUrls = Function("return ([{{urls}}])")();
            logMessage("⬇ Caching caches...", "coral", cacheUrls);
            return cache.addAll(cacheUrls);
        })
    );
    e.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(
                keyList.map((key) => {
                    if (key !== cacheName) {
                        logMessage("👋 See you later " + key, "coral");
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    logMessage("✅ Done installing!", "green");
});
self.addEventListener("fetch", function (event) {
    var shouldCache = event.request.url.split("/").pop(-1).includes(".");
    var messageToLog = "🌎 We got a (no, not fish) fetch! ";
    if (shouldCache) {
        messageToLog += "Caching it for later use.";
    } else {
        messageToLog += "Not caching non-file call.";
    }
    messageToLog += " URL: ";
    messageToLog += event.request.url.split("com")[1];
    messageToLog += "\n";
    logMessage(messageToLog, "slateblue", event.request);
    if (shouldCache) {
        caches
            .open(cacheName)
            .then(function (cache) {
                cache.add(event.request.url);
            })
            .catch(function () {
                logMessage("❌ Error caching", "red", event.request.url);
            });
    }
    event.respondWith(
        fetch(event.request).catch(function () {
            logMessage("↩ Returning cache for", "blue", event.request.url);
            return caches.match(event.request.url).then(function (resty) {
                if (!resty) {
                    logMessage("❌ Page not found:", "red", event.request.url);
                    return caches.match("/404");
                }
            });
        })
    );
});
