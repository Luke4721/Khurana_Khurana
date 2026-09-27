#!/usr/bin/env python3
"""Real invariant: _fix_t_lengths must be identity on the JOINED flight stream."""
import sys, glob, json, re
sys.path.insert(0, "rebrand")
from engine import flight_strings
from engine2 import FLIGHT_RE, _fix_t_lengths

bad = 0
files = sorted(glob.glob("public/**/*.html", recursive=True))
for f in files:
    txt = open(f, encoding="utf-8", errors="ignore").read()
    matches = list(FLIGHT_RE.finditer(txt))
    if not matches:
        continue
    joined = ""
    for m in matches:
        joined += json.loads(f'"{m.group(1)}"')
    fixed = _fix_t_lengths(joined)
    if fixed != joined:
        bad += 1
        i = next((k for k in range(min(len(fixed), len(joined))) if fixed[k] != joined[k]), 0)
        print("DIFF", f, "at", i)
        print("  joined:", repr(joined[max(0,i-40):i+40]))
        print("  fixed :", repr(fixed[max(0,i-40):i+40]))
        if bad > 2:
            break
print(f"checked {len(files)} files, mismatches: {bad}")
