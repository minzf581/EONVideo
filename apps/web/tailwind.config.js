/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        finance: {
          ink: "#111827",
          muted: "#6B7280",
          line: "#E5E7EB",
          surface: "#F7F8FA",
          green: "#0F766E",
          blue: "#1D4ED8",
        },
      },
    },
  },
  plugins: [],
};

