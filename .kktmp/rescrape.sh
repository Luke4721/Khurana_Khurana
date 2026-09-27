#!/bin/bash
# Phase A1: fresh pristine scrape of momentolegal.com into public/
set -u
cd "$(dirname "$0")/.."
BASE="https://momentolegal.com"
PUB=public
mkdir -p .kktmp

curl -sfL --retry 3 -o $PUB/sitemap.xml "$BASE/sitemap.xml" || { echo "SITEMAP FAIL"; exit 1; }
curl -sfL --retry 3 -o $PUB/robots.txt "$BASE/robots.txt"
curl -sfL --retry 3 -o $PUB/404.html "$BASE/404"

grep -oE '<loc>[^<]*</loc>' $PUB/sitemap.xml | sed -E 's#</?loc>##g' | grep -v 'momentolegal.com/tr' > .kktmp/urls.txt
echo "URLs to fetch: $(wc -l < .kktmp/urls.txt)"

fetch_page() {
  local u="$1" path out
  path="${u#https://momentolegal.com}"
  out="public$path.html"
  [ "$path" = "/" ] && out="public/index.html"
  mkdir -p "$(dirname "$out")"
  if ! curl -sfL --retry 3 --max-time 90 -o "$out" "$u"; then echo "PAGEFAIL $u"; fi
}
export -f fetch_page
xargs -P 6 -I{} bash -c 'fetch_page "$@"' _ {} < .kktmp/urls.txt

echo "=== html files now: $(find $PUB -name '*.html' | wc -l)"
echo "=== failures above (if any) ==="
