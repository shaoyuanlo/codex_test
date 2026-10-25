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
  // Number year-grouped publications in reverse order; preprints use a separate p-series.
  eleventyConfig.addFilter("publicationIndexes", (html, section) => {
    if (section !== "publications") return html;
    const groups = html.split(/(?=<h2\b)/);
    let remaining = groups.filter(group => /^<h2\b[^>]*>\d{4}<\/h2>/.test(group))
      .reduce((total, group) => total + (group.match(/<h3\b/g) || []).length, 0);
    let preprint = 0;
    return groups.map(group => {
      const heading = group.match(/^<h2\b[^>]*>(.*?)<\/h2>/)?.[1];
      const isPreprint = heading?.toLowerCase() === "preprints";
      if (!isPreprint && !/^\d{4}$/.test(heading || "")) return group;
      return group.replace(/(<h3\b[^>]*>)([\s\S]*?)(<\/h3>)([\s\S]*?)(?=<h3\b|$)/g,
        (_, opening, title, closing, details) => {
          const index = isPreprint ? `p${++preprint}` : String(remaining--);
          const headingTag = opening.replace(/>$/, ` data-publication-index="${index}">`);
          return `${headingTag}<span class="publication-index">[${index}]</span> ${title}${closing}`
            + details.replace(/<p>/g, '<p class="publication-info">');
        });
    }).join("");
  });
  // Share date/body columns across Markdown lists without changing ordinary bullet lists.
  eleventyConfig.addFilter("datedLists", html => html.replace(/<ul>([\s\S]*?)<\/ul>/g, (list, items) => {
    const columns = items.replace(
      /<li><strong>([^<]+)<\/strong>\s*—\s*([\s\S]*?)<\/li>/g,
      '<li><strong>$1</strong><span>$2</span></li>'
    );
    return columns === items ? list : `<ul class="dated-list">${columns}</ul>`;
  }));
  // Balance sponsor rows at build time; CSS handles narrower screens without client-side scripts.
  eleventyConfig.addFilter("balancedSponsors", html => html.replace(
    /<div class="sponsors">([\s\S]*?)<\/div>/g,
    (container, contents) => {
      const figures = contents.match(/<figure>[\s\S]*?<\/figure>/g) || [];
      if (!figures.length) return container;
      const rowCount = Math.ceil(figures.length / 5);
      const rowSize = Math.floor(figures.length / rowCount);
      const extra = figures.length % rowCount;
      let offset = 0;
      const rows = Array.from({ length: rowCount }, (_, index) => {
        const size = rowSize + (index < extra ? 1 : 0);
        const row = figures.slice(offset, offset + size).join("\n");
        offset += size;
        return `<div class="sponsor-row">${row}</div>`;
      });
      return `<div class="sponsors">${rows.join("\n")}</div>`;
    }
  ));
  eleventyConfig.addGlobalData("siteOrigin", process.env.SITE_URL || "https://shaoyuanlo.github.io");
  return {
    pathPrefix: process.env.PATH_PREFIX || "/",
    dir: { input: "src", output: process.env.ELEVENTY_OUTPUT || "_site" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
}
