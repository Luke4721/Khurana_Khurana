#!/usr/bin/env python3
"""A/B test: which migration layer breaks hydration? Build 3 variants of index.html."""
import re, json, sys, subprocess
sys.path.insert(0, "rebrand")
from engine2 import FLIGHT_RE, _fix_t_lengths
from brand import PALETTE, identity_pairs

# A) pristine control: fresh from live
subprocess.run(["curl", "-sfL", "-o", "public/ab-pristine.html", "https://momentolegal.com/"], check=True)

# B) identity re-encode: consolidate flight chunks, edit nothing
src = open("public/ab-pristine.html", encoding="utf-8").read()
matches = list(FLIGHT_RE.finditer(src))
parts = [json.loads(f'"{m.group(1)}"') for m in matches]
joined = "".join(parts)
fixed = _fix_t_lengths(joined)
new_raw = json.dumps(fixed, ensure_ascii=False)[1:-1]
out, pos = [], 0
for idx, m in enumerate(matches):
    out.append(src[pos:m.start(1)])
    out.append(new_raw if idx == 0 else "")
    pos = m.end(1)
out.append(src[pos:])
open("public/ab-identity.html", "w", encoding="utf-8").write("".join(out))

# C) current migrated index (on disk)
print("variants ready: ab-pristine, ab-identity, index (migrated)")
