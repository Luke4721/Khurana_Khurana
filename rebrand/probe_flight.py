#!/usr/bin/env python3
"""Probe the decoded RSC flight data to understand card/field structures."""
import sys, re, json
sys.path.insert(0, "rebrand")
from engine import flight_strings

def decoded(path):
    out = []
    for s in flight_strings(open(path, encoding="utf-8", errors="ignore").read()):
        if s is not None:
            out.append(s)
    return "\n".join(out)

def show(path, needle, before=80, after=400, label=""):
    d = decoded(path)
    i = d.find(needle)
    print(f"--- {label or path} around {needle!r} (idx {i}) ---")
    if i >= 0:
        print(d[max(0, i-before): i+after].replace("\n", "⏎")[:after+before])
    print()

show("public/team.html", "Abdallah Al Nassiry", label="team card")
show("public/team.html", "teams/", label="team photo ref", after=300)
show("public/team/abdallah-al-nassiry.html", "Abdallah", label="profile name", after=400)
show("public/team/abdallah-al-nassiry.html", "Partner", label="profile role", after=300)
