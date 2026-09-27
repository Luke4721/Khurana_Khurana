#!/usr/bin/env python3
"""Rebuild test variants with the CORRECT engine (v3.1)."""
import sys
sys.path.insert(0, "rebrand")
from engine31 import apply_pairs_v31
from brand import identity_pairs

pairs = identity_pairs()
src = open("public/ab-ctrl.html", encoding="utf-8", errors="ignore").read()

def build(name, subset):
    new, mh, fh, rm = apply_pairs_v31(src, subset)
    open(f"public/ab-{name}.html", "w", encoding="utf-8").write(new)
    print(f"built ab-{name}: {len(subset)} pairs, markup={mh} flight={fh}")

build("v31all", pairs)
build("v31u2", pairs[4:8])   # the subset that failed under v3
