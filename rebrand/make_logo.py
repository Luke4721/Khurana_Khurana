#!/usr/bin/env python3
"""Render K&K logo files at the exact dimensions of the originals they replace."""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

PUB = "public"
WHITE = (245, 241, 232, 255)      # cream-white
MAROON = (124, 3, 3, 255)         # K&K maroon #7C0303

# --- decompress Forum woff2 -> ttf so PIL can use it ---
os.makedirs(".kktmp/fonts", exist_ok=True)
ttf_path = ".kktmp/fonts/forum.ttf"
if not os.path.exists(ttf_path):
    r = subprocess.run(["python3", "-m", "fontTools.ttLib.woff2", "decompress",
                        f"{PUB}/fonts/forum-1.woff2", "-o", ttf_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("fonttools failed:", r.stderr[:300]); sys.exit(1)

def font(sz):
    return ImageFont.truetype(ttf_path, sz)

def text_w(draw, s, f, tracking=0):
    return sum(draw.textlength(c, font=f) + tracking for c in s) - tracking

# --- 1) header wordmark 322x76, white on transparent ---
W, H = 322, 76
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
label = "KHURANA & KHURANA"
# find the largest size that fits with tracking
for sz in range(30, 10, -1):
    f = font(sz)
    tr = max(1, sz // 6)
    if text_w(d, label, f, tr) <= W - 6:
        break
total_w = text_w(d, label, f, tr)
asc, desc = f.getmetrics()
y = (H - (asc + desc)) // 2
x = (W - total_w) / 2
for c in label:
    color = MAROON if c == "&" else WHITE
    d.text((x, y), c, font=f, fill=color)
    x += d.textlength(c, font=f) + tr
im.save(f"{PUB}/images/header/logo.png")
print("header logo:", im.size, "font", sz)

# --- 2) icon 134x134: maroon disc + cream K&K ---
S = 134
for out in [f"{PUB}/icon.png", f"{PUB}/apple-icon.png"]:
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([5, 5, S - 5, S - 5], fill=MAROON)
    fk = font(46)
    fa = font(30)
    wk, wa = d.textlength("K", font=fk), d.textlength("&", font=fa)
    total = wk + 8 + wa + 8 + wk
    x = (S - total) / 2
    asc, desc = fk.getmetrics()
    y = (S - (asc + desc)) // 2
    d.text((x, y), "K", font=fk, fill=WHITE); x += wk + 8
    ya = y + (fk.getmetrics()[0] - fa.getmetrics()[0])  # align baselines
    d.text((x, ya), "&", font=fa, fill=WHITE); x += wa + 8
    d.text((x, y), "K", font=fk, fill=WHITE)
    im.save(out)
    print("icon:", out, im.size)
