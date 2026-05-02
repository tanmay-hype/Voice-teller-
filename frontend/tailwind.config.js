/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pastel: {
          pink: '#ff6b9a',
          'pink-600': '#ff4d7a',
          mint: '#88e0c3',
          lavender: '#d6c8ff',
          peach: '#ffd6cc',
          blush: '#fff1f3'
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
}