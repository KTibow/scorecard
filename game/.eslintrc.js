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
        username: "readonly",
        confetti: "readonly",
    },
    extends: "eslint:recommended",
    rules: {
        "no-unused-vars": "warn",
        camelcase: "warn",
    },
};
