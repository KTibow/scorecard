var confirming = false;
var globreg;

function checkVersion(reg) {
    function listenForWaitingServiceWorker(reg, callback) {
        function awaitStateChange() {
            reg.installing.addEventListener('statechange', function() {
                if (this.state === 'installed') callback(reg);
            });
        }
        if (!reg) return;
        if (reg.waiting) return callback(reg);
        if (reg.installing) awaitStateChange();
        reg.addEventListener('updatefound', awaitStateChange);
    }
    var refreshing;
    navigator.serviceWorker.addEventListener('controllerchange',
        function() {
            if (refreshing) return;
            refreshing = true;
            window.location.reload();
        }
    );

    function promptUserToRefresh(reg) {
        console.log("I think it's time to update.");
        if (!confirming) {
            confirming = true;
            console.log("Confirming...");
            if (window.confirm("Refresh all tabs now and get the latest version of the ClueCard?")) {
                reg.waiting.postMessage('skipWaiting');
            }
            confirming = false;
        }
    }
    listenForWaitingServiceWorker(reg, promptUserToRefresh);
}
if ("serviceWorker" in navigator) {
    window.addEventListener("load", function() {
        navigator.serviceWorker
            .register("/sw.js")
            .then(function(reg) {
                console.log("Service worker: installed!");
                setInterval(5000, checkVersion, reg);
            }).catch (err => console.log("Service worker: not registered", err));
    });
}
window.addEventListener("load", function() {
    let deferredPrompt;
    const addBtn = document.getElementById("add2hs");
    const addAlt = document.getElementById("add2hsalt");
    addBtn.style.display = 'none';
    addAlt.style.display = 'none';
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault();
        // Stash the event so it can be triggered later.
        deferredPrompt = e;
        // Update UI to notify the user they can add to home screen
        addBtn.style.display = 'block';
        addAlt.style.display = 'block';
        addBtn.addEventListener('click', (e) => {
            // hide our user interface that shows our A2HS button
            addBtn.style.display = 'none';
            addAlt.style.display = 'none';
            // Show the prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the A2HS prompt');
                } else {
                    console.log('User dismissed the A2HS prompt');
                }
                deferredPrompt = null;
            });
        });
    });
});
