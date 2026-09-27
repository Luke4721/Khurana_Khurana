#!/usr/bin/content
import sys, re
sys.path.insert(0, "rebrand")
from engine import flight_strings

for page in ["public/team/abdallah-al-nassiry.html", "public/team.html", "public/index.html"]:
    d = "\n".join(s for s in flight_strings(open(page, encoding="utf-8", errors="ignore").read()) if s is not None)
    rows = list(re.finditer(r'([0-9a-f]+):T([0-9a-f]+),', d))
    ok = 0; tot = 0; bad = []
    for m in rows[:200]:
        rid, ln = m.group(1), m.group(2)
        try:
            n = int(ln, 16)
        except ValueError:
            continue
        seg = d[m.end(): m.end()+n]
        # heuristic: segment should not run into another row header too early
        looks_clean = not re.search(r'[0-9a-f]{1,6}:[TIWEF]\b', seg[:40])
        tot += 1
        if looks_clean: ok += 1
        else: bad.append((rid, ln, seg[:50]))
    print(page, f"T-rows: {len(rows)}, clean@chars-semantics: {ok}/{tot}")
    if bad: print("  sample bad:", bad[0])
