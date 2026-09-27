#!/usr/bin/env python3
"""Stack identity pair GROUPS onto working identity base; find the breaking pair."""
import sys
sys.path.insert(0, "rebrand")
from engine31 import apply_pairs_v31
from brand import identity_pairs

src = open("public/ab-identity.html", encoding="utf-8").read()  # WORKS in browser
ip = identity_pairs()

groups = {
    "g0meta": ip[0:1],     # title
    "g1desc": ip[1:2],     # description
    "g2brand": ip[2:8],    # brand names
    "g3hero": ip[8:11],    # hero
    "g4contact": ip[11:],  # email + socials
}

for name, subset in groups.items():
    new, mh, fh, rm = apply_pairs_v31(src, subset)
    open(f"public/ab-{name}.html", "w", encoding="utf-8").write(new)
    print(f"built ab-{name}: markup={mh} flight={fh}")
