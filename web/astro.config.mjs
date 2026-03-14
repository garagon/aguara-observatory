import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

const SITE = "https://watch.aguarascan.com";

export default defineConfig({
  site: SITE,
  base: "/",
  integrations: [
    tailwind(),
    sitemap({
      changefreq: "daily",
      lastmod: new Date(),
      priority: 0.7,
    }),
  ],
  build: {
    assets: "_assets",
  },
});
