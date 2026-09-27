#!/bin/bash
# Phase A2b: reference-driven media sync — download every media path the pristine HTML references
set -u
cd "$(dirname "$0")/.."
BASE="https://momentolegal.com"

# collect paths from HTML: direct src/href/poster + _next/image encoded params
{
  grep -rhoE '(src|href|poster|content)="/(images|uploads|videos|assets|forms|fonts)/[^"]+"' public --include='*.html' | grep -oE '/(images|uploads|videos|assets|forms|fonts)/[^"]+'
  grep -rhoE 'url=%2F(images|uploads|videos|assets|forms|fonts)%2F[^"&]+' public --include='*.html' | sed 's/url=%2F/\//; s/%2F/\//g'
} | sed 's/[?"].*$//' | sort -u > .kktmp/media.txt
echo "media refs: $(wc -l < .kktmp/media.txt)"

fetchm() {
  local p="$1" out="public$p"
  mkdir -p "$(dirname "$out")"
  if [ ! -s "$out" ]; then
    curl -sfL --retry 3 --max-time 120 -o "$out" "https://momentolegal.com$p" || { echo "MEDIAFAIL $p"; rm -f "$out"; }
  fi
}
export -f fetchm
xargs -P 8 -I{} bash -c 'fetchm "$@"' _ {} < .kktmp/media.txt
echo "media sync done"

# force-refresh the two folders the old edits overwrote (kk files at original paths)
fails=0
while read -r p; do
  case "$p" in
    /images/teams/*|/images/insights/*|/images/header/*)
      curl -sfL --retry 2 --max-time 90 -o "public$p" "$BASE$p" || { echo "REFRESHFAIL $p"; fails=$((fails+1)); } ;;
  esac
done < .kktmp/media.txt
echo "forced refresh done ($fails failures)"
rm -f public/kk-reveal.js
grep -rl 'kk-reveal.js' public --include='*.html' 2>/dev/null | xargs -r sed -i 's#<script[^>]*src="/kk-reveal\.js"[^>]*></script>##g'
echo "=== media files on disk: $(find public/images public/uploads public/videos -type f 2>/dev/null | wc -l)"