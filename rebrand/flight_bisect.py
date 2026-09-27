#!/usr/bin/env python3
"""Discriminator: is the poison the & character or the replacement locations?"""
import sys, json, re

FLIGHT_PUSH = re.compile(r'(self\.__next_f\.push\(\[1,")((?:[^"\\]|\\.)*)("\]\))')
src = open("public/ab-pristine.html", encoding="utf-8").read()

def build_flight_only(name, subset):
    matches = list(FLIGHT_PUSH.finditer(src))
    joined = "".join(json.loads(f'"{m.group(2)}"') for m in matches)
    hits = 0
    for old, new in subset:
        hits += joined.count(old)
        joined = joined.replace(old, new)
    if hits == 0:
        print(f"ab-{name}: no hits"); return
    out, pos, done = [], 0, False
    for m in matches:
        out.append(src[pos:m.start(2)])
        out.append(joined if not done else "")
        done = True
        pos = m.end(2)
    out.append(src[pos:])
    open(f"public/ab-{name}.html", "w", encoding="utf-8").write("".join(out))
    print(f"built ab-{name}: {subset}, hits {hits}")

build_flight_only("d1", [("Momento", "KHURANA KHURANA")])   # no ampersand
build_flight_only("d2", [("Momento", "Zzz")])               # neutral, same family
