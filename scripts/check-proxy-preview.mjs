import { readFile, writeFile } from 'node:fs/promises';

// Runs in GitHub Actions, where the public proxy can be checked independently
// of cloud-workspace egress restrictions. The result is saved with the preview.
const manifest = JSON.parse(await readFile('_preview/preview.json', 'utf8'));
const checks = [];
for (const [relative, marker] of [
  ['index.html', '<h1 id="home-title">'],
  ['lab/index.html', '<h1>Lab</h1>'],
  ['publications/index.html', '<h1>Publications</h1>'],
  ['assets/style.css', '.site-header {'],
  ['assets/fonts/fonts.css', "font-family: 'Noto Sans TC';"],
  ['assets/fonts/inter/files/inter-latin-wght-normal.woff2', null],
  ['assets/fonts/noto-sans-tc/files/noto-sans-tc-0-wght-normal.woff2', null]
]) {
  const target = new URL(relative, manifest.url);
  const url = target.href;
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(20000) });
    let matches;
    if (marker === null) {
      matches = Buffer.from(await response.arrayBuffer()).subarray(0, 4).toString('ascii') === 'wOF2';
    } else {
      const text = await response.text();
      matches = text.includes(marker);
      if (relative.endsWith('.html')) {
        matches &&= text.includes(`name="preview-source" content="${manifest.sourceCommit}"`)
          && text.includes(`/revisions/${manifest.sourceCommit.slice(0, 12)}/publications/index.html`)
          && !text.includes('/publication/');
      }
    }
    checks.push({ url, status: response.status, passed: response.ok && matches });
  } catch (error) {
    checks.push({ url, passed: false, error: error.message });
  }
}
const removed = new URL(manifest.url.replace(/revisions\/[^/]+\/index\.html$/, 'publication/index.html'));
removed.searchParams.set('v', manifest.sourceCommit.slice(0, 12));
try {
  const response = await fetch(removed, { signal: AbortSignal.timeout(20000) });
  checks.push({ url: removed.href, status: response.status, passed: response.status === 404 });
} catch (error) {
  checks.push({ url: removed.href, passed: false, error: error.message });
}
const result = {
  sourceCommit: manifest.sourceCommit,
  checkedAt: new Date().toISOString(),
  passed: checks.every(check => check.passed),
  checks
};
await writeFile('_preview/preview-health.json', JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
if (!result.passed) process.exitCode = 1;
