import Eleventy from '@11ty/eleventy';
import { execFileSync } from 'node:child_process';
import { readdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';

// This output is served from the generated site-preview branch by raw.githack.
// The normal GitHub Pages build and production URLs stay independent.
const repository = process.env.GITHUB_REPOSITORY || 'shaoyuanlo/codex_test';
if (!/^[\w.-]+\/[\w.-]+$/.test(repository)) throw new Error('Invalid GitHub repository');
const prefix = `/${repository}/site-preview/`;
const origin = 'https://raw.githack.com';
const output = '_preview';
process.env.PATH_PREFIX = prefix;
process.env.SITE_URL = origin;
process.env.ELEVENTY_OUTPUT = output;

await rm(output, { recursive: true, force: true });
await new Eleventy('src', output).write();

async function rewrite(dir) {
  for (const file of await readdir(dir, { withFileTypes: true })) {
    const filename = path.join(dir, file.name);
    if (file.isDirectory()) {
      await rewrite(filename);
    } else if (filename.endsWith('.html')) {
      const html = await readFile(filename, 'utf8');
      // A raw-file proxy needs explicit filenames; it cannot resolve /lab/.
      const rewritten = html.replace(/(href|src|content)="([^"]*)"/g, (match, attr, value) => {
        if ((value.startsWith(prefix) || value.startsWith(origin + prefix)) && value.endsWith('/')) {
          return `${attr}="${value}index.html"`;
        }
        return match;
      }).replace('</head>', '  <meta name="robots" content="noindex, nofollow">\n</head>');
      await writeFile(filename, rewritten);
    }
  }
}
await rewrite(output);
await writeFile(path.join(output, '.nojekyll'), '');
await writeFile(path.join(output, 'preview.json'), JSON.stringify({
  sourceCommit: process.env.GITHUB_SHA || execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  generatedAt: new Date().toISOString(),
  url: `${origin}${prefix}index.html`
}, null, 2) + '\n');
console.log(`Interactive preview: ${origin}${prefix}index.html`);
