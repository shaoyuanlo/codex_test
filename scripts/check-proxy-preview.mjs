import { readFile, writeFile } from 'node:fs/promises';
import { setTimeout as pause } from 'node:timers/promises';

// Runs in GitHub Actions, where the public proxy can be checked independently
// of cloud-workspace egress restrictions. The result is saved with the preview.
const manifest = JSON.parse(await readFile('_preview/preview.json', 'utf8'));
const checks = [];
// Pace requests and respect temporary rate limits instead of failing immediately.
async function fetchPreview(url, options = {}) {
  for (let attempt = 0; attempt < 4; attempt++) {
    await pause(1500);
    const response = await fetch(url, { ...options, signal: AbortSignal.timeout(20000) });
    if ((response.status !== 429 && response.status < 500) || attempt === 3) return response;
    const header = response.headers.get('retry-after');
    const retryAfter = header === null ? 0 : /^\d+$/.test(header)
      ? Number(header) * 1000 : Math.max(0, Date.parse(header) - Date.now()) || 0;
    await response.arrayBuffer();
    const delay = Math.max(10000 * 2 ** attempt, retryAfter);
    console.log(`Proxy returned ${response.status}; retrying in ${Math.ceil(delay / 1000)}s: ${url}`);
    await pause(delay);
  }
}

// Invalidate fixed HTML through the official proxy endpoint after publishing.
const purges = [];
async function purgeFixedPage(url) {
  try {
    const endpoint = new URL('/purge', manifest.stableUrl);
    endpoint.searchParams.set('url', url);
    const response = await fetchPreview(endpoint, { method: 'DELETE' });
    await response.arrayBuffer();
    purges.push({ url, status: response.status, passed: response.ok });
  } catch (error) {
    purges.push({ url, passed: false, error: error.message });
  }
}
for (const relative of ['index.html', 'lab/index.html', 'publications/index.html', 'activities/index.html', 'teaching/index.html', 'blog/index.html']) {
  await purgeFixedPage(new URL(relative, manifest.stableUrl).href);
}
// The origin may briefly serve old content while its background cache refreshes.
try {
  let response, text, currentVersion;
  for (let attempt = 0; attempt < 4; attempt++) {
    response = await fetchPreview(manifest.stableUrl);
    text = await response.text();
    currentVersion = text.includes(`name="preview-source" content="${manifest.sourceCommit}"`);
    if (!response.ok || currentVersion || attempt === 3) break;
    console.log('Fixed preview is cached; checking again in 20s.');
    await pause(20000);
    await purgeFixedPage(manifest.stableUrl);
  }
  checks.push({
    url: manifest.stableUrl,
    status: response.status,
    passed: response.ok && text.includes('<h1 id="home-title">'),
    currentVersion
  });
} catch (error) {
  checks.push({ url: manifest.stableUrl, passed: false, error: error.message });
}
for (const [relative, marker] of [
  ['index.html', '<h1 id="home-title">'],
  ['lab/index.html', '<h1'],
  ['publications/index.html', '<h1'],
  ['activities/index.html', '<h1'],
  ['teaching/index.html', '<h1'],
  ['blog/index.html', '<h1'],
  ['assets/fonts/inter/files/inter-latin-wght-normal.woff2', null],
  ['assets/fonts/noto-sans-tc/files/noto-sans-tc-0-wght-normal.woff2', null]
]) {
  const target = new URL(relative, manifest.url);
  // Font files are shared across revisions, matching the inline font declarations.
  const url = relative.startsWith('assets/fonts/')
    ? new URL(relative, manifest.stableUrl).href : target.href;
  try {
    const response = await fetchPreview(url);
    let matches;
    if (marker === null) {
      matches = Buffer.from(await response.arrayBuffer()).subarray(0, 4).toString('ascii') === 'wOF2';
    } else {
      const text = await response.text();
      matches = text.includes(marker);
      if (relative.endsWith('.html')) {
        // Page titles are editable content; compare with this build instead of hardcoding labels.
        const expectedHeading = (await readFile(`_preview/${relative}`, 'utf8'))
          .match(/<h1\b[^>]*>[\s\S]*?<\/h1>/)?.[0];
        matches &&= Boolean(expectedHeading && text.includes(expectedHeading));
        matches &&= text.includes(`name="preview-source" content="${manifest.sourceCommit}"`)
          && text.includes(`/revisions/${manifest.sourceCommit.slice(0, 12)}/publications/index.html`)
          && !text.includes('/publication/')
          && text.includes('<style data-preview-style="site">')
          && text.includes('.site-header {')
          && text.includes('<style data-preview-style="fonts">')
          && text.includes("font-family: 'Noto Sans TC';");
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
  const response = await fetchPreview(removed);
  checks.push({ url: removed.href, status: response.status, passed: response.status === 404 });
} catch (error) {
  checks.push({ url: removed.href, passed: false, error: error.message });
}
const result = {
  sourceCommit: manifest.sourceCommit,
  checkedAt: new Date().toISOString(),
  passed: checks.every(check => check.passed) && checks[0]?.currentVersion === true,
  purges,
  checks
};
await writeFile('_preview/preview-health.json', JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result, null, 2));
if (!result.passed) process.exitCode = 1;
