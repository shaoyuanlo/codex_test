export default {
  layout: "layouts/post.njk",
  tags: ["posts"],
  section: "blog",
  eleventyComputed: {
    permalink: data => data.published === false ? false : `/blog/${data.page.fileSlug}/index.html`,
    eleventyExcludeFromCollections: data => data.published === false
  }
};
