import assert from 'node:assert/strict';
import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';

// Check the built result, including every generated blog post and asset link.
const output = path.resolve(process.argv[2] || '_site');
async function walk(dir) {
  const children = await readdir(dir, { withFileTypes: true });
  return (await Promise.all(children.map(item => item.isDirectory()
    ? walk(path.join(dir, item.name)) : path.join(dir, item.name)))).flat();
}
const files = (await walk(output)).filter(file => file.endsWith('.html'));
const home = await readFile(path.join(output, 'index.html'), 'utf8');
const canonical = home.match(/rel="canonical" href="([^"]+)"/)[1];
const base = new URL(canonical);
const prefix = new URL('.', base).pathname;
let links = 0;
for (const file of files) {
  const html = await readFile(file, 'utf8');
  assert.match(html, /<html lang="en">/, `${file}: language`);
  assert.match(html, /name="viewport"/, `${file}: responsive viewport`);
  assert.match(html, /<main id="main"/, `${file}: main landmark`);
  assert.equal((html.match(/<h1\b/g) || []).length, 1, `${file}: one page heading`);
  if (!file.endsWith('404.html')) {
    assert.equal((html.match(/aria-current="page"/g) || []).length, 1, `${file}: active navigation`);
  }
  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = match[1].replaceAll('&amp;', '&');
    if (/^(https?:|mailto:|tel:|data:|#)/.test(href)) continue;
    assert.ok(href.startsWith(prefix), `${file}: URL missing base path: ${href}`);
    const relative = decodeURIComponent(href.slice(prefix.length).split('#')[0].split('?')[0]);
    let target = path.join(output, relative);
    if ((await stat(target)).isDirectory()) target = path.join(target, 'index.html');
    await stat(target);
    links++;
  }
}
for (const page of ['index.html', 'lab/index.html', 'publications/index.html', 'teaching/index.html', 'blog/index.html', '404.html']) {
  await stat(path.join(output, page));
}
console.log(`Validated ${files.length} pages and ${links} local links/assets at ${prefix}`);
