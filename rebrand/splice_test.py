#!/usr/bin/env python3
"""Splice test: swap flight payloads between ctrl (pristine) and v31all (migrated).
Both share the same pristine chunk structure, so positional splicing is exact."""
import re, json

FLIGHT_PUSH = re.compile(r'(self\.__next_f\.push\(\[1,")((?:[^"\\]|\\.)*)("\]\))')

def chunks_of(path):
    return [m.group(2) for m in FLIGHT_PUSH.finditer(open(path, encoding="utf-8").read())]

def splice(dst_path, src_path, out_path):
    dst = open(dst_path, encoding="utf-8").read()
    src_chunks = chunks_of(src_path)
    dst_chunks = chunks_of(dst_path)
    assert len(src_chunks) == len(dst_chunks), f"chunk count mismatch {len(src_chunks)} vs {len(dst_chunks)}"
    it = iter(src_chunks)
    def repl(m):
        return m.group(1) + next(it) + m.group(3)
    out = FLIGHT_PUSH.sub(repl, dst)
    open(out_path, "w", encoding="utf-8").write(out)
    print("spliced:", out_path)

# A: migrated markup + pristine flight
splice("public/ab-v31all.html", "public/ab-ctrl.html", "public/ab-A.html")
# B: pristine markup + migrated flight
splice("public/ab-ctrl.html", "public/ab-v31all.html", "public/ab-B.html")
