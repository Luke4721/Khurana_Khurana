#!/usr/bin/env python3
"""Step 1: palette + identity across all HTML (v3) and JS/CSS chunks (plain)."""
import sys
from pathlib import Path

sys.path.insert(0, "rebrand")
from engine31 import process_file_v31
from brand import PALETTE, identity_pairs

# chunk pass runs via migrate_identity_chunks.py (plain apply_pairs, no flight)

pairs = [(o, n) for o, n in (PALETTE + identity_pairs())]

# contact rows (shared menu flight data on every page)
pairs += [
    ("info@momentolegal.com", "info@khuranaandkhurana.com"),
    ("0212 890 80 55", "+91 89202 69831"),
    ("Istanbul / Turkey", "Delhi NCR / India"),
]

# 1) all html pages through v3
total = 0
files = sorted(Path("public").rglob("*.html"))
for f in files:
    n = process_file_v31(f, pairs)
    if n > 0:
        total += n
print(f"identity: {total} replacements across {len(files)} pages")

print("IDENTITY-DONE (pages only; run migrate_identity_chunks.py for chunks)")
