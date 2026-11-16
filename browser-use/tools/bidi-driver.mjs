// Drive the user's own Zen / Firefox (logged in) over WebDriver BiDi.
// One long-lived session; send commands over HTTP. Run setup.sh first, then:
//   node ~/.cache/browser-use/bidi-driver.mjs        (run in background)
//   curl -s localhost:9333 -d '{"cmd":"pages"}'
// Commands (part = any substring of the tab's URL; last match wins):
//   pages                                   list tab URLs
//   open   {url, name?, full?}              new tab, load, screenshot, print text
//   goto   {part, url, name?, full?}        navigate a tab
//   shot   {part, name, full?}              screenshot + text
//   scroll {part, text, offset?}            scroll so the element with exactly this text is at the top
//   click  {part, text, wait?}              JS click: interactive elements first, then any element
//   rclick {part, sel, text?, wait?}        real mouse click on the first visible sel (whose text includes text)
//   clickxy {part, x, y, wait?}             real mouse click at CSS-pixel coordinates
//   mouse  {part, x, y}                     move the pointer (hover, or clear tooltips)
//   upload {part, file, index?, wait?}      set a local file on the Nth input[type=file]
//   eval   {part, js | file}                evaluate an expression (or a .js file holding one), return JSON
// Env: BIDI_WS (ws://127.0.0.1:9222/session), PORT (9333), SHOTS (<this dir>/shots)
import puppeteer from 'puppeteer-core';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const SHOTS = process.env.SHOTS || path.join(HERE, 'shots');
const PORT = +(process.env.PORT || 9333);
fs.mkdirSync(SHOTS, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));

const browser = await puppeteer.connect({
  browserWSEndpoint: process.env.BIDI_WS || 'ws://127.0.0.1:9222/session',
  protocol: 'webDriverBiDi',
  defaultViewport: null,
});
// Firefox allows ONE BiDi session. Always end it, or the browser must be restarted.
const quit = async () => { try { await browser.disconnect(); } catch {} process.exit(0); };
process.on('SIGTERM', quit);
process.on('SIGINT', quit);
process.on('uncaughtException', e => { console.error(e); quit(); });

async function find(part) {
  const pages = await browser.pages();
  const p = pages.filter(p => p.url().includes(part)).pop();
  if (!p) throw new Error('no tab with ' + part + '\n' + pages.map(p => p.url()).join('\n'));
  return p;
}
async function report(page, name, full) {
  await page.bringToFront();
  await sleep(500);
  let out = '';
  if (name) {
    const f = path.join(SHOTS, name + '.png');
    await page.screenshot({ path: f, fullPage: !!full });
    out += 'SHOT ' + f + '\n';
  }
  out += 'URL ' + page.url() + '\n';
  const t = await page.evaluate(() => document.body?.innerText || '');
  return out + t.replace(/\n{2,}/g, '\n').slice(0, 6000);
}
async function load(page, url) {
  await page.goto(url, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await sleep(8000); // dashboards keep loading after "load"
}

const cmds = {
  pages: async () => (await browser.pages()).map(p => p.url()).join('\n'),
  open: async ({ url, name, full }) => { const p = await browser.newPage(); await load(p, url); return report(p, name, full); },
  goto: async ({ part, url, name, full }) => { const p = await find(part); await load(p, url); return report(p, name, full); },
  shot: async ({ part, name, full }) => report(await find(part), name, full),
  mouse: async ({ part, x, y }) => { const p = await find(part); await p.mouse.move(x, y); await sleep(800); return 'moved'; },
  eval: async ({ part, js, file }) => JSON.stringify(await (await find(part)).evaluate(file ? fs.readFileSync(file, 'utf8') : js), null, 1),
  // Real mouse events: Angular Material dropdowns and radios ignore a JS el.click().
  rclick: async ({ part, sel, text, wait }) => {
    const p = await find(part);
    const pick = (s, t) => [...document.querySelectorAll(s)].find(e => e.offsetParent !== null && (!t || e.innerText.replace(/\s+/g, ' ').includes(t)));
    const ok = await p.evaluate((s, t, f) => {
      const el = eval(f)(s, t);
      if (!el) return false;
      const r = el.getBoundingClientRect();
      if (r.top < 0 || r.bottom > innerHeight) el.scrollIntoView({ block: 'center' });
      return true;
    }, sel, text, pick.toString());
    if (!ok) return 'not found';
    await sleep(500); // measure after scrolling: sticky bars move while the page scrolls
    const box = await p.evaluate((s, t, f) => {
      const el = eval(f)(s, t), r = el.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, tag: el.tagName };
    }, sel, text, pick.toString());
    await p.mouse.click(box.x, box.y);
    await sleep(wait || 3000);
    return 'rclicked ' + box.tag + ' at ' + Math.round(box.x) + ',' + Math.round(box.y);
  },
  clickxy: async ({ part, x, y, wait }) => { const p = await find(part); await p.mouse.click(x, y); await sleep(wait || 3000); return 'clicked at ' + x + ',' + y; },
  upload: async ({ part, file, index, wait }) => {
    const inputs = await (await find(part)).$$('input[type=file]');
    if (!inputs.length) return 'no file input (the page may open an asset picker instead)';
    await inputs[index || 0].uploadFile(file);
    await sleep(wait || 6000);
    return 'uploaded to input ' + (index || 0) + ' of ' + inputs.length;
  },
  scroll: async ({ part, text, offset }) => (await find(part)).evaluate((txt, off) => {
    const el = [...document.querySelectorAll('*')].find(e => e.offsetParent !== null && e.children.length === 0 && e.textContent.trim() === txt);
    if (!el) return 'not found';
    el.scrollIntoView({ block: 'start' });
    window.scrollBy(0, -(off ?? 120)); // room for sticky headers
    return 'scrolled';
  }, text, offset),
  click: async ({ part, text, wait }) => {
    const p = await find(part);
    const r = await p.evaluate(txt => {
      const vis = e => e.offsetParent !== null && e.innerText && e.innerText.replace(/\s*arrow_drop_down|\s*arrow_right/g, '').trim() === txt;
      const ui = 'button,a,[role=button],[role=tab],[role=option],[role=menuitem],[role=menuitemradio],[aria-haspopup],material-select-item';
      const el = [...document.querySelectorAll(ui)].find(vis) || [...document.querySelectorAll('*')].filter(vis).pop();
      if (!el) return false;
      el.scrollIntoView({ block: 'center' });
      el.click();
      return el.tagName + ' ' + (el.getAttribute('role') || '');
    }, text);
    await sleep(wait || 4000);
    return 'clicked: ' + r;
  },
};

http.createServer((req, res) => {
  let body = '';
  req.on('data', d => body += d);
  req.on('end', async () => {
    try {
      const a = JSON.parse(body || '{}');
      if (!cmds[a.cmd]) throw new Error('unknown cmd ' + a.cmd);
      res.end(String(await cmds[a.cmd](a)) + '\n');
    } catch (e) { res.end('ERR ' + e.message + '\n'); }
  });
}).listen(PORT, '127.0.0.1', () => console.log('ready'));
