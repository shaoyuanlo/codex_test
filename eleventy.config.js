import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import matter from "gray-matter";

export default function (eleventyConfig) {
  // Share the homepage front matter across all pages; read again on each build.
  eleventyConfig.addGlobalData("site", async () => {
    const source = await readFile(new URL("./src/home.md", import.meta.url), "utf8");
    const website = matter(source).data.website;
    // Reuse the social Email address in contact links elsewhere on the site.
    const email = website.social.find(link => link.url.startsWith("mailto:"))?.url.slice(7);
    return { ...website, email };
  });
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  // Keep existing paper, slide, and file URLs when migrating the old website.
  for (const directory of ["files", "papers", "talks"]) {
    if (existsSync(directory)) eleventyConfig.addPassthroughCopy({ [directory]: directory });
  }
  if (existsSync("CNAME")) eleventyConfig.addPassthroughCopy("CNAME");
  eleventyConfig.addFilter("year", () => new Date().getUTCFullYear());
  // Keep publication notes editable as · **Oral** in ordinary Markdown.
  eleventyConfig.addFilter("publicationNotes", (html, section) => section === "publications"
    ? html.replace(/·\s*<strong>([^<]+)<\/strong>/g,
      '· <strong class="publication-note">$1</strong>')
    : html);
  eleventyConfig.addGlobalData("siteOrigin", process.env.SITE_URL || "https://shaoyuanlo.github.io");
  return {
    pathPrefix: process.env.PATH_PREFIX || "/",
    dir: { input: "src", output: process.env.ELEVENTY_OUTPUT || "_site" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
}
