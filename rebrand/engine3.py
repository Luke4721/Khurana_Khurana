#!/usr/bin/env python3
"""Engine v3: unified per-page pass.

- markup regions: raw replacement with escape variants (plain, \\/, \\u002F, quote-escaped)
- flight regions: joined decode -> replace -> T-length recompute -> re-encode
- every write is followed by flight validation; corruption rolls back the file.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import esc_variants, validate_html
from engine2 import FLIGHT_RE, segment_rewrite


def apply_pairs_v3(html: str, pairs, remove_card_names=None):
    """Single pass: flight chunks via joined-stream surgery, markup via variant replace.

    Returns (new_html, markup_hits, flight_hits, removed).
    """
    matches = list(FLIGHT_RE.finditer(html))
    flight_hits = 0
    removed = 0
    new_raw = None
    first_start = None

    if matches:
        parts = []
        for m in matches:
            try:
                parts.append(json.loads(f'"{m.group(1)}"'))
            except Exception:
                parts = None
                break
        if parts is None:
            # can't decode -> treat flight as untouched, but do NOT touch markup strings
            # that also appear in flight (rare); safest is to abort the page.
            raise RuntimeError(f"flight decode failure on page")

        joined = "".join(parts)
        j2, fhits, removed = segment_rewrite(joined, pairs, remove_card_names)
        if fhits or removed:
            new_raw = json.dumps(j2, ensure_ascii=False)[1:-1]
            new_raw = re.sub(r'</(script)', r'<\\1', new_raw, flags=re.I)
            first_start = matches[0].start(1)
            flight_hits = fhits + removed

    # markup pass on the ORIGINAL html, skipping regions that belong to flight chunks
    skip = [(m.start(), m.end()) for m in matches]
    buf = []
    pos = 0
    markup_hits = 0

    def inside_flight(a, b):
        return any(a < e and b > s for s, e in skip)

    for old, new in pairs:
        if old == new:
            continue
        for v_old, v_new in zip(esc_variants(old), esc_variants(new)):
            start = 0
            while True:
                i = buf_find(html, v_old, start) if not buf else None
                # operate on the mutable buffer instead
                break
        break  # placeholder: replaced below with buffer-based logic
    # --- buffer-based variant replace ---
    work = html
    for old, new in pairs:
        if old == new:
            continue
        for v_old, v_new in zip(esc_variants(old), esc_variants(new)):
            res = _replace_outside(work, v_old, v_new, skip)
            work, n = res
            markup_hits += n

    if new_raw is not None:
        # splice new flight text into the worked markup
        # recompute offsets: markup replacement can shift offsets, so apply flight
        # splice FIRST on pristine offsets is unsound; instead re-find the first chunk
        # by its exact old raw text
        m0 = matches[0]
        old_raw = m0.group(1)
        idx = work.find(old_raw)
        if idx < 0:
            # the markup pass altered the chunk raw text (shouldn't happen: skipped)
            # fall back: apply to html then re-run markup skipping chunk regions
            work = html.replace(old_raw, new_raw, 1)
            for i in range(1, len(matches)):
                work = work.replace(matches[i].group(1), "", 1)
        else:
            work = work[:idx] + new_raw + work[idx + len(old_raw):]
            # blank out remaining chunks
            for m in matches[1:]:
                raw_i = m.group(1)
                j = work.find(raw_i)
                if j >= 0:
                    work = work[:j] + "" + work[j + len(raw_i):]

    return work, markup_hits, flight_hits, removed


def _decoded_replace(d: str, pairs):
    n = 0
    for old, new in pairs:
        if old != new and old in d:
            n += d.count(old)
            d = d.replace(old, new)
    return d, n


def buf_find(hay, needle, start):
    return hay.find(needle, start)


def _replace_outside(text: str, old: str, new: str, skip) -> tuple[str, int]:
    """Replace all occurrences of `old` that are NOT inside any skip region."""
    if not old or old not in text:
        return text, 0
    out = []
    pos = 0
    n = 0
    while True:
        i = text.find(old, pos)
        if i < 0:
            break
        j = i + len(old)
        if any(i < e and j > s for s, e in skip):
            out.append(text[pos:j])
            pos = j
            continue
        out.append(text[pos:i])
        out.append(new)
        pos = j
        n += 1
    out.append(text[pos:])
    return "".join(out), n


def process_file_v3(path: Path, pairs, remove_card_names=None) -> int:
    txt = path.read_text(encoding="utf-8")
    try:
        new, mh, fh, rm = apply_pairs_v3(txt, pairs, remove_card_names)
    except RuntimeError as e:
        print(f"  !! {path.name}: {e}", file=sys.stderr)
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
    # invariant test: v3 with empty pairs must leave every page byte-identical
    import hashlib
    changed = 0
    files = sorted(Path("public").rglob("*.html"))
    for f in files:
        txt = f.read_text(encoding="utf-8")
        new, *_ = apply_pairs_v3(txt, [], None)
        if new != txt:
            changed += 1
            print("BYTE-DIFF:", f)
            if changed > 3:
                break
    print(f"invariant test: {len(files)} files, byte-diffs: {changed}")
    assert changed == 0, "v3 must be byte-identical with no pairs"
    print("ENGINE3-OK")
