var confirming = false;
var globreg;
console.log("Install.js running...");

function checkVersion(reg) {
    console.log("checkVersion started... (install.js)");

    function listenForWaitingServiceWorker(reg, callback) {
        function awaitStateChange() {
            console.log("Awaiting state change.");
            reg.installing.addEventListener('statechange', function() {
                if (this.state === 'installed') {
                    console.log("Prompting user to refresh.");
                    callback(reg);
                }
            });
        }
        if (!reg) {
            console.log("Error: Reg isn't working");
            return;
        }
        if (reg.waiting) {
            console.log("Prompting user to refresh.");
            return callback(reg);
        }
        if (reg.installing) {
            awaitStateChange();
        }
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
        console.log("I think it's time to update. (install.js)");
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
    console.log("Install.js getting ready to install service worker...");
    window.addEventListener("load", function() {
        console.log("Install.js trying to install service worker...");
        navigator.serviceWorker
            .register("/sw.js")
            .then(function(reg) {
                console.log("Service worker: installed! (install.js)", reg, checkVersion(reg), setInterval(5000, checkVersion, reg));
            }).
        catch (err => console.log("Service worker: not registered (install.js)", err));
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
                    console.log('User accepted the A2HS prompt (install.js)');
                } else {
                    console.log('User dismissed the A2HS prompt (install.js)');
                }
                deferredPrompt = null;
            });
        });
    });
});
