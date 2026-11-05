#!/usr/bin/env python3
"""Render Galatians 6 slides with a reserved camera slot.
Sets: ../wide, ../vert (placeholder) and ../wide_key, ../vert_key (flat chroma green #00B140). Also writes slides.json."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content as C

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Natural palette (light): linen bg #F6F1E3, sage-tint cards #E3EAD0, forest text #1F3326,
# olive accent #4E6B22, clay secondary #9A4F2B, muted green-gray #566650, description text #31483A.
NAVY, CARD, GOLD = (246, 241, 227), (227, 234, 208), (78, 107, 34)   # NAVY = background, GOLD = accent role (olive)
WHITE, MUTED = (31, 51, 38), (86, 102, 80)                            # WHITE = main text role (forest)
CLAY, CREAM, EDGE, DESC = (154, 79, 43), (246, 241, 227), (200, 212, 172), (49, 72, 58)
GI = "/usr/share/fonts/truetype/sand-box/google/Gelasio/Gelasio-Italic-VariableFont_wght.ttf"
INTER = "/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf"
_c = {}
def serif(sz):
    k = ("s", sz)
    if k not in _c:
        f = ImageFont.truetype(GI, sz); f.set_variation_by_name("Bold Italic"); _c[k] = f
    return _c[k]
def sans(sz, w="SemiBold"):
    k = ("i", sz, w)
    if k not in _c:
        f = ImageFont.truetype(INTER, sz); f.set_variation_by_name(w); _c[k] = f
    return _c[k]

def q(t): return "\u201c" + t + "\u201d"
def curly(t): return t.replace("'", "\u2019")

def wrap(text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w) if cur else w
        if font.getlength(t) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def spaced(d, xy, text, font, fill, sp):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill); x += font.getlength(ch) + sp
    return x
def spaced_w(text, font, sp): return sum(font.getlength(c) + sp for c in text) - sp

def fit(text, maker, maxw, maxh, hi, lo, lh=1.22, step=2):
    for s in range(hi, lo - 1, -step):
        f = maker(s); ls = wrap(text, f, maxw)
        if len(ls) * s * lh <= maxh: return s, f, ls
    f = maker(lo); return lo, f, wrap(text, f, maxw)

CHROMA = (0, 177, 64)          # #00B140
PLACEHOLDER = (238, 232, 212)  # linen, slightly deeper than the page
ICON = (196, 206, 168)         # faint sage camera icon
# Camera slot (outer rectangle, border included): x0, y0, x1, y1
# Same boxes as the Galatians 5 decks (camera slot: wide x986 y115 878x494; vertical x22 y840 1037x598, the middle band)
SLOT = {"wide": (986, 115, 1864, 609), "vert": (22, 840, 1059, 1438)}
BORDER = 4

# ---- Layout copied from the Galatians 5 deck (pptx, 2 px per pt) -------------------------------------------
# header label, chip, right-aligned counter, gold bar, text zone, card: exact Gal 5 values, except where they
# collided with the Gal 6 camera slot (none now: the slot is where Gal 5 had the camera).
LAYOUT = {
    "wide": dict(hdr=(86, 65), chip=(86, 115, 79), right=(1865, 65),
                 bar=(86, 238, 13), zone=(130, 238, 806, 1008),
                 card=(986, 645, 878, 374),
                 sizes=dict(verse=64, close=68, big=92, part=96, read=48, num=40, q=48, label=26, flow_n=36, flow_t=40, flow_v=28, flow_d=36, sub=32, ref=28, note=24)),
    "vert": dict(hdr=(82, 89), chip=(82, 144, 86), right=(1015, 170),
                 bar=(82, 266, 13), zone=(125, 266, 878, 806),
                 card=(68, 1466, 945, 390),
                 sizes=dict(verse=64, close=68, big=84, part=88, read=48, num=40, q=48, label=26, flow_n=36, flow_t=40, flow_v=28, flow_d=36, sub=32, ref=28, note=24)),
}

def font_for(kind, size):
    size = max(8, int(round(size)))
    if kind == "serif": return serif(size)
    if kind == "sansb": return sans(size, "Bold")
    if kind == "sansm": return sans(size, "Medium")
    return sans(size, "SemiBold")

def flow_layout(paras, scale, width):
    """paras: [dict(runs=[(text, kind, size, color, nosplit)], after=em, lh=ratio)] -> (lines, height)
    lines: list of (y, [(x, text, font, color)]), y relative to the top of the block."""
    lines = []; y = 0.0
    for pi, p in enumerate(paras):
        toks = []
        for (text, kind, size, color, nosplit) in p["runs"]:
            f = font_for(kind, size * scale)
            if nosplit: toks.append((text, f, color, size * scale, True))
            else:
                for w in text.split(): toks.append((w, f, color, size * scale, False))
        cur, x, lh = [], 0.0, 0.0
        def flush():
            nonlocal cur, y, lh
            if cur:
                lines.append((y, cur)); y += lh; cur = []
        for (w, f, color, sz, ns) in toks:
            gap = 0 if not cur else prev_gap
            wl = f.getlength(w)
            if cur and x + gap + wl > width and not ns:
                flush(); x = 0.0; gap = 0
            cur.append((x + gap, w, f, color)); x = x + gap + wl; lh = max(lh, sz * p.get("lh", 1.2))
            prev_gap = f.getlength(" ") if not ns else 0
        flush()
        y += p.get("after", 0) * (toks[0][3] if toks else 0) if pi < len(paras) - 1 else 0
    return lines, y

class Slide:
    def __init__(self, fmt, key=False):
        self.fmt = fmt; self.vert = fmt == "vert"; self.key = key
        self.W, self.H = (1080, 1920) if self.vert else (1920, 1080)
        self.L = LAYOUT[fmt]
        self.im = Image.new("RGB", (self.W, self.H), NAVY); self.d = ImageDraw.Draw(self.im)
        self.camera()
    def camera(self):
        x0, y0, x1, y1 = SLOT[self.fmt]; d = self.d
        d.rounded_rectangle((x0, y0, x1 - 1, y1 - 1), radius=30, fill=CHROMA if self.key else PLACEHOLDER, outline=GOLD, width=BORDER)
        if not self.key:   # faint camera icon
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            w, h = 190, 120
            d.rounded_rectangle((cx - w // 2, cy - h // 2 + 10, cx + w // 2, cy + h // 2 + 10), radius=18, outline=ICON, width=9)
            d.rounded_rectangle((cx - 34, cy - h // 2 - 12, cx + 34, cy - h // 2 + 12), radius=8, outline=ICON, width=9)
            d.ellipse((cx - 36, cy - 26, cx + 36, cy + 46), outline=ICON, width=9)
            d.ellipse((cx + w // 2 - 34, cy - h // 2 + 28, cx + w // 2 - 22, cy - h // 2 + 40), fill=ICON)
    # --- Gal 5 furniture ---
    def header(self, left, chip, right=None):
        L = self.L; d = self.d
        spaced(d, L["hdr"], left, sans(26, "Bold"), GOLD, 5)
        cx, cy, ch = L["chip"]
        f = sans(36, "Bold"); sp = 4; w = spaced_w(chip, f, sp); px = 40
        d.rounded_rectangle((cx, cy, cx + w + 2 * px, cy + ch), radius=14, fill=GOLD)
        spaced(d, (cx + px, cy + (ch - 36 * 1.2) / 2 - 1), chip, f, CREAM, sp)
        if right:
            f = sans(26, "Medium"); d.text((L["right"][0] - f.getlength(right), L["right"][1]), right, font=f, fill=MUTED)
    def bar_zone(self, zone_h):
        x, y, w = self.L["bar"]; self.d.rectangle((x, y, x + w - 1, y + zone_h), fill=GOLD)
    def zone_text(self, paras, hi_scale=1.0, bottom_reserve=0):
        """Text box (Gal 5 position), vertically centred, shrinks to fit."""
        zx, zy, zw, zy1 = self.L["zone"]; zh = zy1 - zy - bottom_reserve
        sc = hi_scale
        while True:
            lines, h = flow_layout(paras, sc, zw)
            if h <= zh or sc <= 0.35: break
            sc -= 0.02
        y0 = zy + (zh - h) / 2
        for ly, toks in lines:
            for (x, w, f, color) in toks: self.d.text((zx + x, y0 + ly), w, font=f, fill=color)
        return sc
    def card(self, label, paras, label_fill=GOLD):
        cx, cy, cw, chh = self.L["card"]; d = self.d
        d.rounded_rectangle((cx, cy, cx + cw, cy + chh), radius=26, fill=CARD, outline=EDGE, width=2)
        spaced(d, (cx + 36, cy + 43), label, sans(26, "Bold"), label_fill, 5)
        tw = cw - 72; th = chh - 104 - 30
        sc = 1.0
        while True:
            lines, h = flow_layout(paras, sc, tw)
            if h <= th or sc <= 0.4: break
            sc -= 0.02
        for ly, toks in lines:
            for (x, w, f, color) in toks: d.text((cx + 36 + x, cy + 104 + ly), w, font=f, fill=color)
    def save(self, n):
        p = os.path.join(OUT, self.fmt + ("_key" if self.key else "")); os.makedirs(p, exist_ok=True)
        self.im.save(os.path.join(p, f"{n:02d}.png"), optimize=True)

def P(runs, after=0.0, lh=1.2): return dict(runs=runs, after=after, lh=lh)
def R(text, kind, size, color, nosplit=False): return (text, kind, size, color, nosplit)

def build_slides():
    S = []  # list of dict(kind, label, ...)
    S.append(dict(kind="title", label="Title"))
    S.append(dict(kind="flow", label="The flow"))
    S.append(dict(kind="part", label="Part 1: The Read", part="PART 1", title="The Read", sub="The whole chapter, two or three verses at a time."))
    for i, (a, b) in enumerate(C.READ):
        S.append(dict(kind="read", label=f"Read vv. {a}\u2013{b}" if a != b else f"Read v. {a}", a=a, b=b, listen=C.LISTEN_FOR[i]))
    S.append(dict(kind="part", label="Part 2: Verse by Verse", part="PART 2", title="Verse by Verse", sub="Slow down. Let each verse ask you something."))
    for m in C.MOVEMENTS:
        S.append(dict(kind="move", label=f"Movement {m[0]}: {m[4]}", m=m))
        for v in range(m[5], m[6] + 1):
            S.append(dict(kind="verse", label=f"Verse {v}", v=v))
    S.append(dict(kind="your", label="Your Move"))
    S.append(dict(kind="closev", label=f"Close: verse {C.CLOSE_VERSE}", v=C.CLOSE_VERSE))
    S.append(dict(kind="prayer", label="Prayer + site"))
    return S

def draw(s, n, N, sl):
    Z = s.L["sizes"]; kind = sl["kind"]; V = s.vert
    def qcard(label, text): s.card(label, [P([R(text, "sans", Z["q"], WHITE)], 0, 1.3)])
    if kind == "title":
        s.header("SUNDAY", "GALATIANS 6")
        lines = C.TITLE_LINES_VERT if V else C.TITLE_LINES_VERT   # three short lines fit the Gal 5 text column
        paras = [P([R(l, "serif", Z["big"], WHITE)], 0, 1.12) for l in lines]
        paras[-1]["after"] = 0.35
        paras.append(P([R("Galatians 6:1\u201318  \u00b7  KJV", "sansm", Z["sub"], CLAY)], 0, 1.2))
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1]); s.zone_text(paras)
        s.card("TODAY", [P([R(t, "sans", Z["q"], WHITE)], 0.2, 1.25) for t in C.TRIAD])
    elif kind == "flow":
        s.header("GALATIANS 6", "THE FLOW")
        paras = []
        for m in C.MOVEMENTS:
            paras.append(P([R(m[0] + "  ", "sansm", Z["flow_n"], GOLD, True), R(m[1], "sansm", Z["flow_t"], WHITE, False), R("   " + m[2], "sansm", Z["flow_v"], GOLD, True)], 0.1, 1.2))
            paras.append(P([R(m[3], "serif", Z["flow_d"], DESC)], 0.45, 1.2))
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1]); s.zone_text(paras)
        s.card("HOW WE WALK IT", [P([R("Read the whole chapter. Then one verse at a time.", "sans", Z["q"], WHITE)], 0, 1.3)])
    elif kind == "part":
        s.header("GALATIANS 6", sl["part"])
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1]); s.zone_text([P([R(sl["title"], "serif", Z["part"], WHITE)], 0, 1.15)])
        if sl["part"] == "PART 1": s.card("GALATIANS 6:1\u201318", [P([R(sl["sub"], "sans", Z["q"], WHITE)], 0, 1.3)])
        else: s.card("ONE VERSE. ONE QUESTION.", [P([R(sl["sub"], "sans", Z["q"], WHITE)], 0, 1.3)])
    elif kind == "move":
        m = sl["m"]
        s.header("GALATIANS 6", f"{m[0]} \u00b7 {m[2].upper()}")
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1]); s.zone_text([P([R(m[4], "serif", Z["part"], WHITE)], 0, 1.15)])
        s.card(m[1], [P([R(m[3], "sans", Z["q"], WHITE)], 0, 1.3)])
    elif kind == "read":
        a, b = sl["a"], sl["b"]
        k = [i for i, (x, y) in enumerate(C.READ) if x == a][0] + 1
        s.header("GALATIANS 6", f"READ {a}\u2013{b}" if a != b else f"READ {a}", f"Read {k} of {len(C.READ)}")
        paras = [P([R(f"{v}  ", "sansm", Z["num"], GOLD, True), R(curly(C.KJV[v]), "serif", Z["read"], WHITE)], 0.35, 1.2) for v in range(a, b + 1)]
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1]); s.zone_text(paras)
        qcard("LISTEN FOR", sl["listen"])
    elif kind == "verse":
        v = sl["v"]; q_, note = C.VERSES[v]
        s.header("GALATIANS 6", f"VERSE {v}", f"{v} of 18")
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1])
        s.zone_text([P([R(q(curly(C.KJV[v])), "serif", Z["verse"], WHITE)], 0, 1.2)], bottom_reserve=60 if note else 0)
        if note:
            zx, zy, zw, zy1 = s.L["zone"]
            spaced(s.d, (zx, zy1 - 48), note, sans(Z["note"], "Bold"), MUTED, 3)
        qcard("QUESTION", q_)
    elif kind == "your":
        s.header("GALATIANS 6", "YOUR MOVE", "Go do this")
        paras = [P([R(f"{i}   ", "sansm", Z["q"], GOLD, True), R(t, "sansm", Z["q"], WHITE)], 0.4, 1.25) for i, t in enumerate(C.YOUR_MOVE, 1)]
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1]); s.zone_text(paras)
        s.card("SAY IT OUT LOUD", [P([R(C.SAY_IT, "sans", Z["q"], WHITE)], 0, 1.3)])
    elif kind == "closev":
        v = sl["v"]
        s.header("GALATIANS 6", f"VERSE {v}")
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1])
        s.zone_text([P([R(q(curly(C.KJV[v])), "serif", Z["close"], WHITE)], 0.3, 1.2), P([R(f"GALATIANS 6:{v}", "sansm", Z["ref"], CLAY)], 0, 1.2)])
        s.card("GALATIANS 6", [P([R("Grow deep. Think biblically.", "sans", Z["q"], WHITE)], 0, 1.3)])
    elif kind == "prayer":
        s.header("GALATIANS 6", "NEED PRAYER?")
        s.bar_zone(s.L["zone"][3] - s.L["zone"][1])
        s.zone_text([P([R("Text", "serif", Z["big"], WHITE)], 0, 1.12), P([R("844-320-PRAY", "serif", Z["big"], CLAY)], 0.3, 1.12), P([R("for prayer", "sans", Z["q"], WHITE)], 0, 1.2)])
        s.card("ONLINE", [P([R("staytheway.com", "sansb", Z["q"] + 8, GOLD)], 0, 1.3)])

def check_slots():
    """Every text/card rectangle must stay clear of the camera slot."""
    for fmt, L in LAYOUT.items():
        sx0, sy0, sx1, sy1 = SLOT[fmt]
        zx, zy, zw, zy1 = L["zone"]; cx, cy, cw, ch = L["card"]
        for name, (x0, y0, x1, y1) in dict(zone=(L["bar"][0], zy, zx + zw, zy1), card=(cx, cy, cx + cw, cy + ch), chip=(L["chip"][0], L["chip"][1], L["chip"][0] + 500, L["chip"][1] + L["chip"][2]), right=(L["right"][0] - 400, L["right"][1], L["right"][0], L["right"][1] + 40)).items():
            assert x1 <= sx0 or x0 >= sx1 or y1 <= sy0 or y0 >= sy1, (fmt, name)

def main():
    check_slots()
    S = build_slides(); N = len(S)
    for fmt in ("wide", "vert"):
        for key in (False, True):
            for i, sl in enumerate(S, 1):
                s = Slide(fmt, key); draw(s, i, N, sl); s.save(i)
    json.dump([dict(n=i, kind=sl["kind"], label=sl["label"]) for i, sl in enumerate(S, 1)], open(os.path.join(OUT, "src", "slides.json"), "w"), indent=1)
    print("slides:", N)
if __name__ == "__main__":
    main()
