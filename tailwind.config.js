/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/pages/**/*.jpy',
    './app/pages/**/*.html',
    './app/templates/**/*.html',
    './app/assets/**/*.js',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
    require('@tailwindcss/typography'),
  ],
  daisyui: {
    themes: ['light', 'dark', 'cupcake'],
  },
};
