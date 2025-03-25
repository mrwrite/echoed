/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts,scss}",
    "./.storybook/**/*.{ts,js}",
    "./stories/**/*.{ts,js}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2E294E",
        accent: "#EFB700",
        warn: "#D85A2B",
      },
    },
  },
  plugins: [],
}

