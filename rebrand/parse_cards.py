#!/usr/bin/env python3
"""Extract the team card array (with $ref descriptions resolved) from team.html flight."""
import sys, re, json
sys.path.insert(0, "rebrand")
from engine import flight_strings

d = "\n".join(s for s in flight_strings(open("public/team.html", encoding="utf-8", errors="ignore").read()) if s is not None)

# description strings live in rows like  29:T2f1,<text>
descs = {}
for m in re.finditer(r'([0-9a-f]+):T([0-9a-f]+),', d):
    rid, ln = m.group(1), m.group(2)
    start = m.end()
    try:
        n = int(ln, 16)
    except ValueError:
        continue
    descs[rid] = d[start:start+n]

# anchor on a known card, backtrack to the enclosing '['
i = d.find('{"name":"Abdallah')
assert i >= 0, "card entry not found"
j = d.rfind('[', 0, i)
assert j >= 0, "enclosing bracket not found"

depth = 0; k = j; in_str = False; esc = False
while True:
    c = d[k]
    if in_str:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': in_str = False
    else:
        if c == '"': in_str = True
        elif c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                k += 1; break
    k += 1
arr = json.loads(d[j:k])
print("cards:", len(arr))

out = []
for c in arr:
    ref = (c.get("description") or "").lstrip("$")
    out.append({
        "name": c["name"], "role": c["role"], "image": c["image"],
        "email": c.get("email",""), "linkedin": c.get("linkedin",""),
        "desc_id": ref, "desc": descs.get(ref, "")
    })
json.dump(out, open(".kktmp/fresh_cards.json", "w"), ensure_ascii=False, indent=1)
for c in out[:10]:
    print(f"  {c['name'][:32]!r:36} {c['role'][:18]!r:22} {c['image']} desc:{len(c['desc'])}ch")
print("\nsample desc:", out[1]["desc"][:160])
