#!/usr/bin/env python3
"""Chunk pass: apply identity+palette pairs to every JS/CSS under public/_next/static."""
import sys
from pathlib import Path

sys.path.insert(0, "rebrand")
from engine import apply_pairs
from brand import PALETTE, identity_pairs

pairs = [(o, n) for o, n in (PALETTE + identity_pairs())]
pairs += [
    ("info@momentolegal.com", "info@khuranaandkhurana.com"),
    ("0212 890 80 55", "+91 89202 69831"),
    ("Istanbul / Turkey", "Delhi NCR / India"),
]

total = 0
files = 0
for f in Path("public/_next/static").rglob("*"):
    if f.is_file() and f.suffix in {".js", ".css", ".svg"}:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        new, n = apply_pairs(txt, pairs)
        if n:
            f.write_text(new, encoding="utf-8")
            total += n
            files += 1
print(f"chunks: {total} replacements in {files} files")
