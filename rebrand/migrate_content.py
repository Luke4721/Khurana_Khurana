#!/usr/bin/env python3
"""Content migration: K&K text + team data through engine31 (markup+flight synced).
Uses ONLY data scraped earlier (.kktmp). Structure untouched."""
import sys, re, json, shutil
from pathlib import Path
sys.path.insert(0, "rebrand")
from engine31 import process_file_v31, apply_pairs_v31

PUB = Path("public")
bios = json.load(open(".kktmp/bios.json"))          # 24 members, seniority order
pages = json.load(open(".kktmp/pages.json"))        # 29 KK practice/article pages
posts = json.load(open(".kktmp/posts_full.json"))   # 15 full articles

# ---------------------------------------------------------------- team
# fresh roster names (from parsed fresh_cards.json) mapped to KK members in order
fresh = json.load(open(".kktmp/fresh_cards.json"))
kk_names = [m["name"] for m in bios]
fresh_names = [c["name"] for c in fresh]

def unescape(s):
    return s.replace("&amp;", "&")

# mapping: match KK member i -> fresh card i (both seniority-ordered, 24 kept)
# fresh card names are unique enough for exact replacement
team_pairs = []
n = min(len(kk_names), len(fresh_names))
for i in range(n):
    old = unescape(fresh_names[i])
    new = unescape(kk_names[i])
    if old != new:
        team_pairs.append((old, new))
        # role line: fresh roles are office labels; replace with KK roles
        old_role = unescape(fresh[i]["role"])
        new_role = unescape(bios[i]["role"])
        if (old_role, new_role) not in team_pairs:
            team_pairs.append((old_role, new_role))
        # photo: copy KK photo to the fresh card's image path
        img_path = fresh[i]["image"]                     # /uploads/images/<hash>.jpg
        dst = PUB / img_path.lstrip("/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        src = Path(".kktmp/photos") / bios[i]["img"]
        if src.exists():
            shutil.copy(src, dst)

# bio pages: for each kept fresh profile slot, its <title> + og/meta carry the old
# name; replace across pages via exact old->new pairs (names are unique)
print(f"team pairs: {len(team_pairs)}")

# ---------------------------------------------------------------- apply
files = sorted(PUB.rglob("*.html"))
total = 0
for f in files:
    nh = process_file_v31(f, team_pairs)
    if nh > 0:
        total += nh
print(f"content replacements: {total} across {len(files)} pages")
