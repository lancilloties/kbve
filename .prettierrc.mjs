/** @type {import("prettier").Config} */
export default {
	"printWidth": 80,
	"singleQuote": true,
	"useTabs": true,
	"tabWidth": 4,
	"semi": true,
	"bracketSpacing": true,
	"bracketSameLine":true,
	"htmlWhitespaceSensitivity": "ignore",
	plugins: ['prettier-plugin-astro'],
	overrides: [
	  {
		files: '*.astro',
		options: {
		  parser: 'astro',
		},
	  },
	],
  };