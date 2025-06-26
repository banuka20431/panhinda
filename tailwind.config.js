module.exports = {
  // ...
  safelist: [
    {
      pattern: /brand-(green|amber|red|grey)-[0-9]{3}/,
    },
  ],
  content: [
    './templates/**/*.html',    // Flask templates
    './app/**/*.html',          // If you store templates here
    './static/**/*.js',         // JS with classnames
    './static/**/*.css',        // Optional: utility classes in custom CSS
  ],
  theme: {
    extend: {
      fontSize: {
        '100px': '100px', // Optional: Named font size
      },
      fontFamily: {
        caveat: ['"Caveat"', 'cursive'], // Optional if using @font-face or Google Fonts
      },
    },
  },
  darkMode: 'class', // or 'media' or false
  plugins: [],
}
