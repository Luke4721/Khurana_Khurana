#!/usr/bin/env python3
"""Engine v3.1: offset-drift-proof unified per-page pass.

Architecture:
- Split each page into alternating TEXT and FLIGHT-RAW segments ONCE (stable segmentation).
- Pairs applied to TEXT segments only (escape variants, per segment -> no drift).
- Pairs applied to the JOINED DECODED flight stream (segment_rewrite: length-aware).
- Reassembly: re-encoded stream goes into chunk 0; chunks 1..n become empty strings.

Byte-identity invariant: with no pairs (and no removals), output == input.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import esc_variants, validate_html
from engine2 import FLIGHT_RE, segment_rewrite

FLIGHT_PUSH = re.compile(r'(self\.__next_f\.push\(\[1,")((?:[^"\\]|\\.)*)("\]\))')


def _replace_in_text_segment(text: str, pairs) -> tuple[str, int]:
    n = 0
    for old, new in pairs:
        if old == new:
            continue
        for v_old, v_new in zip(esc_variants(old), esc_variants(new)):
            if v_old and v_old in text:
                n += text.count(v_old)
                text = text.replace(v_old, v_new)
    return text, n


def apply_pairs_v31(html: str, pairs, remove_card_names=None):
    """Returns (new_html, markup_hits, flight_hits, removed)."""
    segs = []            # list of (kind, payload)
    last = 0
    decoded_parts = []
    chunk_spans = []     # (seg_index, decoded_len) to map back later
    for m in FLIGHT_PUSH.finditer(html):
        if m.start() > last:
            segs.append(("text", html[last:m.start()]))
        try:
            dec = json.loads(f'"{m.group(2)}"')
        except Exception:
            raise RuntimeError("flight decode failure")
        segs.append(("flight", (m, dec)))
        chunk_spans.append((len(segs) - 1, len(dec)))
        decoded_parts.append(dec)
        last = m.end()
    if last < len(html):
        segs.append(("text", html[last:]))

    # edit text segments
    markup_hits = 0
    for i, (kind, payload) in enumerate(segs):
        if kind == "text":
            new, n = _replace_in_text_segment(payload, pairs)
            segs[i] = ("text", new)
            markup_hits += n

    # edit joined flight stream
    joined = "".join(decoded_parts)
    fixed, fhits, removed = segment_rewrite(joined, pairs, remove_card_names)
    flight_hits = fhits + removed

    if markup_hits == 0 and flight_hits == 0:
        return html, 0, 0, 0

    # distribute edited stream back: chunk 0 gets everything, rest get ""
    # NOTE: store DECODED stream in segs; encode ONCE at reassembly (no double-escape).
    if flight_hits or removed:
        fixed = re.sub(r'</(script)', r'<\\1', fixed, flags=re.I)
        first_done = False
        for i, (kind, payload) in enumerate(segs):
            if kind != "flight":
                continue
            if not first_done:
                segs[i] = ("flight", (payload[0], fixed))
                first_done = True
            else:
                segs[i] = ("flight", (payload[0], ""))
    else:
        # flight untouched: put back each chunk's (unedited) decoded text
        for i, (kind, payload) in enumerate(segs):
            if kind == "flight":
                segs[i] = ("flight", (payload[0], payload[1]))

    # reassemble
    out = []
    for kind, payload in segs:
        if kind == "text":
            out.append(payload)
        else:
            m, dec = payload
            out.append(m.group(1))
            out.append(json.dumps(dec, ensure_ascii=False)[1:-1])
            out.append(m.group(3))
    return "".join(out), markup_hits, flight_hits, removed


def process_file_v31(path: Path, pairs, remove_card_names=None) -> int:
    txt = path.read_text(encoding="utf-8")
    try:
        new, mh, fh, rm = apply_pairs_v31(txt, pairs, remove_card_names)
    except RuntimeError as e:
        print(f"  !! {path.name}: {e} (skipped, left pristine)", file=sys.stderr)
        return -1
    if mh == 0 and fh == 0:
        return 0
    path.write_text(new, encoding="utf-8")
    ok, msg = validate_html(path)
    if not ok:
        path.write_text(txt, encoding="utf-8")
        print(f"  !! VALIDATION FAILED {path.name}: {msg} (rolled back)", file=sys.stderr)
        return -1
    return mh + fh


if __name__ == "__main__":
    import hashlib
    changed = 0
    files = sorted(Path("public").rglob("*.html"))
    for f in files:
        txt = f.read_text(encoding="utf-8")
        try:
            new, *_ = apply_pairs_v31(txt, [], None)
        except RuntimeError:
            print("DECODE FAIL:", f); changed += 1; continue
        if new != txt:
            changed += 1
            print("BYTE-DIFF:", f)
    print(f"invariant: {len(files)} files, diffs: {changed}")
    assert changed == 0
    print("ENGINE31-OK")
