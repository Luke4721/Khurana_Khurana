#!/usr/bin/env python3
"""Probe text blocks of the pages that still need mapping."""
import sys, re, json
sys.path.insert(0, "rebrand")
from blocks import _static_blocks, _flight_blocks

PAGES = [
    "public/about.html", "public/culture.html", "public/contact.html",
    "public/expertise.html", "public/expertise/arbitration.html",
    "public/insights.html", "public/insights/the-right-moment-to-act-in-corporate-disputes.html",
    "public/policies/privacy-policy.html", "public/404.html",
]

for p in PAGES:
    try:
        html = open(p, encoding="utf-8").read()
    except FileNotFoundError:
        print("MISSING", p); continue
    mb = _static_blocks(html)
    fb = _flight_blocks(html)
    print(f"\n=== {p} ===  markup blocks: {len(mb)}  flight blocks: {len(fb)}")
    for b in mb[:8]:
        print("  M:", b[:95])
    if fb:
        for b in fb[:4]:
            print("  F:", b[:95])
