import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";
import fs from "node:fs";
import path from "node:path";

const SITE = "https://watch.aguarascan.com";

// Build skill URLs from JSON files so they appear in the sitemap
// even though they're now client-side rendered via skill-viewer.
function getSkillUrls() {
  const skillsDir = path.join(process.cwd(), "public", "api", "v1", "skills");
  if (!fs.existsSync(skillsDir)) return [];
  const urls = [];
  for (const reg of fs.readdirSync(skillsDir)) {
    const regDir = path.join(skillsDir, reg);
    if (!fs.statSync(regDir).isDirectory()) continue;
    for (const file of fs.readdirSync(regDir)) {
      if (!file.endsWith(".json")) continue;
      const slug = file.replace(".json", "");
      urls.push(`${SITE}/skills/${reg}/${slug}/`);
    }
  }
  return urls;
}

export default defineConfig({
  site: SITE,
  base: "/",
  integrations: [
    tailwind(),
    sitemap({
      filter: (page) => !page.includes("/skill-viewer"),
      customPages: getSkillUrls(),
    }),
  ],
  build: {
    assets: "_assets",
  },
});
