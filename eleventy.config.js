import { existsSync } from "node:fs";

export default function (eleventyConfig) {
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
