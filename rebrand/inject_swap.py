#!/usr/bin/env python3
"""Inject <script src="/kk-swap.js" defer> into every HTML page <head>, idempotently."""
import re
from pathlib import Path

PUB = Path("public")
TAG = '<script src="/kk-swap.js" defer></script>'
n = 0
for f in PUB.rglob("*.html"):
    t = f.read_text(encoding="utf-8")
    if "kk-swap.js" in t:
        continue
    if "</head>" in t:
        t = t.replace("</head>", TAG + "</head>", 1)
        f.write_text(t, encoding="utf-8")
        n += 1
print(f"injected into {n} pages")
