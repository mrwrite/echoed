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
        primary: "var(--echo-primary)",
        secondary: "var(--echo-secondary)",
        accent: "var(--echo-accent)",
        ink: "var(--echo-ink)",
        sand: "var(--echo-sand)",
        sky: "#49A2D6",
        warn: "#FF4C4C",
        success: "#1D9A6C",
        info: "#00A8FF",
        // Animal coloring palette
        giraffe: "#D2B48C",   // tan shade for giraffe body
        elephant: "#808080", // gray shade for elephant
        lion: "#C19A6B",     // brownish gold for lion fur
      },
      boxShadow: {
        elevated: '0 18px 40px -18px rgba(17, 24, 39, 0.25)',
        'soft-card': '0 12px 30px -12px rgba(15, 23, 42, 0.22)',
      },
      borderRadius: {
        xl: '18px',
        '2xl': '24px',
      },
      fontFamily: {
        sans: ['Inter','ui-sans-serif', 'system-ui'],
      }
    },
  },
  plugins: [],
}

