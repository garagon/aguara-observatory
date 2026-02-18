import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  site: "https://garagon.github.io",
  base: "/aguara-observatory",
  integrations: [tailwind()],
  build: {
    assets: "_assets",
  },
});
