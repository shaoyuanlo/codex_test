import Eleventy from '@11ty/eleventy';
import { execFileSync } from 'node:child_process';
import { cp, mkdir, readdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';

// This output is served from the generated site-preview branch by raw.githack.
// The normal GitHub Pages build and production URLs stay independent.
const repository = process.env.GITHUB_REPOSITORY || 'shaoyuanlo/codex_test';
if (!/^[\w.-]+\/[\w.-]+$/.test(repository)) throw new Error('Invalid GitHub repository');
const origin = 'https://raw.githack.com';
const output = '_preview';
const sourceCommit = process.env.GITHUB_SHA || execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
const version = sourceCommit.slice(0, 12);
const stablePrefix = `/${repository}/site-preview/`;
const prefix = `${stablePrefix}revisions/${version}/`;
process.env.PATH_PREFIX = prefix;
process.env.SITE_URL = origin;
process.env.ELEVENTY_OUTPUT = output;

await rm(output, { recursive: true, force: true });
await new Eleventy('src', output).write();

// Keep the page styled even when the proxy throttles separate CSS requests.
const stylesheet = await readFile('src/assets/style.css', 'utf8');
const galleryScript = await readFile('src/assets/gallery.js', 'utf8');
const fontStylesheet = (await readFile('src/assets/fonts/fonts.css', 'utf8'))
  .replaceAll('url(./', `url(${stablePrefix}assets/fonts/`);

async function rewrite(dir) {
  for (const file of await readdir(dir, { withFileTypes: true })) {
    const filename = path.join(dir, file.name);
    if (file.isDirectory()) {
      await rewrite(filename);
    } else if (filename.endsWith('.html')) {
      const html = await readFile(filename, 'utf8');
      // A raw-file proxy needs explicit filenames; it cannot resolve /lab/.
      const rewritten = html
        .replace(`<script src="${prefix}assets/gallery.js" defer></script>`,
          `<script data-preview-script="gallery">${galleryScript}</script>`)
        .replace(`<link rel="stylesheet" href="${prefix}assets/style.css">`,
          `<style data-preview-style="site">${stylesheet}</style>`)
        .replace(`<link rel="stylesheet" href="${prefix}assets/fonts/fonts.css">`,
          `<style data-preview-style="fonts">${fontStylesheet}</style>`)
        .replace(/(href|src|content)="([^"]*)"/g, (match, attr, value) => {
        if (value.startsWith(prefix) || value.startsWith(origin + prefix)) {
          const url = new URL(value, origin);
          if (url.pathname.endsWith('/')) url.pathname += 'index.html';
          return `${attr}="${value.startsWith(origin) ? url.href : url.pathname + url.search + url.hash}"`;
        }
        return match;
      }).replace('</head>', `  <meta name="preview-source" content="${sourceCommit}">\n  <meta name="robots" content="noindex, nofollow">\n</head>`);
      await writeFile(filename, rewritten);
    }
  }
}
await rewrite(output);
await writeFile(path.join(output, '.nojekyll'), '');
await writeFile(path.join(output, 'preview.json'), JSON.stringify({
  sourceCommit,
  generatedAt: new Date().toISOString(),
  stableUrl: `${origin}${stablePrefix}index.html`,
  url: `${origin}${prefix}index.html`
}, null, 2) + '\n');
// A new directory bypasses proxies that ignore query strings in cache keys.
// Snapshot pages link only to this revision; old revisions are removed on publish.
const entries = await readdir(output);
const snapshot = path.join(output, 'revisions', version);
await mkdir(snapshot, { recursive: true });
for (const entry of entries) {
  await cp(path.join(output, entry), path.join(snapshot, entry), { recursive: true });
}
// Fixed pages must link to fixed paths, so deleting an old revision cannot
// break their navigation. Proxy caches may delay when these pages refresh.
async function writeStablePages(dir) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.name === 'revisions') continue;
    const filename = path.join(dir, entry.name);
    if (entry.isDirectory()) await writeStablePages(filename);
    else if (filename.endsWith('.html')) {
      const html = await readFile(filename, 'utf8');
      await writeFile(filename, html.replaceAll(prefix, stablePrefix));
    }
  }
}
await writeStablePages(output);
console.log(`Fixed preview: ${origin}${stablePrefix}index.html`);
console.log(`Interactive preview: ${origin}${prefix}index.html`);
