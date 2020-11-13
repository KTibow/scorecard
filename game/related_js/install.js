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
            .then(function (reg) {
                log_message("✅ Done installing!", "green");
            })
            .catch(function (err) {
                log_message("❌ Error installing", "red");
            });
    }
    let deferredPrompt;
    const addBtn = document.getElementById("add2hs");
    window.addEventListener("beforeinstallprompt", (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault();
        // Stash the event so it can be triggered later.
        deferredPrompt = e;
        // Update UI to notify the user they can add to home screen
        addBtn.style.setProperty("opacity", "1", "important");
        addBtn.style.setProperty("visibility", "visible", "important");
        addBtn.addEventListener("click", (e) => {
            // hide our user interface that shows our A2HS button
            addBtn.style.setProperty("opacity", "0", "important");
            addBtn.style.setProperty("visibility", "hidden", "important");
            // Show the prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === "accepted") {
                    log_message("📲 User accepted the A2HS prompt!", "green");
                } else {
                    log_message("❌ User dismissed the A2HS prompt", "red");
                }
                deferredPrompt = null;
            });
        });
    });
});
