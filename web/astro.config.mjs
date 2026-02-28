import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

const SITE = "https://watch.aguarascan.com";

export default defineConfig({
  site: SITE,
  base: "/",
  integrations: [
    tailwind(),
    sitemap(),
  ],
  build: {
    assets: "_assets",
  },
});
