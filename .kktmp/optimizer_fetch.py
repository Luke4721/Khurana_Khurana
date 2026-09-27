#!/usr/bin/env python3
"""Re-fetch media via live /_next/image optimizer (direct path first, optimizer fallback)."""
import os, re, subprocess, sys, urllib.parse

BASE = "https://momentolegal.com"
paths = [l.strip() for l in open(".kktmp/media.txt") if l.strip()]
fails = []

def try_url(url, out):
    r = subprocess.run(["curl", "-sfL", "--retry", "2", "--max-time", "90", "-o", out, url],
                       capture_output=True)
    return r.returncode == 0 and os.path.getsize(out) > 0

for p in paths:
    out = "public" + p
    os.makedirs(os.path.dirname(out), exist_ok=True)
    enc = urllib.parse.quote(p, safe="")
    ok = try_url(BASE + p, out)
    if not ok:
        ok = try_url(f"{BASE}/_next/image?url={enc}&w=1920&q=75", out)
    if not ok:
        ok = try_url(f"{BASE}/_next/image?url={enc}&w=1200&q=75", out)
    if ok:
        print("OK  ", p)
    else:
        if os.path.exists(out):
            os.remove(out)
        fails.append(p)
        print("FAIL", p)

print(f"\ndone: {len(paths)-len(fails)} ok, {len(fails)} fail")
for f in fails:
    print("  MISSING:", f)
