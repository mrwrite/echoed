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
        tertiary: "#D85A2B",
        warn: "#FF4C4C",
        success: "#00A86B",
        info: "#00A8FF",
        // Animal coloring palette
        giraffe: "#D2B48C",   // tan shade for giraffe body
        elephant: "#808080", // gray shade for elephant
        lion: "#C19A6B",     // brownish gold for lion fur
      },
      fontFamily: {
        sans: ['Inter','ui-sans-serif', 'system-ui'],
      }
    },
  },
  plugins: [],
}

