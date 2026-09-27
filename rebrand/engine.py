#!/usr/bin/env python3
"""
Hydration-safe rebrand engine.

RULES:
- Every change goes through `apply_pairs` which performs ONE combined pass over the
  raw HTML/JS text, replacing in BOTH the plain (markup) and JSON-escaped (flight
  data) forms, so React hydration always sees matching strings.
- Structure, class names, tags, animation hooks are NEVER touched — only string leaves.
- After writing, `validate_file` parses every embedded RSC flight string as JSON;
  any corruption is caught at build time, never in the browser.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"

# ---------- escape variants for a literal string ----------

def esc_variants(s: str) -> list[str]:
    """All JSON/string-escape forms the same literal can take in flight data / JS."""
    variants = {
        s,                                   # plain markup form
        s.replace("/", "\\/"),               # escaped solidus (RSC JSON style)
        s.replace("/", "\\u002F"),           # unicode escape
        s.replace('"', '\\"'),               # escaped quotes (attr inside JSON string)
        s.replace("/", "\\/").replace('"', '\\"'),
        s.replace("/", "\\u002F").replace('"', '\\"'),
        s.replace("'", "\\'"),               # JS single-quote form
    }
    return [v for v in variants if v]

# ---------- flight validation ----------

FLIGHT_RE = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')

def flight_strings(html: str):
    """Yield the decoded flight chunks embedded in the page."""
    for m in FLIGHT_RE.finditer(html):
        raw = m.group(1)
        try:
            yield json.loads(f'"{raw}"')
        except Exception:
            yield None  # signals corruption

def validate_html(path: Path) -> tuple[bool, str]:
    txt = path.read_text(encoding="utf-8")
    bad = 0
    for s in flight_strings(txt):
        if s is None:
            bad += 1
    if bad:
        return False, f"{bad} corrupt flight chunk(s)"
    return True, ""

# ---------- the one and only mutation entry point ----------

def apply_pairs(text: str, pairs: list[tuple[str, str]]) -> tuple[str, int]:
    """Replace old->new in plain AND escaped forms. One combined conceptual pass."""
    count = 0
    for old, new in pairs:
        if old == new:
            continue
        for ev_old, ev_new in zip(esc_variants(old), esc_variants(new)):
            if ev_old in text:
                count += text.count(ev_old)
                text = text.replace(ev_old, ev_new)
    return text, count

def process_file(path: Path, pairs: list[tuple[str, str]]) -> int:
    txt = path.read_text(encoding="utf-8")
    new, n = apply_pairs(txt, pairs)
    if n == 0:
        return 0
    path.write_text(new, encoding="utf-8")
    if path.suffix == ".html":
        ok, msg = validate_html(path)
        if not ok:
            path.write_text(txt, encoding="utf-8")   # roll back
            print(f"  !! VALIDATION FAILED {path.name}: {msg} (rolled back)", file=sys.stderr)
            return -1
    return n

def process_glob(patterns: list[str], pairs: list[tuple[str, str]], label: str) -> int:
    total = 0
    files: list[Path] = []
    for pat in patterns:
        p = (PUB / pat) if not pat.startswith("/") else Path(pat)
        files += sorted(p.glob("*")) if "*" in str(p) or p.is_dir() else [p]
    seen = set()
    for f in files:
        if f in seen or not f.is_file() or f.suffix not in {".html", ".js", ".css", ".svg", ".xml"}:
            continue
        seen.add(f)
        n = process_file(f, pairs)
        if n > 0:
            total += n
    print(f"[{label}] replacements: {total} across {len(seen)} candidate files")
    return total

if __name__ == "__main__":
    # smoke test: engine loads, flight validation works on the real pages
    ok = True
    for f in [PUB / "index.html", PUB / "team.html"]:
        good, msg = validate_html(f)
        print(f.name, "flight-ok" if good else f"BROKEN: {msg}")
        ok = ok and good
    sys.exit(0 if ok else 1)
