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
  // Publish content files separately from site styles and fonts.
  eleventyConfig.addPassthroughCopy({ "files": "files" });
  if (existsSync("CNAME")) eleventyConfig.addPassthroughCopy("CNAME");
  eleventyConfig.addFilter("year", () => new Date().getUTCFullYear());
  // Keep publication notes editable as · **Oral** in ordinary Markdown.
  eleventyConfig.addFilter("publicationNotes", (html, section) => section === "publications"
    ? html.replace(/·\s*<strong>([^<]+)<\/strong>/g,
      '· <strong class="publication-note">$1</strong>')
    : html);
  // Share date/body columns across Markdown lists without changing ordinary bullet lists.
  eleventyConfig.addFilter("datedLists", html => html.replace(/<ul>([\s\S]*?)<\/ul>/g, (list, items) => {
    const columns = items.replace(
      /<li><strong>([^<]+)<\/strong>\s*—\s*([\s\S]*?)<\/li>/g,
      '<li><strong>$1</strong><span>$2</span></li>'
    );
    return columns === items ? list : `<ul class="dated-list">${columns}</ul>`;
  }));
  eleventyConfig.addGlobalData("siteOrigin", process.env.SITE_URL || "https://shaoyuanlo.github.io");
  return {
    pathPrefix: process.env.PATH_PREFIX || "/",
    dir: { input: "src", output: process.env.ELEVENTY_OUTPUT || "_site" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
}
