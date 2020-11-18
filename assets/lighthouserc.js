module.exports = {
    ci: {
        collect: {
            url: [
                "http://127.0.0.1:5000",
                "http://127.0.0.1:5000/cluecard/test",
            ],
            startServerCommand: "python3 -m assets.lighthouse_boot",
            startServerReadyPattern: "Running on http://127.0.0.1:5000",
            startServerReadyTimeout: 5000,
        },
        upload: {
            target: "temporary-public-storage",
        },
    },
};
