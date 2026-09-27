#!/usr/bin/env python3
"""Graduated A/B: find which pair set breaks hydration."""
import sys, subprocess, json
sys.path.insert(0, "rebrand")
from engine3 import apply_pairs_v3
from brand import PALETTE, identity_pairs

src = open("public/ab-ctrl.html", encoding="utf-8", errors="ignore").read()

def build(name, pairs):
    new, *_ = apply_pairs_v3(src, pairs)
    open(f"public/ab-{name}.html", "w", encoding="utf-8").write(new)
    print("built", name)

build("palette", [(o, n) for o, n in PALETTE])
build("text", identity_pairs())
build("both", [(o, n) for o, n in (PALETTE + identity_pairs())])
