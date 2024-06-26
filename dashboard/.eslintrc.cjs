module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    "eslint:recommended",
    "plugin:@tanstack/eslint-plugin-query/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/typescript",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:storybook/recommended",
  ],
  ignorePatterns: [".eslintrc.cjs", "*.config.js"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    requireConfigFile: false,
    ecmaVersion: 2021,
    sourceType: "module",
    project: ["./tsconfig.app.json", "./tsconfig.node.json"],
    tsconfigRootDir: __dirname,
  },
  settings: {
    react: {
      version: "detect",
    },
  },
  plugins: [
    "react-refresh",
    "import",
    "react",
    "react-hooks",
    "@typescript-eslint",
  ],
  rules: {
    "no-duplicate-imports": "warn",
    "no-magic-numbers": [
      "error",
      {
        detectObjects: false,
        ignore: [-1, 0, 1, 2],
        ignoreArrayIndexes: true,
        ignoreDefaultValues: true,
      },
    ],
    "no-restricted-imports": [
      "error",
      {
        patterns: ["../../*"],
      },
    ],
    "no-shadow": "off",
    "no-underscore-dangle": ["error", { allow: ["__typename"] }],
    "no-unused-vars": "off",
    "no-use-before-define": "off",
    "react-refresh/only-export-components": [
      "warn",
      { allowConstantExport: true },
    ],
    "@typescript-eslint/prefer-optional-chain": "warn",
    "@typescript-eslint/consistent-type-imports": "warn",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-empty-function": "off",
    "@typescript-eslint/no-inferrable-types": "warn",
    "@typescript-eslint/no-shadow": ["warn", { ignoreTypeValueShadow: true }],
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      },
    ],
    "import/extensions": [
      "error",
      "ignorePackages",
      {
        js: "never",
        jsx: "never",
        ts: "never",
        tsx: "never",
      },
    ],
    "import/no-cycle": ["error", { ignoreExternal: true }],
    "import/no-extraneous-dependencies": [
      "error",
      {
        devDependencies: [
          "**/*{.,_}{test,spec}.{ts,tsx}",
          ".storybook/**",
          "src/stories/**",
        ],
      },
    ],
    "import/order": [
      "error",
      {
        groups: [
          ["builtin", "external"],
          "internal",
          "parent",
          ["index", "sibling"],
        ],
        "newlines-between": "always-and-inside-groups",
      },
    ],
    "import/prefer-default-export": "off",
    "react-hooks/exhaustive-deps": "warn",
    "react-hooks/rules-of-hooks": "error",
    "react/destructuring-assignment": "off",
    "react/jsx-filename-extension": [
      "error",
      {
        extensions: [".tsx"],
      },
    ],
    "react/jsx-key": ["error", { checkFragmentShorthand: true }],
    "react/jsx-props-no-spreading": "off",
    "react/prop-types": "off",
    "react/react-in-jsx-scope": "off",
    "react/require-default-props": "off",
  },
};
