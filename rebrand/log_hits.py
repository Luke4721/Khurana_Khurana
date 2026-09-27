#!/usr/bin/env python3
"""Log every 'Momento' occurrence in flight with context; classify T-row vs gap."""
import sys, json, re
sys.path.insert(0, "rebrand")

FLIGHT_PUSH = re.compile(r'(self\.__next_f\.push\(\[1,")((?:[^"\\]|\\.)*)("\]\))')
src = open("public/ab-ctrl.html", encoding="utf-8").read()
matches = list(FLIGHT_PUSH.finditer(src))
joined = "".join(json.loads(f'"{m.group(2)}"' ) for m in matches)

# compute T-row spans (original lengths)
spans = []
pos = 0
for m in re.finditer(r'([0-9a-f]+):T([0-9a-f]+),', joined):
    if m.start() < pos:
        continue
    ln = int(m.group(2), 16)
    spans.append((m.end(), m.end() + ln, m.group(1)))
    pos = m.end() + ln

def classify(i):
    for a, b, rid in spans:
        if a <= i < b:
            return f"T-row {rid}"
    return "GAP"

for k, m in enumerate(re.finditer(r'Momento', joined)):
    i = m.start()
    print(f"{k:2d} [{classify(i):12s}] ...{joined[max(0,i-55):i+45]}...".replace("\n", "⏎"))
