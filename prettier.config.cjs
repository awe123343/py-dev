// prettier.config.js, .prettierrc.js, prettier.config.cjs, or .prettierrc.cjs

/**
 * @see https://prettier.io/docs/configuration
 * @type {import("prettier").Config}
 */
const config = {
  plugins: ['prettier-plugin-java', 'prettier-plugin-toml'],
  printWidth: 120,
  trailingComma: 'es5',
  tabWidth: 4,
  semi: false,
  singleQuote: true,
  overrides: [
    {
      files: ['*.yaml', '*.json', '*.js', '*.jsx', '*.ts', '*.tsx', '*.cjs'],
      options: {
        tabWidth: 2,
      },
    },
  ],
}

module.exports = config
