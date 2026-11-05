#!/usr/bin/env python3
"""Generate index.html, presenter.html, wide.html, vert.html (self-contained, inline JS/CSS, no deps)."""
import json, os
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
S = json.load(open(os.path.join(OUT, "src", "slides.json")))
N = len(S)
LABELS = json.dumps([s["label"] for s in S])

CORE = r"""
var N = %(N)d, LABELS = %(LABELS)s;
var KEY = 'gal6-slideshow-state', CH = 'gal6-slideshow', HB = 'gal6-slideshow-hb-';
var me = Math.random().toString(36).slice(2, 10);
var bc = null; try { bc = new BroadcastChannel(CH); } catch (e) { bc = null; }
var state = { slide: 1, black: false, ts: 0, from: '' };
var listeners = [];
function clamp(n) { n = parseInt(n, 10); if (isNaN(n)) n = 1; return Math.max(1, Math.min(N, n)); }
function pad(n) { return (n < 10 ? '0' : '') + n; }
function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
function emit() { for (var i = 0; i < listeners.length; i++) try { listeners[i](state); } catch (e) {} }
function adopt(s) {   // adopt a remote state if it is newer
  if (!s || typeof s.slide !== 'number') return;
  if (s.from === me) return;
  if (s.ts < state.ts) return;
  if (s.ts === state.ts && s.from === state.from) return;
  state = { slide: clamp(s.slide), black: !!s.black, ts: s.ts, from: s.from };
  emit();
}
function publish() {
  state.ts = Date.now(); state.from = me;
  lsSet(KEY, JSON.stringify(state));
  if (bc) try { bc.postMessage({ t: 'state', s: state }); } catch (e) {}
  emit();
}
function go(n) { n = clamp(n); if (n === state.slide && !state.black) return; state.slide = n; state.black = false; publish(); }
function next() { if (state.black) { state.black = false; publish(); return; } go(state.slide + 1); }
function prev() { if (state.black) { state.black = false; publish(); return; } go(state.slide - 1); }
function toggleBlack() { state.black = !state.black; publish(); }
function onKey(e, extra) {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  var k = e.key, t = e.target && e.target.tagName;
  if (t === 'INPUT' || t === 'TEXTAREA') return;
  var h = true;
  if (k === 'ArrowRight' || k === 'ArrowDown' || k === ' ' || k === 'PageDown' || k === 'Enter' || k === 'n' || k === 'N') next();
  else if (k === 'ArrowLeft' || k === 'ArrowUp' || k === 'PageUp' || k === 'Backspace' || k === 'p' || k === 'P') prev();
  else if (k === 'Home') go(1);
  else if (k === 'End') go(N);
  else if (k === 'b' || k === 'B' || k === '.') toggleBlack();
  else if (k === 'f' || k === 'F') { var d = document.documentElement; if (document.fullscreenElement) document.exitFullscreen(); else if (d.requestFullscreen) d.requestFullscreen(); }
  else h = false;
  if (h) e.preventDefault();
}
// init: stored state -> ?slide=N override
(function () {
  var raw = lsGet(KEY);
  if (raw) { try { var s = JSON.parse(raw); if (s && typeof s.slide === 'number') state = { slide: clamp(s.slide), black: !!s.black, ts: s.ts || 0, from: s.from || '' }; } catch (e) {} }
  var m = /[?&]slide=(\d+)/.exec(location.search);
  if (m) { state.slide = clamp(m[1]); state.black = /[?&]black=1/.test(location.search); state.ts = Date.now(); state.from = me; lsSet(KEY, JSON.stringify(state)); setTimeout(function () { if (bc) try { bc.postMessage({ t: 'state', s: state }); } catch (e) {} }, 0); }
})();
if (bc) bc.onmessage = function (ev) {
  var d = ev.data || {};
  if (d.t === 'state') adopt(d.s);
  else if (d.t === 'hello' && state.ts) { try { bc.postMessage({ t: 'state', s: state }); } catch (e) {} }
  else if (d.t === 'hb') seen[d.role + ':' + d.id] = Date.now();
};
window.addEventListener('storage', function (ev) {
  if (ev.key === KEY && ev.newValue) { try { adopt(JSON.parse(ev.newValue)); } catch (e) {} }
});
// polling safety net: some browsers do not fire 'storage' events between file:// pages
setInterval(function () { var raw = lsGet(KEY); if (raw) { try { adopt(JSON.parse(raw)); } catch (e) {} } }, 250);
var seen = {};
function heartbeat(role) {
  function beat() {
    var now = Date.now();
    lsSet(HB + me, JSON.stringify({ role: role, ts: now }));
    if (bc) try { bc.postMessage({ t: 'hb', role: role, id: me }); } catch (e) {}
  }
  beat(); setInterval(beat, 2000);
  window.addEventListener('pagehide', function () { try { localStorage.removeItem(HB + me); } catch (e) {} });
}
function liveRoles() {   // roles seen in the last 6 s (BroadcastChannel and localStorage heartbeats)
  var now = Date.now(), r = {};
  for (var k in seen) { if (now - seen[k] < 6000) r[k.split(':')[0]] = (r[k.split(':')[0]] || 0) + 1; }
  try { for (var i = 0; i < localStorage.length; i++) { var kk = localStorage.key(i); if (kk && kk.indexOf(HB) === 0) { var v = JSON.parse(localStorage.getItem(kk)); if (now - v.ts < 6000) r[v.role] = Math.max(r[v.role] || 0, 1); else localStorage.removeItem(kk); } } } catch (e) {}
  return r;
}
if (bc) try { bc.postMessage({ t: 'hello' }); } catch (e) {}
""" % dict(N=N, LABELS=LABELS)

def page(title, head_css, body, js, bodyattr=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{head_css}</style></head>
<body{bodyattr}>
{body}
<script>
{CORE}
{js}
</script>
</body></html>
"""

VIEW_CSS = "html,body{margin:0;height:100%;background:#000;overflow:hidden;cursor:none}img{position:fixed;inset:0;width:100%;height:100%;object-fit:contain;display:block}#blk{position:fixed;inset:0;background:#000;display:none}"
def view(fmt, role):
    body = '<img id="s" alt=""><div id="blk"></div>'
    js = f"""
var FMT = '{fmt}', DIR = FMT + (/[?&]key=1/.test(location.search) ? '_key' : ''), img = document.getElementById('s'), blk = document.getElementById('blk');
var cache = {{}};
function src(n) {{ return DIR + '/' + pad(n) + '.png'; }}
function preload(n) {{ if (n < 1 || n > N || cache[n]) return; var i = new Image(); i.src = src(n); cache[n] = i; }}
function render() {{
  var n = state.slide; blk.style.display = state.black ? 'block' : 'none';
  var want = src(n); var c = cache[n] || (preload(n), cache[n]);
  if (c.complete) img.src = want; else {{ c.onload = function () {{ if (state.slide === n) img.src = want; }}; img.src = want; }}
  preload(n + 1); preload(n - 1);
  document.title = '{role}' + (DIR !== FMT ? ' KEY ' : ' ') + n + ' / ' + N;
}}
listeners.push(render); render();
document.addEventListener('keydown', onKey);
heartbeat('{fmt}');
setTimeout(function () {{ for (var i = 1; i <= N; i++) preload(i); }}, 800);
"""
    return page(f"Galatians 6 {role}", VIEW_CSS, body, js)

PRES_CSS = """
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#F1ECDA;color:#1F3326;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
#app{display:grid;grid-template-rows:auto 1fr auto;height:100%;gap:10px;padding:12px}
.top{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.num{font-size:34px;font-weight:700;color:#4E6B22}.lab{font-size:20px;color:#31483A;flex:1;min-width:140px}
.timer{font-variant-numeric:tabular-nums;font-size:34px;font-weight:700}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:#555;margin:0 4px 0 12px}.dot.on{background:#3ddc84}
.small{font-size:14px;color:#566650}
.main{display:grid;grid-template-columns:2fr 1fr;gap:12px;min-height:0}
.panel{background:#E3EAD0;border-radius:12px;padding:10px;display:flex;flex-direction:column;min-height:0}
.panel h3{margin:0 0 8px;font-size:13px;letter-spacing:.15em;color:#4E6B22}
.row{display:flex;gap:10px;flex:1;min-height:0;align-items:center;justify-content:center}
.row img{border:1px solid #B9C79A;border-radius:6px;background:#000;max-width:100%;max-height:100%;min-height:0}
.cur .w{flex:1 1 62%;min-width:0;cursor:pointer}.cur .v{flex:0 1 auto;max-height:100%}
.nxt .row{flex-direction:column}.nxt img{max-height:48%}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
button{background:#4E6B22;color:#F6F1E3;border:0;border-radius:8px;padding:10px 16px;font-size:16px;font-weight:700;cursor:pointer}
button.alt{background:#C9D5B0;color:#1F3326}button:active{transform:translateY(1px)}
input[type=number]{width:70px;padding:9px;border-radius:8px;border:1px solid #394a95;background:#F1ECDA;color:#1F3326;font-size:16px}
#black{display:none;background:#b3261e;color:#fff;border-radius:8px;padding:4px 10px;font-weight:700}
"""
def presenter():
    body = """<div id="app">
<div class="top"><span class="num" id="num">1 / %d</span><span class="lab" id="lab"></span><span id="black">BLACK</span>
<span class="small">Sync:<span class="dot" id="dw"></span>wide<span class="dot" id="dv"></span>vert</span><span class="timer" id="tm">00:00</span></div>
<div class="main">
 <div class="panel cur"><h3>CURRENT (click = next, right-click = back)</h3><div class="row"><img class="w" id="cw" alt=""><img class="v" id="cv" alt=""></div></div>
 <div class="panel nxt"><h3>NEXT</h3><div class="row"><img id="nw" alt=""><img id="nv" alt=""></div></div>
</div>
<div class="bar"><button class="alt" id="bp">&larr; Back</button><button id="bn">Next &rarr;</button><button class="alt" id="bb">Black (B)</button>
<label class="small">Go to <input type="number" id="gt" min="1" max="%d"></label><button class="alt" id="bg">Go</button>
<span style="flex:1"></span><button class="alt" id="ts">Start timer</button><button class="alt" id="tr">Reset</button>
<button class="alt" id="ow">Open wide window</button><button class="alt" id="ov">Open vert window</button><button class="alt" id="owk">Wide (green key)</button><button class="alt" id="ovk">Vert (green key)</button>
<span class="small">Keys: &rarr; / Space / PgDn / click = next &middot; &larr; / PgUp = back &middot; B or . = black &middot; Home/End &middot; F = fullscreen</span></div>
</div>""" % (N, N)
    js = r"""
function $(i) { return document.getElementById(i); }
function render() {
  var n = state.slide, nx = Math.min(N, n + 1);
  $('num').textContent = n + ' / ' + N; $('lab').textContent = LABELS[n - 1] || '';
  $('black').style.display = state.black ? 'inline-block' : 'none';
  $('cw').src = 'wide/' + pad(n) + '.png'; $('cv').src = 'vert/' + pad(n) + '.png';
  $('nw').src = 'wide/' + pad(nx) + '.png'; $('nv').src = 'vert/' + pad(nx) + '.png';
  $('nw').style.visibility = $('nv').style.visibility = (n >= N) ? 'hidden' : 'visible';
  document.title = 'Presenter ' + n + ' / ' + N;
}
listeners.push(render); render();
// timer: starts on the first advance; start/pause + reset buttons
var tStart = 0, tAcc = 0, tRun = false;
function tick() { var ms = tAcc + (tRun ? Date.now() - tStart : 0), s = Math.floor(ms / 1000), h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), ss = s % 60;
  $('tm').textContent = (h ? h + ':' + pad(m) : pad(m)) + ':' + pad(ss); $('ts').textContent = tRun ? 'Pause timer' : 'Start timer'; }
function tToggle() { if (tRun) { tAcc += Date.now() - tStart; tRun = false; } else { tStart = Date.now(); tRun = true; } tick(); }
setInterval(tick, 500); tick();
function adv(f) { if (!tRun && tAcc === 0) tToggle(); f(); }
document.addEventListener('keydown', function (e) {
  var k = e.key; if (!e.ctrlKey && !e.metaKey && !e.altKey && (k === 'ArrowRight' || k === 'ArrowDown' || k === ' ' || k === 'PageDown' || k === 'Enter' || k === 'n' || k === 'N') && !tRun && tAcc === 0 && !(e.target && e.target.tagName === 'INPUT')) tToggle();
  onKey(e);
});
$('cw').addEventListener('click', function () { adv(next); });
$('cw').addEventListener('contextmenu', function (e) { e.preventDefault(); prev(); });
$('nw').addEventListener('click', function () { adv(next); }); $('nv').addEventListener('click', function () { adv(next); });
$('bn').onclick = function () { adv(next); }; $('bp').onclick = prev; $('bb').onclick = toggleBlack;
$('bg').onclick = function () { var v = $('gt').value; if (v) go(v); };
$('gt').addEventListener('keydown', function (e) { if (e.key === 'Enter') { var v = $('gt').value; if (v) go(v); e.stopPropagation(); } });
$('ts').onclick = tToggle; $('tr').onclick = function () { tAcc = 0; tRun = false; tick(); };
function openW(url, name, w, h) { window.open(url, name, 'popup,width=' + w + ',height=' + h); }
$('ow').onclick = function () { openW('wide.html', 'gal6_wide', 1280, 720); };
$('ov').onclick = function () { openW('vert.html', 'gal6_vert', 540, 960); };
$('owk').onclick = function () { openW('wide.html?key=1', 'gal6_wide_key', 1280, 720); };
$('ovk').onclick = function () { openW('vert.html?key=1', 'gal6_vert_key', 540, 960); };
heartbeat('presenter');
setInterval(function () { var r = liveRoles(); $('dw').className = 'dot' + (r.wide ? ' on' : ''); $('dv').className = 'dot' + (r.vert ? ' on' : ''); }, 1000);
"""
    return page("Galatians 6 Presenter", PRES_CSS, body, js)

IDX_CSS = """
*{box-sizing:border-box}body{margin:0;background:#F6F1E3;color:#1F3326;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.5}
.wrap{max-width:1100px;margin:0 auto;padding:28px 20px 60px}h1{font-family:Georgia,serif;font-style:italic;font-size:44px;margin:0 0 4px}
.gold{color:#4E6B22}.sub{color:#566650;margin:0 0 22px}
.btns{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0}
a.b,button{background:#4E6B22;color:#F6F1E3;border:0;border-radius:10px;padding:14px 22px;font-size:18px;font-weight:700;cursor:pointer;text-decoration:none}
a.alt,button.alt{background:#C9D5B0;color:#1F3326}
.card{background:#E3EAD0;border-radius:14px;padding:16px 20px;margin:16px 0}.card h2{margin:0 0 6px;font-size:15px;letter-spacing:.14em;color:#4E6B22}
code{background:#F6F1E3;padding:2px 6px;border-radius:5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.t{background:#F6F1E3;border-radius:8px;padding:6px;cursor:pointer;border:2px solid transparent;font-size:12px;color:#566650}.t.cur{border-color:#4E6B22}
.t img{width:100%;display:block;border-radius:4px}
"""
def index():
    body = """<div class="wrap">
<h1>Galatians 6 <span class="gold">live slides</span></h1>
<p class="sub">%d slides, wide 1920&times;1080 and vertical 1080&times;1920, always on the same slide number. KJV text.</p>
<div class="btns"><button id="op">Open presenter</button><button class="alt" id="ow">Open wide window</button><button class="alt" id="ov">Open vertical window</button><button class="alt" id="owk">Wide, green key (OBS)</button><button class="alt" id="ovk">Vertical, green key (OBS)</button></div>
<div class="card"><h2>HOW IT WORKS</h2>
<p>Open the presenter and the two view windows <b>in the same browser</b> (same profile). Advance in the presenter (arrow keys, Space, a clicker, or click the slide). The wide and vertical windows follow instantly.</p>
<p>Share the wide window to StreamYard as a screen share in landscape, and the vertical window as a second screen share in portrait. In OBS, add <code>wide.html</code> as a 1920&times;1080 browser source and <code>vert.html</code> as a 1080&times;1920 browser source. See README.md.</p>
<p>Start on a given slide: <code>presenter.html?slide=7</code>. Black screen: press <b>B</b>. Green-screen camera slot for OBS keying: <code>wide.html?key=1</code>, <code>vert.html?key=1</code>.</p></div>
<div class="card"><h2>JUMP TO A SLIDE</h2><div class="grid" id="g"></div></div>
</div>""" % N
    js = r"""
var g = document.getElementById('g');
for (var i = 1; i <= N; i++) { (function (n) { var d = document.createElement('div'); d.className = 't'; d.id = 't' + n;
  d.innerHTML = '<img loading="lazy" src="wide/' + pad(n) + '.png" alt=""><div>' + n + '. ' + LABELS[n - 1] + '</div>'; d.onclick = function () { go(n); }; g.appendChild(d); })(i); }
function render() { var els = g.children; for (var i = 0; i < els.length; i++) els[i].className = 't' + (i + 1 === state.slide ? ' cur' : ''); }
listeners.push(render); render();
function openW(url, name, w, h) { window.open(url, name, 'popup,width=' + w + ',height=' + h); }
document.getElementById('op').onclick = function () { openW('presenter.html', 'gal6_presenter', 1280, 800); };
document.getElementById('ow').onclick = function () { openW('wide.html', 'gal6_wide', 1280, 720); };
document.getElementById('ov').onclick = function () { openW('vert.html', 'gal6_vert', 540, 960); };
document.getElementById('owk').onclick = function () { openW('wide.html?key=1', 'gal6_wide_key', 1280, 720); };
document.getElementById('ovk').onclick = function () { openW('vert.html?key=1', 'gal6_vert_key', 540, 960); };
document.addEventListener('keydown', onKey);
"""
    return page("Galatians 6 live slides", IDX_CSS, body, js)

for name, html in [("index.html", index()), ("presenter.html", presenter()), ("wide.html", view("wide", "Wide")), ("vert.html", view("vert", "Vertical"))]:
    open(os.path.join(OUT, name), "w").write(html)
print("ok", N)
