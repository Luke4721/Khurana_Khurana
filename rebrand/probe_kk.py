#!/usr/bin/env python3
"""Probe flight stream of a built page for KK strings and escaping forms."""
import re, json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "public/ab-v31all.html"
t = open(path, encoding="utf-8").read()
chunks = re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', t)
joined = "".join(json.loads(f'"{c}"') for c in chunks if c)
print("chunks:", len(chunks), "joined len:", len(joined))
print("flight has 'Khurana & Khurana':", "Khurana & Khurana" in joined)
print("flight has 'Khurana':", "Khurana" in joined)
print("flight has 'Momento':", "Momento" in joined)
for m in list(re.finditer(r"Khurana", joined))[:8]:
    print("ctx:", repr(joined[max(0, m.start()-8):m.start()+30]))
