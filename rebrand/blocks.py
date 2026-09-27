#!/usr/bin/env python3
"""Shared helpers: extract pristine text blocks, distribute KK copy into them."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from engine2 import FLIGHT_RE  # noqa: E402

BLOCK_MIN = 34  # ignore nav crumbs / buttons


def _static_blocks(html: str) -> list[str]:
    """Visible text of content tags in raw markup, excluding script/flight regions."""
    t = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
    blocks = []
    for m in re.finditer(r"<(h1|h2|h3|h4|p|figcaption|li|blockquote|a|span|button)\b[^>]*>(.*?)</\1>",
                         t, flags=re.S | re.I):
        tag, inner = m.group(1), m.group(2)
        if "<" in inner:  # container, not a leaf
            continue
        txt = re.sub(r"<[^>]+>", "", inner)
        txt = txt.replace("&amp;", "&").replace("&#x27;", "'").replace("&#x2F;", "/")
        txt = txt.replace("&quot;", '"').replace("&nbsp;", " ")
        txt = re.sub(r"\s+", " ", txt).strip()
        if len(txt) >= BLOCK_MIN and txt not in blocks:
            blocks.append(txt)
    return blocks


def _flight_blocks(html: str) -> list[str]:
    """Visible text blocks in the decoded flight stream."""
    joined = ""
    for m in FLIGHT_RE.finditer(html):
        try:
            import json
            joined += json.loads(f'"{m.group(1)}"')
        except Exception:
            pass
    joined = re.sub(r"[0-9a-f]+:T[0-9a-f]+,", "\n", joined)
    joined = joined.replace("\\n", "\n")
    blocks = []
    for line in joined.split("\n"):
        txt = line.strip()
        if len(txt) >= BLOCK_MIN and not re.search(r'[\{\}"\[\]]', txt) and txt not in blocks:
            blocks.append(txt)
    return blocks


def sentences(text: str) -> list[str]:
    """Split prose into sentences, keeping headings as their own units."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def pair_up(old_blocks: list[str], new_text: str) -> list[tuple[str, str]]:
    """Distribute new_text sentences across old blocks 1:1 (extras merged into last slot)."""
    olds = [b for b in old_blocks if not b.startswith(("©", "HOME", "ABOUT"))]
    if not olds:
        return []
    units = []
    for para in new_text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if len(para) < 80:            # heading-ish
            units.append(para)
        else:
            units.extend(sentences(para))
    pairs = []
    if len(units) <= len(olds):
        for i, o in enumerate(olds):
            pairs.append((o, units[i] if i < len(units) else units[-1]))
    else:
        per = len(units) // len(olds)
        extra = len(units) % len(olds)
        k = 0
        for i, o in enumerate(olds):
            take = per + (1 if i < extra else 0)
            pairs.append((o, " ".join(units[k:k + take])))
            k += take
    return pairs
