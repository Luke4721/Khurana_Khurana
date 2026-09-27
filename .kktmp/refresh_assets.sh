#!/bin/bash
# Phase A2: pristine chunks + refresh contaminated media (teams/insights/header/favicons)
set -u
cd "$(dirname "$0")/.."
BASE="https://momentolegal.com"
mkdir -p public/_next/static/chunks public/images/teams public/images/insights

# 1) all /_next/static paths referenced anywhere in pristine HTML
grep -rhoE '/_next/static/[A-Za-z0-9/._~-]+' public --include='*.html' | sed 's/\\u002F/\//g' | sort -u > .kktmp/assets1.txt

fetcha() {
  local p="$1"
  local out="public$p"
  mkdir -p "$(dirname "$out")"
  if [ ! -s "$out" ]; then
    if ! curl -sfL --retry 3 --max-time 60 -o "$out" "https://momentolegal.com$p"; then echo "ASSETFAIL $p"; rm -f "$out"; fi
  fi
}
export -f fetcha
xargs -P 8 -I{} bash -c 'fetcha "$@"' _ {} < .kktmp/assets1.txt
echo "assets round1 done: $(wc -l < .kktmp/assets1.txt) refs"

# 2) closure round: refs that appear INSIDE downloaded JS/CSS (url paths) — download if missing
grep -rhoE '/_next/static/[A-Za-z0-9/._~-]+\.(js|css|woff2?|png|jpg|jpeg|svg|webp)' public/_next 2>/dev/null | sort -u >> .kktmp/assets1.txt
sort -u .kktmp/assets1.txt -o .kktmp/assets1.txt
xargs -P 8 -I{} bash -c 'fetcha "$@"' _ {} < .kktmp/assets1.txt
echo "closure done"

# 3) refresh contaminated media folders + favicons (mirror live tree exactly)
refresh_dir() {
  local d="$1"
  curl -sfL --max-time 60 "https://momentolegal.com/$d/" -o .kktmp/dirlist.tmp 2>/dev/null || true
  # autoindex may be disabled; instead re-fetch known stale names by listing local files
}
# teams: local file names are the live site's names (we mirrored them originally) — re-download each
for f in public/images/teams/*; do
  n="$(basename "$f")"
  curl -sfL --retry 2 --max-time 60 -o "$f" "https://momentolegal.com/images/teams/$n" || echo "TEAMFAIL $n"
done
for f in public/images/insights/*; do
  n="$(basename "$f")"
  curl -sfL --retry 2 --max-time 60 -o "$f" "https://momentolegal.com/images/insights/$n" || echo "INSFAIL $n"
done
for n in header-logo.png header-logo@2x.png logo.png icon.png favicon.png apple-icon.png favicon.ico; do
  [ -f "public/images/$n" ] || [ -f "public/$n" ] || continue
  if [ -f "public/images/$n" ]; then curl -sfL --retry 2 --max-time 60 -o "public/images/$n" "https://momentolegal.com/images/$n" || echo "HDRFAIL $n"; fi
  if [ -f "public/$n" ]; then curl -sfL --retry 2 --max-time 60 -o "public/$n" "https://momentolegal.com/$n" || echo "ICONFAIL $n"; fi
done
curl -sfL --retry 2 -o public/icon.png "https://momentolegal.com/icon.png" || echo "ICONFAIL icon.png"
curl -sfL --retry 2 -o public/apple-icon.png "https://momentolegal.com/apple-icon.png" || echo "ICONFAIL apple-icon.png"

# 4) strip our workaround script from all HTML (pristine again)
grep -rl 'kk-reveal.js' public --include='*.html' | while read -r f; do
  python3 - "$f" <<'EOF'
import re,sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
s=re.sub(r'<script[^>]*src="/kk-reveal\.js"[^>]*></script>','',s)
open(p,'w',encoding='utf-8').write(s)
EOF
done
rm -f public/kk-reveal.js
echo "=== final chunk count: $(ls public/_next/static/chunks/ | wc -l)"
echo "=== html: $(find public -name '*.html' | wc -l)"