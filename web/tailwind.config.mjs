/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}"],
  theme: {
    extend: {
      colors: {
        aguara: {
          50: "#fef7ee",
          100: "#fdead7",
          200: "#f9d0ae",
          300: "#f5af7a",
          400: "#f08844",
          500: "#ec6a1f",
          600: "#dd5115",
          700: "#b73c13",
          800: "#923118",
          900: "#762b16",
          950: "#401309",
        },
      },
    },
  },
  plugins: [],
};
