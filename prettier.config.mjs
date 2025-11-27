// prettier.config.js, .prettierrc.js, prettier.config.cjs, or .prettierrc.cjs

/**
 * @see https://prettier.io/docs/configuration
 * @type {import("prettier").Config}
 */
const config = {
  plugins: ['prettier-plugin-java', 'prettier-plugin-toml'],
  printWidth: 120,
  trailingComma: 'all',
  tabWidth: 4,
  semi: false,
  singleQuote: true,
  overrides: [
    {
      files: ['*.yaml', '*.yml', '*.json', '*.js', '*.jsx', '*.ts', '*.tsx', '*.cjs', '*.mjs'],
      options: {
        tabWidth: 2,
      },
    },
  ],
}

export default config
