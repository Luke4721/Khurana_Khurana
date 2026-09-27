#!/usr/bin/env python3
"""Engine v2: flight-data surgery with automatic T-row length recomputation."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine import flight_strings, validate_html, esc_variants, PUB

FLIGHT_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')


def _fix_t_lengths(d: str) -> str:
    """Recompute every T-row hex length to match its (possibly edited) content.

    Rows nested inside an already-consumed row's content are skipped —
    their region was emitted verbatim with the enclosing row."""
    out = []
    pos = 0
    for m in re.finditer(r'([0-9a-f]+):T([0-9a-f]+),', d):
        if m.start() < pos:
            continue                              # inside a previous row's content
        ln = int(m.group(2), 16)
        content = d[m.end(): m.end() + ln]        # content is exactly ln chars (decoded)
        out.append(d[pos:m.start()])
        out.append(f"{m.group(1)}:T{len(content):x},")
        out.append(content)
        pos = m.end() + ln
    out.append(d[pos:])
    return "".join(out)


def _remove_named_objects(d: str, names: list[str]) -> tuple[str, int]:
    """Balanced-remove JSON objects like {"name":"X",...} from decoded flight text."""
    removed = 0
    for name in names:
        key = f'{{"name":"{name}"'
        while True:
            i = d.find(key)
            if i < 0:
                break
            # walk to matching close brace
            depth = 0; j = i; in_str = False; esc = False
            while j < len(d):
                c = d[j]
                if in_str:
                    if esc: esc = False
                    elif c == '\\': esc = True
                    elif c == '"': in_str = False
                else:
                    if c == '"': in_str = True
                    elif c == '{': depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            j += 1
                            break
                j += 1
            # swallow a trailing comma if present
            if j < len(d) and d[j] == ',':
                j += 1
            d = d[:i] + d[j:]
            removed += 1
    return d, removed


def apply_pairs_decoded(d: str, pairs) -> tuple[str, int]:
    """Plain replace in decoded space (no escape variants needed)."""
    n = 0
    for old, new in pairs:
        if old != new and old in d:
            n += d.count(old)
            d = d.replace(old, new)
    return d, n


def segment_rewrite(joined: str, pairs, remove_card_names=None) -> tuple[str, int, int]:
    """Desync-proof rewrite: apply edits per segment (row content bounded by ORIGINAL
    lengths, or gaps with no length prefixes). Lengths recomputed per row."""
    out = []
    pos = 0
    hits = 0
    removed = 0
    for m in re.finditer(r'([0-9a-f]+):T([0-9a-f]+),', joined):
        if m.start() < pos:
            continue                    # nested row: already consumed
        ln = int(m.group(2), 16)
        cstart = m.end()
        cend = cstart + ln
        out.append(apply_pairs_decoded(joined[pos:m.start()], pairs)[0])
        content = joined[cstart:cend]
        if remove_card_names:
            content, rm = _remove_named_objects(content, remove_card_names)
            removed += rm
        content, h = apply_pairs_decoded(content, pairs)
        hits += h
        out.append(f"{m.group(1)}:T{len(content):x},")
        out.append(content)
        pos = cend
    out.append(apply_pairs_decoded(joined[pos:], pairs)[0])
    return "".join(out), hits, removed


def rewrite_flight(html: str, pairs, remove_card_names=None) -> tuple[str, int, int]:
    """Rewrite the page's flight stream as ONE joined text (T-rows may span chunks).

    The concatenated [1] chunks are edited, T-lengths recomputed, then re-emitted:
    the first chunk carries the whole stream, subsequent chunks become empty strings
    (no-op appends for React, which only cares about order, not boundaries).

    Returns (new_html, pair_hits, removed_objects)."""
    matches = list(FLIGHT_RE.finditer(html))
    if not matches:
        return html, 0, 0
    parts = []
    for m in matches:
        try:
            parts.append(json.loads(f'"{m.group(1)}"'))
        except Exception:
            return html, 0, 0          # unexpected encoding: never risk corruption
    joined = "".join(parts)
    fixed, hits, removed = segment_rewrite(joined, pairs, remove_card_names)
    if hits == 0 and removed == 0:
        return html, 0, 0
    new_raw = json.dumps(fixed, ensure_ascii=False)[1:-1]
    # script-safety: never emit a literal </script inside a JS string
    new_raw = re.sub(r'</(script)', r'<\\/\\1', new_raw, flags=re.I)
    out = []
    pos = 0
    for idx, m in enumerate(matches):
        out.append(html[pos:m.start(1)])
        out.append(new_raw if idx == 0 else "")
        pos = m.end(1)
    out.append(html[pos:])
    return "".join(out), hits + removed, removed


def process_file_flight(path: Path, pairs, remove_card_names=None) -> int:
    txt = path.read_text(encoding="utf-8")
    new, hits, removed = rewrite_flight(txt, pairs, remove_card_names)
    if hits == 0 and removed == 0:
        return 0
    path.write_text(new, encoding="utf-8")
    ok, msg = validate_html(path)
    if not ok:
        path.write_text(txt, encoding="utf-8")
        print(f"  !! FLIGHT VALIDATION FAILED {path.name}: {msg} (rolled back)", file=sys.stderr)
        return -1
    return hits + removed


if __name__ == "__main__":
    # smoke: fix_t_lengths must be identity on pristine pages
    for f in [PUB / "team.html", PUB / "index.html", PUB / "team/abdallah-al-nassiry.html"]:
        txt = f.read_text(encoding="utf-8")
        for m in FLIGHT_RE.finditer(txt):
            decoded = json.loads(f'"{m.group(1)}"')
            fixed = _fix_t_lengths(decoded)
            status = "identity" if fixed == decoded else "CHANGED"
            if status != "identity":
                print(f.name, status)
                i = next((k for k in range(min(len(fixed), len(decoded))) if fixed[k] != decoded[k]), 0)
                print("  diff at", i, repr(decoded[i-30:i+30]), "VS", repr(fixed[i-30:i+30]))
                break
        else:
            print(f.name, "all chunks identity")
    print("ENGINE2-OK")
