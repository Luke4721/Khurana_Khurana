#!/usr/bin/env python3
"""Dump flight contexts of key strings."""
import sys, json, re

FLIGHT_PUSH = re.compile(r'(self\.__next_f\.push\(\[1,")((?:[^"\\]|\\.)*)("\]\))')

joined = "".join(json.loads(f'"{m.group(2)}"') for m in FLIGHT_PUSH.finditer(open(sys.argv[1], encoding="utf-8").read()))
for probe in sys.argv[2:]:
    ms = list(re.finditer(re.escape(probe), joined))
    print(f"--- {probe!r}: {len(ms)} hits")
    for m in ms[:3]:
        print("   ", joined[max(0, m.start()-70):m.start()+45].replace("\n", "|"))
