/** @type {import('tailwindcss').Config} */
export default {
  content: ["src/**/*.svelte"],
  theme: {
    extend: {
      zIndex: {
        '1000': '1000',
        '1001': '1001',
      }
    },
  },
  plugins: [],
}
