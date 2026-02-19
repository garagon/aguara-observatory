import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  site: "https://aguara-observatory.netlify.app",
  base: "/",
  integrations: [tailwind()],
  build: {
    assets: "_assets",
  },
});
