import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://watch.aguarascan.com",
  base: "/",
  integrations: [tailwind(), sitemap()],
  build: {
    assets: "_assets",
  },
});
