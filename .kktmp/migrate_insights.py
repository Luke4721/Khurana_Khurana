#!/usr/bin/env python3
"""Insights migration: K&K real articles.

- insights.html: replace the 8 Momento cards with 8 K&K article cards (of 15).
- Each article page: rebuilt from the cloned article template with K&K title,
  category, read-time, cover image, and full body paragraphs.
- Old Momento article files are removed and replaced by 15 K&K-named pages.
  Article pages are made static (React flight stripped) since the body changes.
"""
import re, json, os, html as H

posts = json.load(open('.kktmp/posts_full.json'))

# Card markup builder for insights.html (matches clone's card anatomy loosely but
# uses clean classes already present in the compiled CSS)
def card(p):
    title = H.escape(p['title'], quote=False).replace('&', '&amp;')
    cover = p.get('cover_file') or '/images/insights/01-arbitration-of-insolvency-related-contract-claims.png'
    mins = p.get('mins') or '7'
    cat = H.escape(p.get('cat') or 'News & Updates', quote=False).replace('&', '&amp;')
    excerpt = H.escape((p.get('excerpt') or p.get('desc') or '')[:180], quote=False).replace('&', '&amp;')
    return f'''<div class="w-full"><a class="w-full flex flex-col gap-[45px] md:gap-[1.5vw]" href="/insights/{p["file"]}"><div class="relative w-full h-[451px] md:w-[21.312vw] md:h-[27.813vw] overflow-hidden"><img alt="{title}" loading="lazy" class="object-cover grayscale" style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0" src="{cover}"/></div><div class="w-full flex flex-col gap-[14px] md:gap-[0.8vw]"><p class="text-[12px] uppercase tracking-[0.2em] text-white/50">{cat} &#183; {mins} min read</p><h3 class="font-forum text-[20px] md:text-[1.458vw] leading-[1.25] text-white">{title}</h3><p class="text-[14px] text-white/60">{excerpt}</p><span class="text-[12px] uppercase tracking-[0.2em] text-white/70 mt-[6px]">See Details</span></div></a></div>'''

# ------------------------------------------------ article pages
TEMPLATE = open('.kktmp/orig-article.html', encoding='utf-8').read() if os.path.exists('.kktmp/orig-article.html') else open('public/insights/arbitration-clauses-and-the-drafting-momento.html', encoding='utf-8').read()

PARA_CLASS = 'text-[16px] md:leading-[1.25vw] text-white/67 mb-[16px] md:mb-[1.5vw] md:text-[0.938vw]'
H_CLASS = 'font-forum text-[20px] md:text-[1.458vw] text-white mt-[24px] mb-[12px]'

def strip_react(s):
    s = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<link[^>]*as="script"[^>]*/>', '', s)
    return s

def article_slug_file(p):
    slug = p['slug']
    f = slug
    f = f.replace('ó', 'o').replace('í', 'i')
    f = re.sub(r'[^a-z0-9-]', '-', f)
    f = re.sub(r'-{2,}', '-', f).strip('-')
    return f[:70].strip('-') + '.html'

built = []
for p in posts:
    f = article_slug_file(p)
    p['file'] = f
    cover = None
    cl = p.get('cover_local')
    if cl:
        base = os.path.basename(cl)
        base = re.sub(r'[^a-zA-Z0-9._-]', '-', base)
        if os.path.exists('public/images/insights/' + base):
            cover = '/images/insights/' + base
    p['cover_file'] = cover
    title = H.escape(p['title'], quote=False).replace('&', '&amp;')
    mins = p.get('mins') or '7'
    s = TEMPLATE
    s = re.sub(r'<title>.*?</title>', f'<title>{title} | Khurana &amp; Khurana</title>', s, count=1, flags=re.S)
    meta_txt = H.escape((p.get('desc') or p['title'])[:220], quote=True).replace('&','&amp;')
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda mm: mm.group(1) + meta_txt + mm.group(2), s, count=1)
    # hero h1
    s = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda mm: mm.group(1) + title + mm.group(2), s, count=1, flags=re.S)
    # category/read-time line (first small uppercase line after h1 if present)
    s = re.sub(r'(class="text-\[12px\][^"]*uppercase[^"]*"[^>]*>)[^<]*(<)',
               lambda mm: mm.group(1) + f'News &amp; Updates &#183; {mins} min read' + mm.group(2), s, count=1)
    # cover image: first insights image in body
    if cover:
        s = re.sub(r'srcSet="/_next/image\?url=%2Fimages%2Finsights%2F[^"]*"', f'srcSet="{cover}"', s, count=1)
        s = re.sub(r'src="/_next/image\?url=%2Fimages%2Finsights%2F[^"]*"', f'src="{cover}"', s, count=1)
    # body: replace the run of content paragraphs with K&K body
    body_html = ''
    for para in p.get('paras', []):
        t = H.escape(para.strip(), quote=False).replace('&', '&amp;')
        if not t:
            continue
        if t.isupper() or (len(t) < 60 and not t.endswith('.')):
            body_html += f'<h2 class="{H_CLASS}">{t}</h2>'
        else:
            body_html += f'<p class="{PARA_CLASS}">{t}</p>'
    if body_html:
        # find first body <p> and last </p> of the article container and replace range
        ps = list(re.finditer(r'<p class="text-\[16px\][^"]*"[^>]*>.*?</p>', s, re.S))
        if ps:
            s = s[:ps[0].start()] + body_html + s[ps[-1].end():]
    s = strip_react(s)
    open('public/insights/' + f, 'w', encoding='utf-8').write(s)
    built.append(f)

print('built articles:', len(built))

# remove old Momento article files
for f in os.listdir('public/insights'):
    if f.endswith('.html') and f not in built:
        os.remove('public/insights/' + f)
        print('removed', f)

# ------------------------------------------------ insights.html index
idx = open('public/insights.html', encoding='utf-8').read()
# replace the whole cards grid: find the grid div containing card links
gi = idx.find('grid grid-cols-1 md:grid-cols-[repeat(4,21.312vw)]')
gstart = idx.rfind('<div', 0, gi)
gend = idx.find('See Details')
# advance to the end of the last card's closing tags
gend = idx.find('</div></a></div>', gend)
gend = idx.find('</div>', gend + len('</div></a></div>')) + len('</div>')
new_cards = ''.join(card(p) for p in posts[:8])
idx = idx[:gstart] + f'<div class="grid grid-cols-1 md:grid-cols-[repeat(4,21.312vw)] gap-y-[70px] md:gap-y-[8vw] md:justify-between">{new_cards}</div>' + idx[gend:]
idx = strip_react(idx)
open('public/insights.html', 'w', encoding='utf-8').write(idx)
print('index rebuilt')
