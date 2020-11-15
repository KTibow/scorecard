module.exports = {
    env: {
        browser: true,
        es2021: true,
    },
    parserOptions: {
        ecmaVersion: 12,
    },
    globals: {
        userIdString: "readonly",
        confetti: "readonly",
    },
    extends: "plugin:prettier/recommended",
};
