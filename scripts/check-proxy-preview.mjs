import { readFile, writeFile } from 'node:fs/promises';

// Runs in GitHub Actions, where the public proxy can be checked independently
// of cloud-workspace egress restrictions. The result is saved with the preview.
const manifest = JSON.parse(await readFile('_preview/preview.json', 'utf8'));
const checks = [];
for (const [relative, marker] of [
  ['index.html', '<h1 id="home-title">'],
  ['lab/index.html', '<h1>Lab</h1>'],
  ['assets/style.css', '--paper: #f9f8f5']
]) {
  const url = new URL(relative, manifest.url).href;
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(20000) });
    const body = await response.text();
    checks.push({ url, status: response.status, passed: response.ok && body.includes(marker) });
  } catch (error) {
    checks.push({ url, passed: false, error: error.message });
  }
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
