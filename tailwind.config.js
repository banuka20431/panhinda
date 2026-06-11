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
  darkMode: 'class', // or 'media' or false
}
