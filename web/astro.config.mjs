import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://aguara-observatory.netlify.app",
  base: "/",
  integrations: [tailwind(), sitemap()],
  build: {
    assets: "_assets",
  },
});
