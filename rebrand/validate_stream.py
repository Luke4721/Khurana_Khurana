#!/usr/bin/env python3
"""Simulate React's flight parser: rows are self-delimiting JSON or length-prefixed T text.
Reports the first misalignment. Usage: python3 rebrand/validate_stream.py public/ab-h7.html"""
import sys, json, re

FLIGHT_PUSH = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')

def stream_of(path):
    t = open(path, encoding="utf-8").read()
    return "".join(json.loads(f'"{c}"') for c in FLIGHT_PUSH.findall(t))

def validate(stream):
    i = 0
    n = len(stream)
    rows = 0
    while i < n:
        # row: id (hex-ish) ':' type-char ...  (or an inline continuation: ':HL[...')
        m = re.match(r'([0-9a-f]+):', stream[i:i+12])
        if not m:
            if stream[i:i+1] == ':':
                # inline payload row: read till newline
                j = stream.find('\n', i)
                i = n if j < 0 else j + 1
                rows += 1
                continue
            return f"row {rows} @ {i}: expected row id, got {stream[i:i+40]!r}"
        rid = m.group(1)
        i += m.end()
        tchar = stream[i]
        i += 1
        if tchar == 'T':
            lm = re.match(r'([0-9a-f]+),', stream[i:i+12])
            if not lm:
                return f"row {rid} @ {i}: expected T length, got {stream[i:i+40]!r}"
            ln = int(lm.group(1), 16)
            i += lm.end() + ln          # skip content by declared length
            rows += 1
            continue
        if tchar == '"' and stream[i:i+1] == '$':
            # $-prefixed server-reference string row: read till unescaped closing quote
            j = i
            while j < n:
                if stream[j] == '\\':
                    j += 2
                    continue
                if stream[j] == '"':
                    break
                j += 1
            i = j + 1
            if i < n and stream[i] == '\n':
                i += 1
            rows += 1
            continue
        if tchar in '"[{0123456789tfn-':   # JSON value rows
            dec = json.JSONDecoder()
            try:
                _, end = dec.raw_decode(stream, i)
            except Exception as e:
                return f"row {rid} @ {i}: JSON parse error {e} :: {stream[i:i+60]!r}"
            i = end
            if i < n and stream[i] == '\n':
                i += 1
            rows += 1
            continue
        if tchar in 'ISWDLXECQC':  # other row types with payloads till newline (I = module)
            j = stream.find('\n', i)
            i = n if j < 0 else j + 1
            rows += 1
            continue
        return f"row {rid} @ {i}: unknown type {tchar!r} :: {stream[i:i+60]!r}"
    return f"OK ({rows} rows)"

if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(path, "->", validate(stream_of(path)))
