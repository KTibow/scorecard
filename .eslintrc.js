module.exports = {
    env: {
        browser: true,
        es2021: true,
    },
    parserOptions: {
        ecmaVersion: 12,
    },
    globals: {
        user_id: "readonly",
        confetti: "readonly",
    },
    extends: "plugin:prettier/recommended",
};
