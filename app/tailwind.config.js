/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        forest: {
          50:  "#f0f7f0",
          100: "#dceddc",
          200: "#bcdabc",
          300: "#8fbf8f",
          400: "#5fa05f",
          500: "#3d823d",
          600: "#2d6830",
          700: "#245226",
          800: "#1e4220",
          900: "#1a361c",
          950: "#0d1f0f",
        },
        bark: {
          100: "#f5ede3",
          200: "#e8d5bc",
          300: "#d4b48a",
          400: "#b8895a",
          500: "#956c3e",
          600: "#7a5530",
          700: "#614225",
          800: "#4d331d",
          900: "#3d2817",
        },
      },
    },
  },
  plugins: [],
};
