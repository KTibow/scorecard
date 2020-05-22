if ("serviceWorker" in navigator) {
  window.addEventListener("load", function() {
    var reg = navigator.serviceWorker
      .register("/sw.js")
      .then(res => console.log("service worker registered"))
      .catch(err => console.log("service worker not registered", err));
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
    // reload once when the new Service Worker starts activating
    var refreshing;
    navigator.serviceWorker.addEventListener('controllerchange',
      function() {
        if (refreshing) return;
        refreshing = true;
        window.location.reload();
      }
    );
    function promptUserToRefresh(reg) {
      // this is just an example
      // don't use window.confirm in real life; it's terrible
      if (window.confirm("Refresh all tabs now and get the latest version of the ClueCard?")) {
        reg.waiting.postMessage('skipWaiting');
      }
    }
    listenForWaitingServiceWorker(reg, promptUserToRefresh);
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
