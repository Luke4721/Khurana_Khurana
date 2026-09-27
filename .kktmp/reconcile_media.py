#!/usr/bin/env python3
"""Reconcile teams/insights media against what the fresh HTML references; fill gaps from .kktmp."""
import re, glob, os, shutil, subprocess

def is_image(p):
    try:
        out = subprocess.run(["file", "-b", "--mime-type", p], capture_output=True, text=True).stdout.strip()
        return out.startswith("image/")
    except Exception:
        return False

# 1. authoritative refs from fresh html (unescaped + escaped forms)
txt_all = ""
for f in glob.glob("public/**/*.html", recursive=True):
    txt_all += open(f, encoding="utf-8", errors="ignore").read()
txt_all = txt_all.replace("\\u002F", "/")
refs = set(re.findall(r"images/(teams|insights)/([A-Za-z0-9_.-]+\.(?:png|jpg|jpeg|webp|svg))", txt_all))
print("html-referenced team/insight images:", len(refs))

# 2. fill gaps from .kktmp sources
src_map = {os.path.basename(p): p for p in glob.glob(".kktmp/photos/*") + glob.glob(".kktmp/covers/*") + glob.glob(".kktmp/covers/00*") }
missing, fixed = [], 0
for d, name in sorted(refs):
    out = f"public/images/{d}/{name}"
    if os.path.exists(out) and is_image(out):
        continue
    missing.append(f"{d}/{name}")
    if name in src_map and is_image(src_map[name]):
        shutil.copy(src_map[name], out)
        fixed += 1
        print("restored from kktmp:", f"{d}/{name}")
    else:
        # last resort: use dummy cover so nothing 404s (content phase will overwrite)
        dummy = "public/images/insights/dummy-insight-1.png"
        if os.path.exists(dummy):
            shutil.copy(dummy, out)
            print("placeholder:", f"{d}/{name}")

print(f"gaps found: {len(missing)}, restored: {fixed}")
for m in missing:
    p = f"public/images/{m}"
    if not os.path.exists(p):
        print("STILL MISSING:", m)

# 3. validate every team/insight image is a real image
bad = []
for p in glob.glob("public/images/teams/*") + glob.glob("public/images/insights/*"):
    if os.path.isfile(p) and not is_image(p):
        bad.append(p)
print("invalid image files:", bad if bad else "none")
