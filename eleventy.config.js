import { existsSync } from "node:fs";

export default function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  // Keep existing paper, slide, and file URLs when migrating the old website.
  for (const directory of ["files", "papers", "talks"]) {
    if (existsSync(directory)) eleventyConfig.addPassthroughCopy({ [directory]: directory });
  }
  if (existsSync("CNAME")) eleventyConfig.addPassthroughCopy("CNAME");
  eleventyConfig.addFilter("year", () => new Date().getUTCFullYear());
  // Keep publication notes editable as [**Oral**] in ordinary Markdown.
  eleventyConfig.addFilter("publicationNotes", (html, section) => section === "publications"
    ? html.replace(/\[<strong>([^<]+)<\/strong>\]/g,
      '<span class="publication-note">[<strong>$1</strong>]</span>')
    : html);
  eleventyConfig.addFilter("dateLabel", date => new Intl.DateTimeFormat("en", {
    year: "numeric", month: "long", day: "numeric", timeZone: "UTC"
  }).format(new Date(date)));
  eleventyConfig.addFilter("isoDate", date => new Date(date).toISOString().slice(0, 10));
  eleventyConfig.addCollection("writing", collection => collection.getFilteredByTag("posts")
    .filter(post => post.data.published !== false)
    .sort((a, b) => b.date - a.date));
  eleventyConfig.addGlobalData("siteOrigin", process.env.SITE_URL || "https://shaoyuanlo.github.io");
  return {
    pathPrefix: process.env.PATH_PREFIX || "/",
    dir: { input: "src", output: process.env.ELEVENTY_OUTPUT || "_site" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
}
