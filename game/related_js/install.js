function log_message(message, color) {
    console.log(
        "%c install.js: %c" + message,
        "color: #ad50ff;",
        "color: " + color
    );
}
log_message("🔁 Getting ready to install service worker", "green");
window.addEventListener("load", function () {
    if ("serviceWorker" in navigator) {
        log_message("🔻 Installing...", "yellow");
        navigator.serviceWorker
            .register("/sw.js")
            .then(function () {
                log_message("✅ Done installing!", "green");
            })
            .catch(function () {
                log_message("❌ Error installing", "red");
            });
    }
    let deferredPrompt;
    var a2hs = document.createElement("button");
    a2hs.id = "a2hs";
    a2hs.classList.add("alt-button");
    a2hs.style.opacity = 0;
    a2hs.style.visibility = "hidden";
    a2hs.setAttribute("data-icon", "system_update_alt");
    document.body.appendChild(a2hs);
    window.addEventListener("beforeinstallprompt", (event) => {
        event.preventDefault();
        deferredPrompt = event;
        if (!document.body.innerText.includes("☹")) {
            a2hs.style.setProperty("opacity", "1", "important");
            a2hs.style.setProperty("visibility", "visible", "important");
        }
        a2hs.addEventListener("click", () => {
            a2hs.style.setProperty("opacity", "0", "important");
            a2hs.style.setProperty("visibility", "hidden", "important");
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === "accepted") {
                    log_message("📲 User accepted the A2HS prompt!", "green");
                } else {
                    log_message("❌ User dismissed the A2HS prompt.", "red");
                }
                deferredPrompt = null;
            });
        });
    });
});
