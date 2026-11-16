#!/usr/bin/env node
// Walks a prototype in headless Chrome and saves screenshots of the phone, for checking states and
// transitions and for comparing the prototype with the real phone side by side. Fails on any
// script error in the page.
//
//   node shoot.mjs <prototype.html> <out dir> 'step' 'step' …
//
// Steps (coordinates are relative to the #phone element):
//   click:<css selector>   tap:x,y   drag:x0,y0,x1,y1   type:<text>   key:Escape
//   wait:<ms>   shot:<name>   eval:<js>   set:<radio name>=<value>   (e.g. set:platform=android)
// Example:
//   node shoot.mjs prototype.html shots set:platform=ios 'click:.tile[data-i="1"]' wait:120 shot:grow-mid wait:600 shot:detail
//
// Needs Google Chrome (CHROME=path to override) and Node 22+.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const [file, out, ...steps] = process.argv.slice(2);
if (!file || !out) { console.error("usage: shoot.mjs <prototype.html> <out dir> 'step' …"); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9229 + Math.floor(Math.random() * 500);
const profile = fs.mkdtempSync(path.join(out, ".chrome-"));
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--no-first-run", "--hide-scrollbars", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const quit = (code) => { try { ws?.close(); } catch {} chrome.kill(); setTimeout(() => { fs.rmSync(profile, { recursive: true, force: true }); process.exit(code); }, 300); };

let targets = [];
for (let i = 0; i < 50 && !targets.length; i++) { try { targets = (await (await fetch(`http://127.0.0.1:${PORT}/json`)).json()).filter((t) => t.type === "page"); } catch {} await sleep(200); }
if (!targets.length) { console.error("shoot: Chrome did not start"); quit(1); }
const ws = new WebSocket(targets[0].webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pending = new Map(); const errors = [];
ws.addEventListener("message", (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { pending.get(d.id)(d.result); pending.delete(d.id); }
  if (d.method === "Runtime.exceptionThrown") errors.push(d.params.exceptionDetails.exception?.description ?? d.params.exceptionDetails.text);
  if (d.method === "Runtime.consoleAPICalled" && d.params.type === "error") errors.push(d.params.args.map((a) => a.value ?? a.description).join(" "));
});
const cdp = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const js = async (expr) => (await cdp("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true }))?.result?.value;
const box = async (sel) => js(`(() => { const n = document.querySelector(${JSON.stringify(sel)}); if (!n) return null; const r = n.getBoundingClientRect(); return { x: r.left, y: r.top, w: r.width, h: r.height }; })()`);
const mouse = (type, x, y) => cdp("Input.dispatchMouseEvent", { type, x, y, button: "left", buttons: type === "mouseReleased" ? 0 : 1, clickCount: 1 });
const tapAt = async (x, y) => { await mouse("mousePressed", x, y); await sleep(60); await mouse("mouseReleased", x, y); };

await cdp("Runtime.enable"); await cdp("Page.enable");
await cdp("Emulation.setDeviceMetricsOverride", { width: 1000, height: 1000, deviceScaleFactor: 2, mobile: false });
await cdp("Page.navigate", { url: "file://" + path.resolve(file) }); await sleep(800);
await js("try { localStorage.clear() } catch {} location.reload()"); await sleep(800);

for (const step of steps) {
  const i = step.indexOf(":"), k = i < 0 ? step : step.slice(0, i), v = i < 0 ? "" : step.slice(i + 1);
  const phone = await box("#phone");
  const at = (s) => s.split(",").map(Number);
  if (k === "click") { const b = await box(v); if (!b) { console.error(`shoot: no element ${v}`); quit(1); } await tapAt(b.x + b.w / 2, b.y + b.h / 2); }
  else if (k === "tap") { const [x, y] = at(v); await tapAt(phone.x + x, phone.y + y); }
  else if (k === "drag") {
    const [x0, y0, x1, y1] = at(v);
    await mouse("mousePressed", phone.x + x0, phone.y + y0);
    for (let n = 1; n <= 12; n++) { await sleep(16); await mouse("mouseMoved", phone.x + x0 + (x1 - x0) * n / 12, phone.y + y0 + (y1 - y0) * n / 12); }
    await mouse("mouseReleased", phone.x + x1, phone.y + y1);
  }
  else if (k === "type") await cdp("Input.insertText", { text: v });
  else if (k === "key") await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: v, code: v });
  else if (k === "wait") await sleep(Number(v) || 300);
  else if (k === "eval") console.log(`eval ${v} -> ${JSON.stringify(await js(v))}`);
  else if (k === "set") { const [name, value] = v.split("="); const b = await box(`input[name="${name}"][value="${value}"]`); if (b) await tapAt(b.x + b.w / 2, b.y + b.h / 2); await sleep(300); }
  else if (k === "shot") {
    const r = await cdp("Page.captureScreenshot", { format: "png", clip: { x: phone.x, y: phone.y, width: phone.w, height: phone.h, scale: 1 } });
    const f = path.join(out, `${v || "shot"}.png`); fs.writeFileSync(f, Buffer.from(r.data, "base64")); console.log(`shot ${f}`);
  }
  else { console.error(`shoot: unknown step ${step}`); quit(2); }
}
if (errors.length) { console.error("page errors:\n  " + errors.join("\n  ")); quit(1); }
console.log("shoot: no page errors");
quit(0);
