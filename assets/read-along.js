/* Read-along player for y3f study guides.
 *
 * The page keeps its own markup. This script reads the timeline in
 * <script type="application/json" id="read-along-data">, wraps each narrated
 * sentence of the page in <span class="rl"> (by character offsets inside the
 * same elements the build script read), and docks a player to the bottom:
 * the sentence being read is highlighted, the page scrolls along with it, and
 * clicking any sentence plays from there. A light switch at the top of the
 * page turns dark mode on and off.
 */
(function () {
  "use strict";

  var THEME_KEY = "y3f-theme";
  function remember(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { /* private mode: fine */ }
    return null;
  }

  /* ---- light switch (dark mode) ------------------------------------------ */

  var html = document.documentElement;
  if (remember(THEME_KEY) === "dark") html.classList.add("ra-dark");

  var sound = null;
  function click(on) { // a short, quiet mechanical click
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      sound = sound || new Ctx();
      var n = Math.floor(sound.sampleRate * 0.025), buf = sound.createBuffer(1, n, sound.sampleRate), d = buf.getChannelData(0);
      for (var i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 10);
      var src = sound.createBufferSource(), band = sound.createBiquadFilter(), gain = sound.createGain();
      src.buffer = buf;
      band.type = "bandpass";
      band.frequency.value = on ? 2600 : 1900;
      gain.gain.value = 0.25;
      src.connect(band); band.connect(gain); gain.connect(sound.destination);
      src.start();
    } catch (e) { /* no sound is fine */ }
  }

  var lightSwitch = document.createElement("button");
  lightSwitch.type = "button";
  lightSwitch.className = "ra-switch";
  lightSwitch.setAttribute("role", "switch");
  lightSwitch.innerHTML = '<span class="ra-rocker"><span class="ra-lever"></span></span>';
  function syncSwitch() {
    var dark = html.classList.contains("ra-dark");
    lightSwitch.setAttribute("aria-checked", dark ? "false" : "true");
    lightSwitch.setAttribute("aria-label", dark ? "Lights are off (dark mode). Turn them on" : "Lights are on. Turn them off (dark mode)");
    lightSwitch.title = dark ? "Lights on" : "Lights off";
  }
  lightSwitch.addEventListener("click", function () {
    var dark = !html.classList.contains("ra-dark");
    // The theme itself switches instantly (so it can never be left half-done); where the
    // browser supports it, a snapshot crossfade softens the change.
    var flip = function () { html.classList.toggle("ra-dark", dark); syncSwitch(); };
    var calm = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (document.startViewTransition && !calm && document.visibilityState === "visible") {
      var t = document.startViewTransition(flip);
      // The browser may skip the crossfade (tab not rendering); the flip still happens.
      [t.ready, t.finished, t.updateCallbackDone].forEach(function (p) { if (p && p.catch) p.catch(function () {}); });
    } else flip();
    remember(THEME_KEY, dark ? "dark" : "light");
    syncSwitch();
    click(!dark);
  });
  syncSwitch();
  document.body.appendChild(lightSwitch);

  /* ---- the read-along ---------------------------------------------------- */

  var dataEl = document.getElementById("read-along-data");
  if (!dataEl) return;
  var data = JSON.parse(dataEl.textContent);
  var page = document.querySelector(data.root || "main") || document.body;

  // lines: [blockIndex, startOffset, endOffset, t0ms, t1ms, section]
  var lines = data.lines;
  var starts = lines.map(function (l) { return l[3]; });
  var spansOf = lines.map(function () { return []; });
  var reduceMotion = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var storeKey = "read-along:" + (data.id || location.pathname);
  function store(key, value) { return remember(storeKey + key, value); }

  /* 1. wrap each narrated sentence */

  var blocks = page.querySelectorAll(data.selector);
  if (data.leaf) { // an element holding other matches (a note made of paragraphs) isn't a line itself
    blocks = [].filter.call(blocks, function (el) { return !el.querySelector(data.selector); });
  }
  var byBlock = {};
  lines.forEach(function (l, i) { (byBlock[l[0]] = byBlock[l[0]] || []).push(i); });
  var skipped = 0;

  Object.keys(byBlock).forEach(function (key) {
    var b = +key, el = blocks[b];
    if (!el || el.textContent.length !== data.blockLengths[b]) { skipped++; return; }
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    var nodes = [], node;
    while ((node = walker.nextNode())) nodes.push(node);
    var offset = 0;
    nodes.forEach(function (text) {
      var from = offset, to = offset + text.data.length;
      offset = to;
      var hits = byBlock[b].filter(function (i) { return lines[i][1] < to && lines[i][2] > from; });
      if (!hits.length) return;
      // Text inside MathML can't hold HTML spans, and KaTeX's own glyph boxes shouldn't be split:
      // highlight the whole formula instead.
      var math = text.parentNode.closest && text.parentNode.closest("math, .katex");
      if (math) {
        var host = math, up;
        while ((up = host.parentElement && host.parentElement.closest(".katex-display, .katex, .math-inline, .math-display"))) host = up;
        if (host === math && math.localName === "math") host = math.parentElement;
        if (!host.classList.contains("rl")) {
          host.classList.add("rl");
          host.setAttribute("data-l", hits[0]);
          spansOf[hits[0]].push(host);
        }
        return;
      }
      // Nor can SVG text (a drawn label would vanish): highlight the whole drawing.
      var pic = text.parentNode.closest && text.parentNode.closest("svg");
      if (pic) {
        if (!pic.classList.contains("rl")) {
          pic.classList.add("rl");
          pic.setAttribute("data-l", hits[0]);
          spansOf[hits[0]].push(pic);
        }
        return;
      }
      var frag = document.createDocumentFragment(), cursor = from;
      hits.forEach(function (i) {
        var s = Math.max(lines[i][1], from), e = Math.min(lines[i][2], to);
        if (s > cursor) frag.appendChild(document.createTextNode(text.data.slice(cursor - from, s - from)));
        if (!text.data.slice(s - from, e - from).trim()) { // layout whitespace: nothing to highlight
          frag.appendChild(document.createTextNode(text.data.slice(s - from, e - from)));
          cursor = e;
          return;
        }
        var span = document.createElement("span");
        span.className = "rl";
        span.setAttribute("data-l", i);
        span.textContent = text.data.slice(s - from, e - from);
        frag.appendChild(span);
        spansOf[i].push(span);
        cursor = e;
      });
      if (cursor < to) frag.appendChild(document.createTextNode(text.data.slice(cursor - from)));
      text.parentNode.replaceChild(frag, text);
    });
  });
  if (skipped) console.warn("read-along: " + skipped + " block(s) changed since the audio was built; not linked");

  /* 2. the player */

  var icon = {
    play: '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.14v13.72a1 1 0 0 0 1.5.86l11.04-6.86a1 1 0 0 0 0-1.72L9.5 4.28A1 1 0 0 0 8 5.14z"/></svg>',
    pause: '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4.5" width="4" height="15" rx="1.2"/><rect x="14" y="4.5" width="4" height="15" rx="1.2"/></svg>',
    prev: '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="5" y="5" width="2.4" height="14" rx="1"/><path d="M19 6.2v11.6a1 1 0 0 1-1.55.83L9.6 13.03a1.25 1.25 0 0 1 0-2.06l7.85-5.6A1 1 0 0 1 19 6.2z"/></svg>',
    next: '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="16.6" y="5" width="2.4" height="14" rx="1"/><path d="M5 6.2v11.6a1 1 0 0 0 1.55.83l7.85-5.6a1.25 1.25 0 0 0 0-2.06l-7.85-5.6A1 1 0 0 0 5 6.2z"/></svg>'
  };

  var bar = document.createElement("div");
  bar.className = "ra";
  bar.setAttribute("role", "region");
  bar.setAttribute("aria-label", "Read-along audio");
  bar.innerHTML =
    '<div class="ra-in">' +
    '<button class="ra-skip ra-prev" type="button" aria-label="Previous line" title="Previous line (←)">' + icon.prev + "</button>" +
    '<button class="ra-play" type="button" aria-label="Play" title="Play (space)">' + icon.play + "</button>" +
    '<button class="ra-skip ra-next" type="button" aria-label="Next line" title="Next line (→)">' + icon.next + "</button>" +
    '<div class="ra-mid"><div class="ra-meta"><span class="ra-sec"></span><span class="ra-time">0:00</span></div>' +
    '<div class="ra-bar" role="slider" tabindex="0" aria-label="Seek" aria-valuemin="0"><div class="ra-track"></div>' +
    '<div class="ra-fill"></div><div class="ra-knob"></div></div></div>' +
    '<button class="ra-rate" type="button" aria-label="Playback speed" title="Playback speed">1×</button>' +
    "</div>";
  document.body.appendChild(bar);
  document.body.classList.add("ra-ready");

  var audio = new Audio();
  audio.preload = "metadata";
  if ("preservesPitch" in audio) audio.preservesPitch = true;

  var q = function (sel) { return bar.querySelector(sel); };
  var playBtn = q(".ra-play"), secEl = q(".ra-sec"), timeEl = q(".ra-time"), seek = q(".ra-bar"),
    fill = q(".ra-fill"), knob = q(".ra-knob"), rateBtn = q(".ra-rate");
  var total = data.duration;
  seek.setAttribute("aria-valuemax", Math.round(total / 1000));

  var sectionNames = [];
  (data.sections || []).forEach(function (s) {
    var tick = document.createElement("div");
    tick.className = "ra-tick";
    tick.style.left = (s.t / total) * 100 + "%";
    seek.insertBefore(tick, fill);
    sectionNames[s.n] = s.label;
  });

  function clock(ms) {
    var t = Math.max(0, Math.floor(ms / 1000));
    return Math.floor(t / 60) + ":" + ("0" + (t % 60)).slice(-2);
  }

  /* 3. which line is under the playhead, and keeping it in view */

  // A page can hide parts of itself (a filter): lines inside [data-ra-off] are skipped.
  function off(i) { var el = blocks[lines[i][0]]; return !!(el && el.closest("[data-ra-off]")); }
  function shown(i, step) { while (i >= 0 && i < lines.length && off(i)) i += step; return i; }

  function lineAt(ms) { // last line that has started; it stays lit through its pause
    var lo = 0, hi = starts.length - 1, best = -1;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (starts[mid] <= ms + 1) { best = mid; lo = mid + 1; } else hi = mid - 1;
    }
    return best;
  }

  var current = -1, started = false;  // nothing is lit until playback (or a saved position) begins
  var handsOffUntil = 0;   // after you scroll yourself, the page waits a moment before following again
  var autoScrolling = false, autoTimer = 0;

  function keepInView(i) {
    var spans = spansOf[i];
    if (!spans || !spans.length || Date.now() < handsOffUntil) return;
    var top = spans[0].getBoundingClientRect().top;
    var bottom = spans[spans.length - 1].getBoundingClientRect().bottom;
    var view = Math.min(window.innerHeight, bar.getBoundingClientRect().top);
    if (top >= view * 0.18 && bottom <= view * 0.72) return; // already in the reading band
    autoScrolling = true;
    clearTimeout(autoTimer);
    autoTimer = setTimeout(function () { autoScrolling = false; }, 800);
    window.scrollTo({ top: Math.max(0, window.scrollY + top - view * 0.3), behavior: reduceMotion ? "auto" : "smooth" });
  }

  function setLine(i) {
    if (i === current) return;
    if (current >= 0) spansOf[current].forEach(function (s) { s.classList.remove("ra-on"); });
    current = i;
    if (i < 0) return;
    spansOf[i].forEach(function (s) {
      s.classList.add("ra-on");
      var d = s.closest("details");
      if (d && !d.open) d.open = true;
    });
    secEl.textContent = sectionNames[lines[i][5]] || data.title || "";
    if (!audio.paused) keepInView(i);
  }

  /* 4. loading, with automatic recovery from a dropped connection */

  var pending = null;        // a position to apply once the audio can seek
  var lastMs = 0;            // last known playhead, to resume from after a reload
  var wantPlaying = false;   // what the listener asked for
  var failed = false, retries = 0, retryTimer = 0, status = "";

  function now() { return pending !== null ? pending : audio.readyState ? audio.currentTime * 1000 : lastMs; }

  function setStatus(text) { status = text; paint(); }

  function paint() {
    var ms = now();
    var pct = Math.min(100, (ms / total) * 100) + "%";
    fill.style.width = pct;
    knob.style.left = pct;
    timeEl.textContent = status || clock(ms) + " / " + clock(total);
    seek.setAttribute("aria-valuenow", Math.round(ms / 1000));
    seek.setAttribute("aria-valuetext", clock(ms));
    if (!started) return;
    var i = lineAt(ms);
    if (i >= 0 && off(i)) { // the playhead reached a hidden part: go on from the next line still shown
      var j = shown(i, 1);
      if (j < lines.length) { seekTo(lines[j][3]); return; }
      pause();
    }
    setLine(i);
  }

  function load(bust) {
    audio.src = data.audio + (bust ? (data.audio.indexOf("?") < 0 ? "?" : "&") + "retry=" + Date.now() : "");
    audio.load();
  }

  // A network error used to leave the player dead until a reload. Now it retries by
  // itself (backing off), keeps the position, and carries on playing if it was.
  audio.addEventListener("error", function () {
    clearTimeout(retryTimer);
    if (pending === null) pending = lastMs;
    retries++;
    if (retries > 6) {
      failed = true;
      bar.classList.add("ra-error");
      setStatus("Audio unavailable · press play to retry");
      return;
    }
    setStatus("Reconnecting…");
    retryTimer = setTimeout(function () {
      load(retries > 2); // after two plain retries, step past any cached bad response
      if (wantPlaying) play();
    }, Math.min(8000, 500 * Math.pow(2, retries - 1)));
  });
  audio.addEventListener("loadedmetadata", function () {
    if (pending !== null) { audio.currentTime = pending / 1000; pending = null; }
    audio.playbackRate = audio.defaultPlaybackRate;
    failed = false;
    bar.classList.remove("ra-error");
    setStatus("");
  });
  audio.addEventListener("playing", function () { retries = 0; });
  load(false);

  var raf = 0;
  function loop() { paint(); raf = audio.paused ? 0 : requestAnimationFrame(loop); }

  /* 5. controls */

  function seekTo(ms) {
    started = true;
    ms = Math.max(0, Math.min(total - 50, ms));
    lastMs = ms;
    if (audio.readyState < 1) pending = ms;
    else audio.currentTime = ms / 1000;
    paint();
  }

  function play() {
    wantPlaying = true;
    started = true;
    if (failed) { failed = false; retries = 0; bar.classList.remove("ra-error"); setStatus("Loading…"); load(true); }
    var p = audio.play();
    if (p && p.catch) p.catch(function () {});
  }
  function pause() { wantPlaying = false; audio.pause(); }
  function toggle() { if (audio.paused) play(); else pause(); }

  function playLine(i) {
    if (i < 0 || i >= lines.length) return;
    handsOffUntil = 0;
    seekTo(lines[i][3]);
    play();
    keepInView(i);
  }
  function prevLine() { // like a music player: restart this line first, then step back
    var ms = now(), i = lineAt(ms);
    var back = shown(i > 0 && ms - lines[i][3] < 1500 ? i - 1 : Math.max(i, 0), -1);
    playLine(back >= 0 ? back : shown(0, 1));
  }
  function nextLine() { var j = shown(lineAt(now()) + 1, 1); if (j < lines.length) playLine(j); }

  playBtn.addEventListener("click", toggle);
  q(".ra-prev").addEventListener("click", prevLine);
  q(".ra-next").addEventListener("click", nextLine);

  audio.addEventListener("play", function () {
    playBtn.innerHTML = icon.pause;
    playBtn.setAttribute("aria-label", "Pause");
    handsOffUntil = 0;
    if (current >= 0) keepInView(current);
    if (!raf) raf = requestAnimationFrame(loop);
  });
  audio.addEventListener("pause", function () {
    playBtn.innerHTML = icon.play;
    playBtn.setAttribute("aria-label", "Play");
    store(":t", String(Math.round(lastMs)));
    paint();
  });
  audio.addEventListener("seeked", paint);
  var lastSave = 0;
  audio.addEventListener("timeupdate", function () {
    if (audio.readyState && !audio.seeking && pending === null) lastMs = audio.currentTime * 1000;
    if (Date.now() - lastSave > 3000) { lastSave = Date.now(); store(":t", String(Math.round(lastMs))); }
    paint(); // animation frames pause in background tabs; this keeps the highlight current anyway
  });
  audio.addEventListener("ended", function () { wantPlaying = false; store(":t", "0"); });

  // Speed.
  var rates = [1, 1.25, 1.5, 1.75, 2, 0.75];
  function setRate(r) {
    audio.defaultPlaybackRate = r;
    audio.playbackRate = r;
    rateBtn.textContent = r + "×";
    store(":rate", String(r));
  }
  rateBtn.addEventListener("click", function () {
    setRate(rates[(rates.indexOf(audio.playbackRate) + 1) % rates.length] || 1);
  });
  var savedRate = parseFloat(store(":rate"));
  if (rates.indexOf(savedRate) >= 0) setRate(savedRate);

  // Scrub bar: drag or click to seek; arrow keys step 5 s when it has focus.
  function scrubAt(e) {
    var r = seek.getBoundingClientRect();
    return Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)) * total;
  }
  seek.addEventListener("pointerdown", function (e) {
    seek.setPointerCapture(e.pointerId);
    seek.classList.add("ra-drag");
    handsOffUntil = 0;
    seekTo(scrubAt(e));
  });
  seek.addEventListener("pointermove", function (e) { if (seek.classList.contains("ra-drag")) seekTo(scrubAt(e)); });
  seek.addEventListener("pointerup", function () {
    seek.classList.remove("ra-drag");
    if (current >= 0 && !audio.paused) keepInView(current);
  });
  seek.addEventListener("keydown", function (e) {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault();
      e.stopPropagation();
      seekTo(now() + (e.key === "ArrowRight" ? 5000 : -5000));
    }
  });

  // Click a sentence → play from it. Hover shows the whole sentence.
  page.addEventListener("click", function (e) {
    var span = e.target.closest && e.target.closest(".rl");
    if (!span || span.closest("summary")) return;
    if (e.target.closest("a[href]")) return; // a link in a line goes where it points, without playing
    var sel = window.getSelection && window.getSelection();
    if (sel && !sel.isCollapsed && sel.toString().trim()) return; // they were selecting text
    playLine(+span.getAttribute("data-l"));
  });
  var hovered = -1;
  function hover(i) {
    if (i === hovered) return;
    if (hovered >= 0) spansOf[hovered].forEach(function (s) { s.classList.remove("ra-hover"); });
    hovered = i;
    if (i >= 0) spansOf[i].forEach(function (s) { s.classList.add("ra-hover"); });
  }
  page.addEventListener("pointerover", function (e) {
    if (e.pointerType && e.pointerType !== "mouse") return;
    var span = e.target.closest && e.target.closest(".rl");
    hover(span && !span.closest("summary") ? +span.getAttribute("data-l") : -1);
  });
  page.addEventListener("pointerleave", function () { hover(-1); });

  // Scrolling yourself pauses the follow for a few seconds; then it picks up again.
  function userScrolled() { if (!autoScrolling) handsOffUntil = Date.now() + 4000; }
  window.addEventListener("wheel", userScrolled, { passive: true });
  window.addEventListener("touchmove", userScrolled, { passive: true });
  window.addEventListener("keydown", function (e) {
    var tag = (e.target.tagName || "").toLowerCase();
    if (e.metaKey || e.ctrlKey || e.altKey || tag === "input" || tag === "textarea" || e.target.isContentEditable) return;
    if (e.key === " " && (tag === "body" || tag === "html" || tag === "main")) { e.preventDefault(); toggle(); }
    else if (e.key === "ArrowLeft" && tag !== "button") { e.preventDefault(); prevLine(); }
    else if (e.key === "ArrowRight" && tag !== "button") { e.preventDefault(); nextLine(); }
    else if (["PageUp", "PageDown", "ArrowUp", "ArrowDown", "Home", "End"].indexOf(e.key) >= 0) userScrolled();
  });

  // Lock-screen / headphone controls.
  if ("mediaSession" in navigator) {
    try {
      navigator.mediaSession.metadata = new MediaMetadata({ title: data.title || document.title, artist: data.artist || "", album: data.album || "" });
      var session = navigator.mediaSession;
      session.setActionHandler("play", play);
      session.setActionHandler("pause", pause);
      session.setActionHandler("previoustrack", prevLine);
      session.setActionHandler("nexttrack", nextLine);
      session.setActionHandler("seekbackward", function () { seekTo(now() - 10000); });
      session.setActionHandler("seekforward", function () { seekTo(now() + 10000); });
      session.setActionHandler("seekto", function (d) { seekTo(d.seekTime * 1000); });
    } catch (e) { /* older browsers */ }
  }

  // Pick up where you left off.
  var resume = parseInt(store(":t"), 10);
  if (resume > 3000 && resume < total - 3000) seekTo(resume);
  else { paint(); secEl.textContent = data.title || ""; }
})();
