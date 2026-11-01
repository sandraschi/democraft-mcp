// Headless README/preview screenshots of the running webapp (:11245).
// Usage: bun scripts/shots.mjs [outDir]
import { chromium } from "@playwright/test";

const out = process.argv[2] ?? "../docs/screenshots";
const base = process.env.DEMOCRAFT_WEB ?? "http://127.0.0.1:11245";
const pages = [
	["dashboard", "/"],
	["craft-solid", "/craft/solid?demo=enclosure-fit"],
	["craft-vector", "/craft/vector?demo=cleanup-pass"],
	["depot", "/depot"],
];

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
for (const [name, path] of pages) {
	// "networkidle" never settles against the Vite dev server; wait for load + images.
	await page.goto(`${base}${path}`, { waitUntil: "load", timeout: 30_000 });
	await page.waitForTimeout(2500);
	await page.screenshot({ path: `${out}/${name}.png`, fullPage: false });
	console.log(`${name}: ${out}/${name}.png`);
}
await browser.close();
