module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:5000/'],
      startServerCommand: 'python3 lighthouse_boot.py',
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
