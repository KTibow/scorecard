module.exports = {
    ci: {
        collect: {
            url: ["http://127.0.0.1:5000"],
            startServerCommand: "python3 lighthouse_boot.py",
            startServerReadyPattern: "Running on http://127.0.0.1:5000",
            startServerReadyTimeout: 5000,
            puppeteerScript: "login-script.js"
        },
        upload: {
            target: "temporary-public-storage",
        },
    },
};
