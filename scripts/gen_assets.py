#!/usr/bin/env python3
"""Builds the animated ASCII-halftone SVGs used by the README.

    python3 scripts/gen_assets.py

Writes assets/banner.svg and assets/divider.svg. Pure stdlib, no installs.
Change the constants below (name, colours, frame count) and re-run.
"""
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "assets"))

NAME = "NAFEESIUM"
TAGLINE = "indie dev — games, tools, small obsessions"
HINT = "[ click for the live version ]"
BG, AMBER, BLUE = "#161821", "#E0A458", "#7EC8E3"

RAMP = " .:-=+*#%@"      # halftone ramp, light to dense
NB = " "            # non-breaking space: renderers never collapse it
WIDTH, CW, LH = 960, 8, 16
COLS = WIDTH // CW       # 120 columns
ROWS = 17
FRAMES, DT = 20, 0.15    # 20 frames x 0.15s = a 3s seamless loop
LOOP = FRAMES * DT
PAD_TOP = 14
FS = 13.3
STILL = FRAMES // 2      # frame shown when animation is off / unsupported

# Banner: a recording of the interactive page. GitHub strips scripts and an <img> SVG gets no
# pointer events, so instead of reacting to YOUR cursor, a ghost cursor runs the same heat /
# glitch / ripple model from index.html and the result is baked into the frames.
BF, BDT = 36, 0.1        # 36 frames x 0.1s = 3.6s loop
BSTILL = 6
GLITCH = "01<>/\\|[]{}#$%&*+=~^"
CREAM, LIGHT_AMBER = "#fff3da", "#f2c98a"
CLICKS = (0, BF // 2)    # frames where the ghost "clicks" and sends a ripple

# 5x7 block font: only the letters the name needs.
FONT = {
    "N": ["10001", "11001", "10101", "10101", "10011", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
}


def build_mask():
    sx, gap = 2, 2  # letters are drawn 2 cells wide per pixel (cells are tall)
    total = len(NAME) * 5 * sx + (len(NAME) - 1) * gap
    left = (COLS - total) // 2
    top = (ROWS - 7) // 2
    mask = [[0] * COLS for _ in range(ROWS)]
    for i, ch in enumerate(NAME):
        x0 = left + i * (5 * sx + gap)
        for gy, line in enumerate(FONT[ch]):
            for gx, bit in enumerate(line):
                if bit == "1":
                    for k in range(sx):
                        mask[top + gy][x0 + gx * sx + k] = 1
    glow = [[0] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            if mask[r][c]:
                continue
            glow[r][c] = int(any(
                0 <= r + dr < ROWS and 0 <= c + dc < COLS and mask[r + dr][c + dc]
                for dr in (-1, 0, 1) for dc in (-2, -1, 0, 1, 2)
            ))
    return mask, glow, top


MASK, GLOW, TOP = build_mask()


def dens(c, r, p):
    """Background halftone density 0..1. Integer multiples of p keep the loop seamless."""
    x, y = c, r * 2.0
    v = math.sin(x * 0.085 + p)
    v += math.sin(y * 0.21 - p)
    v += math.sin((x * 0.6 + y) * 0.06 + p)
    v += math.sin(math.hypot(x - COLS * 0.5, y - ROWS) * 0.16 - 2 * p)
    v = (v + 4) / 8
    t = min(1.0, max(0.0, (v - 0.42) * 2.0)) ** 1.25
    edge = min(1.0, min(c, COLS - 1 - c) / 14.0)
    return t * (0.35 + 0.65 * edge) * 0.85


def ramp(d):
    return RAMP[max(0, min(9, int(d * 9 + 0.5)))]


def row_y(r, pad=PAD_TOP):
    return pad + r * LH + 12


def text(cls, y, s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", NB)
    return (f'<text class="{cls}" x="0" y="{y}" textLength="{WIDTH}" '
            f'lengthAdjust="spacing">{s}</text>')


def ghost(f):
    """Ghost cursor in grid pixels. A closed figure-eight, so the loop is seamless."""
    a = 2 * math.pi * f / BF
    return (WIDTH * (0.5 + 0.38 * math.sin(a)),
            ROWS * LH * (0.5 + 0.30 * math.sin(2 * a + 0.6)))


def simulate_heat():
    """Same model as index.html: stamp a soft blob under the cursor, diffuse, fade.
    Runs two laps and keeps the second, so the heat trail wraps around cleanly."""
    sub = 4                                      # sub-steps per frame, smooths the trail
    fade = 0.93 ** (60 * BDT / sub)
    R2 = 70.0 ** 2
    heat = [[0.0] * COLS for _ in range(ROWS)]
    kept = []
    for step in range(BF * 2):
        f = step % BF
        x0, y0 = ghost(f - 1)
        x1, y1 = ghost(f)
        speed = math.hypot(x1 - x0, y1 - y0) / BDT
        strength = min(1.0, 0.38 + speed / 1400)
        for s in range(sub):
            t = (s + 1) / sub
            gx, gy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for r in range(ROWS):
                dy = (r + 0.5) * LH - gy
                for c in range(COLS):
                    dx = (c + 0.5) * CW - gx
                    v = math.exp(-(dx * dx + dy * dy) / R2 * 2.2) * strength
                    if v > heat[r][c]:
                        heat[r][c] = v
            new = [[0.0] * COLS for _ in range(ROWS)]
            for r in range(ROWS):
                for c in range(COLS):
                    n = ((heat[r][c - 1] if c else 0.0) + (heat[r][c + 1] if c < COLS - 1 else 0.0) +
                         (heat[r - 1][c] if r else 0.0) + (heat[r + 1][c] if r < ROWS - 1 else 0.0))
                    new[r][c] = (heat[r][c] * 0.78 + n * 0.25 * 0.22) * fade
            heat = new
        if step >= BF:
            kept.append([row[:] for row in heat])
    return kept


def ring_at(f, X, Y):
    """Ripple strength at pixel (X, Y) in frame f, from every ghost click."""
    total = 0.0
    for e in CLICKS:
        age = ((f - e) % BF) * BDT
        cx, cy = ghost(e)
        off = (math.hypot(X - cx, Y - cy) - age * 520) / 38
        total += math.exp(-off * off) * math.exp(-age * 1.3) * 0.9
    return min(1.0, total)


LAYERS = ("b", "w", "c", "g", "n", "n2", "n3")


def banner_frame(f, heat, rng):
    p = 2 * math.pi * f / BF
    grid = {k: [[NB] * COLS for _ in range(ROWS)] for k in LAYERS}
    for r in range(ROWS):
        Y = (r + 0.5) * LH
        for c in range(COLS):
            X = (c + 0.5) * CW
            h = heat[r][c]
            ring = ring_at(f, X, Y)
            warm = h + ring
            if MASK[r][c]:
                # letters: dense so they read at a glance, brighter and glitchy where it is hot
                shimmer = 0.5 + 0.5 * math.sin(c * 0.7 + r * 1.3 + p * 3)
                d = min(1.0, 0.72 + 0.2 * shimmer + h * 0.35 + ring * 0.4)
                ch = RAMP[min(9, max(7, int(d * 9 + 0.5)))]
                layer = "n" if warm < 0.3 else ("n2" if warm < 0.6 else "n3")
                if h > 0.3 and rng.random() < (h - 0.25) * 0.9:
                    ch = rng.choice(GLITCH)
                    layer = "n3" if rng.random() < 0.4 else "n2"
                grid[layer][r][c] = ch
                continue
            if GLOW[r][c]:
                d = h * 0.85 + ring * 0.9
                if d < 0.1:                      # knockout halo: mostly blank so edges stay crisp
                    if 0.5 + 0.5 * math.sin(c * 0.9 - r * 1.7 + p * 2) > 0.7:
                        grid["g"][r][c] = "."
                    continue
            else:
                zone = 0.45 if TOP - 1 <= r <= TOP + 7 else 1.0   # calmer field behind the name
                d = dens(c, r, p) * zone + h * 0.85 + ring * 0.9
            ch = ramp(d)
            if ch == " ":
                continue
            grid["c" if warm > 0.8 else "w" if warm > 0.35 else "b"][r][c] = ch

    # the ghost cursor itself, a little [+] reticle
    gx, gy = ghost(f)
    cx, cy = int(gx / CW), int(gy / LH)
    for dx, ch in ((-1, "["), (0, "+"), (1, "]")):
        if 0 <= cx + dx < COLS:
            for k in LAYERS:
                grid[k][cy][cx + dx] = NB
            grid["n3"][cy][cx + dx] = ch

    out = []
    for r in range(ROWS):
        for k in LAYERS:
            row = "".join(grid[k][r])
            if row.strip(NB):
                out.append(text(k, row_y(r), row))
    return out


def anim_css(extra="", frames=FRAMES, dt=DT):
    pct = 100 / frames
    loop = frames * dt
    return f"""
text{{font-family:'Fira Code','JetBrains Mono','SFMono-Regular',Menlo,Consolas,'Liberation Mono','Courier New',monospace;font-size:{FS}px;white-space:pre}}
.f{{opacity:0;animation:s {loop:.2f}s step-end infinite}}
.k{{opacity:1}}
@keyframes s{{0%{{opacity:1}}{pct - 0.05:.3f}%{{opacity:0}}100%{{opacity:0}}}}
.b{{fill:{BLUE};fill-opacity:.5}}
.g{{fill:{AMBER};fill-opacity:.38}}
.n{{fill:{AMBER}}}
.a{{fill:{AMBER}}}
{extra}
@media (prefers-reduced-motion:reduce){{.f{{animation:none}}.cur{{animation:none}}}}
"""


def frame_group(f, rows, frames=FRAMES, dt=DT, still=STILL):
    delay = 0.0 if f == 0 else (frames - f) * dt   # negative delay: no load-time overlap
    cls = "f k" if f == still else "f"
    return f'<g class="{cls}" style="animation-delay:-{delay:.3f}s">' + "".join(rows) + "</g>"


def write_banner():
    height = PAD_TOP + ROWS * LH + 40
    sub_y = PAD_TOP + ROWS * LH + 22
    n = len("▸ " + TAGLINE)
    extra = (".sub{fill:" + BLUE + ";fill-opacity:.8}.hint{fill:" + AMBER +
             ";fill-opacity:.55}.cur{fill:" + AMBER + ";animation:blk 1s step-end infinite}"
             "@keyframes blk{50%{opacity:0}}"
             ".w{fill:" + AMBER + ";fill-opacity:.8}.c,.n3{fill:" + CREAM + "}.n2{fill:" + LIGHT_AMBER + "}")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" '
        f'aria-label="{NAME} — ASCII halftone banner with a ghost cursor">',
        f"<style>{anim_css(extra, BF, BDT)}</style>",
        f'<rect width="100%" height="100%" fill="{BG}"/>',
    ]
    rng = random.Random(7)
    for f, heat in enumerate(simulate_heat()):
        parts.append(frame_group(f, banner_frame(f, heat, rng), BF, BDT, BSTILL))
    parts.append(
        f'<text class="sub" x="16" y="{sub_y}" textLength="{n * CW}" lengthAdjust="spacing">'
        f"▸{NB}{TAGLINE.replace(' ', NB)}</text>"
    )
    parts.append(f'<rect class="cur" x="{16 + n * CW + 4}" y="{sub_y - 11}" width="8" height="14"/>')
    parts.append(
        f'<text class="hint" x="{WIDTH - 16}" y="{sub_y}" text-anchor="end" '
        f'textLength="{len(HINT) * CW}" lengthAdjust="spacing">{HINT.replace(" ", NB)}</text>'
    )
    parts.append("</svg>")
    path = os.path.join(OUT, "banner.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    return path


def divider_frame(f):
    p = 2 * math.pi * f / FRAMES
    glint = f / FRAMES * (COLS + 40) - 20
    bg = [[NB] * COLS for _ in range(3)]
    am = [[NB] * COLS for _ in range(3)]
    for c in range(COLS):
        w = 1 + 0.95 * math.sin(c * 0.13 + p) * (0.6 + 0.4 * math.sin(c * 0.05 - p))
        for r in range(3):
            idx = min(7, int(math.exp(-((r - w) ** 2) / 0.45) * 7.4))   # lighter than the banner: it is only a rule
            if idx <= 0:
                continue
            (am if abs(c - glint) < 7 else bg)[r][c] = RAMP[idx]
    rows = []
    for r in range(3):
        y = row_y(r, pad=4)
        rows.append(text("b", y, "".join(bg[r])))
        if any(ch != NB for ch in am[r]):
            rows.append(text("a", y, "".join(am[r])))
    return rows


def write_divider():
    height = 4 * 2 + 3 * LH
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" role="img" aria-label="divider">',
        f"<style>{anim_css()}</style>",
    ]
    for f in range(FRAMES):
        parts.append(frame_group(f, divider_frame(f)))
    parts.append("</svg>")
    path = os.path.join(OUT, "divider.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    return path


def preview(f=STILL):
    """Print one banner frame as plain text (letters = uppercase block, field = ramp)."""
    p = 2 * math.pi * f / FRAMES
    for r in range(ROWS):
        line = ""
        for c in range(COLS):
            line += "#" if MASK[r][c] else ("+" if GLOW[r][c] else ramp(dens(c, r, p)))
        print(line)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for p in (write_banner(), write_divider()):
        print(f"{os.path.relpath(p)}  {os.path.getsize(p) / 1024:.0f} KB")
