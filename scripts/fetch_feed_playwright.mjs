// scripts/fetch_feed_playwright.mjs
import { chromium } from 'playwright';
import fs from 'fs/promises';

const url = process.env.SRC;
if (!url) {
  console.error('SRC is empty');
  process.exit(1);
}

await fs.mkdir('public', { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (compatible; FeedFetcher/1.0)',
  javaScriptEnabled: true,
});
const page = await context.newPage();

try {
  const res = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForLoadState('networkidle', { timeout: 60000 });

  let text = '';
  try {
    text = await res.text();
  } catch (e) {
    // ignore
  }

  if (!text || text.trim().length === 0 || text.trim().startsWith('<html')) {
    // 用已设置的cookie在页面内拉取原始文本
    text = await page.evaluate(async (u) => {
      const r = await fetch(u, { credentials: 'include' });
      return await r.text();
    }, url);
  }

  await fs.writeFile('public/asgaros.xml', text, 'utf8');
  console.log(`Saved public/asgaros.xml (${text.length} bytes)`);
} catch (e) {
  console.error('Playwright fetch failed:', e);
  process.exit(1);
} finally {
  await browser.close();
}
