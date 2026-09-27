#!/usr/bin/env python3
"""Diagnostic 2: flight name written with &amp; (HTML-escaped) instead of raw &."""
import sys, json, re
sys.path.insert(0, "rebrand")
from engine2 import segment_rewrite

FLIGHT_PUSH = re.compile(r'(self\.__next_f\.push\(\[1,")((?:[^"\\]|\\.)*)("\]\))')
src = open("public/ab-ctrl.html", encoding="utf-8").read()

matches = list(FLIGHT_PUSH.finditer(src))
parts = [json.loads(f'"{m.group(2)}"') for m in matches]
joined = "".join(parts)
fixed, hits, _ = segment_rewrite(joined, [("Momento", "Khurana &amp; Khurana")], None)
new_raw = json.dumps(fixed, ensure_ascii=False)[1:-1]
out, pos, done = [], 0, False
for m in matches:
    out.append(src[pos:m.start(2)])
    out.append(new_raw if not done else "")
    done = True
    pos = m.end(2)
out.append(src[pos:])
open("public/ab-diag2.html", "w", encoding="utf-8").write("".join(out))
print("built ab-diag2 with flight hits:", hits)
