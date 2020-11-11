module.exports = {
  ci: {
    collect: {
      url: ['Running on http://127.0.0.1:5000'],
      startServerCommand: 'python3 lighthouse_boot.py',
      startServerReadyPattern: 'Running on http://127.0.0.1:5000',
      startServerReadyTimeout: 5000
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
