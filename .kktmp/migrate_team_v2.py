#!/usr/bin/env python3
"""Team migration v2 — safer: surgical edits only, no broad regex deletions.

For each of the 24 K&K members, start from the PRISTINE template profile,
apply:
  1. <title>, meta description
  2. h1 name, role <p>
  3. bio <p> run inside the bio container (exact class match)
  4. hero photo srcSet/src (first uploads/images occurrence)
  5. grid swap: replace ONLY the <ul ...>...</ul> block that contains
     aria-label="View  member cards, with a freshly built <ul> of 24 cards.
Everything else stays byte-identical to the template, so hydration stays
consistent and no sections are lost.
"""
import re, json, os, glob, html as H

bios = json.load(open('.kktmp/bios.json'))
TEMPLATE = open('.kktmp/orig-melih.html', encoding='utf-8').read()

BIO_CLASS = 'text-[16px] md:text-[max(14px,1.042vw)] leading-[26px] md:leading-[max(22px,1.667vw)] mb-[12px] md:mb-[1vw]'

def photo_path(m):
    name = m['slug'].replace('-', '_')
    for ext in ('png', 'jpg'):
        p = f'images/teams/{name}.{ext}'
        if os.path.exists('public/' + p):
            return '/' + p
    return None

def bio_paras(m):
    raw = m.get('bio', '')
    t = re.sub(r'^[^A-Za-z]*', '', raw)
    t = re.sub(r'^' + re.escape(m['name']) + r'\s*' + re.escape(m['role']) + r'?', '', t)
    t = re.sub(r'OFFICE\s+\S[^A-Z]*PRACTICE AREA\s+[^A-Z]*', '', t, flags=re.I)
    paras = [p.strip() for p in re.split(r'(?<=[.!?])\s+', t) if len(p.strip()) > 60]
    return paras[:8]

def esc(s):
    return H.escape(s, quote=False).replace('&', '&amp;')

def card_li(m):
    ph = photo_path(m)
    name, role = esc(m['name']), esc(m['role'])
    img = (f'<img alt="{name} — {role}" loading="lazy" decoding="async" data-nimg="fill" '
           f'class="object-cover object-[center_10%]" '
           f'style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0;color:transparent" '
           f'src="/_next/image?url={H.escape(ph, quote=True)}&amp;w=640&amp;q=75"/>') if ph else '<div></div>'
    return (f'<li><button type="button" aria-label="View {name} details" aria-haspopup="dialog" '
            f'class="flex flex-col items-center text-center w-full cursor-pointer group/card">'
            f'<div class="relative aspect-[4/5] overflow-hidden w-full">{img}</div>'
            f'<p class="mt-[10px] font-forum uppercase text-white/90 text-[13px] tracking-[0.08em]">{name}</p>'
            f'<p class="text-[12px] text-white/50">{role}</p></button></li>')

GRID_UL = '<ul class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-[16px] md:gap-[1.2vw] w-full">' + \
          ''.join(card_li(m) for m in bios) + '</ul>'

def swap_grid(s):
    """Replace the member-grid <ul> (the one whose first card says 'View ... details')."""
    # find '<ul' ... '</ul>' regions; pick the one containing 'aria-label="View'
    pos = 0
    while True:
        ui = s.find('<ul', pos)
        if ui < 0:
            return s, False
        ue = s.find('</ul>', ui)
        if ue < 0:
            return s, False
        block = s[ui:ue + 5]
        if 'aria-label="View' in block:
            return s[:ui] + GRID_UL + s[ue + 5:], True
        pos = ue + 5

built = []
for m in bios:
    s = TEMPLATE
    name, role = m['name'], m['role']
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(name)} | Khurana &amp; Khurana</title>', s, count=1, flags=re.S)
    meta_txt = H.escape((m.get('bio') or f'{name} — {role} at Khurana & Khurana.')[:220], quote=True).replace('&','&amp;')
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda mm: mm.group(1) + meta_txt + mm.group(2), s, count=1)
    s = re.sub(r'(<h1 id="team-member-title"[^>]*>).*?(</h1>)', lambda mm: mm.group(1) + esc(name) + mm.group(2), s, count=1, flags=re.S)
    s = re.sub(r'(<p class=" text-\[16px\] md:text-\[max\(14px,1\.25vw\)\][^>]*>).*?(</p>)',
               lambda mm: mm.group(1) + esc(role) + mm.group(2), s, count=1, flags=re.S)
    paras = bio_paras(m)
    if paras:
        new_paras = ''.join(f'<p class="{BIO_CLASS}">{esc(p)}</p>' for p in paras)
        marker = 'text-white/50 max-w-[600px] md:max-w-[43vw]">'
        i = s.find(marker)
        if i >= 0:
            start = i + len(marker)
            # find the matching close of this div: the '</div>' that precedes the email/LinkedIn buttons
            end = s.find('<div class="mt-[24px]', start)
            if end < 0:
                end = s.find('</div>', start)
            s = s[:start] + new_paras + s[end:]
    ph = photo_path(m)
    if ph:
        enc = H.escape(ph, quote=True)
        s = re.sub(r'srcSet="/_next/image\?url=%2Fuploads%2Fimages%2F[^"]*"', f'srcSet="/_next/image?url={enc}&amp;w=1080&amp;q=75"', s, count=1)
        s = re.sub(r'src="/_next/image\?url=%2Fuploads%2Fimages%2F[^"]*"', f'src="/_next/image?url={enc}&amp;w=1080&amp;q=75"', s, count=1)
    s, ok = swap_grid(s)
    if not ok:
        print('WARN grid not found for', m['slug'])
    p = f'public/team/{m["slug"]}.html'
    open(p, 'w', encoding='utf-8').write(s)
    built.append(m['slug'])

print('rebuilt profiles:', len(built))

# team.html index: same grid swap
ti = open('public/team.html', encoding='utf-8').read()
ti, ok = swap_grid(ti)
open('public/team.html', 'w', encoding='utf-8').write(ti)
print('index grid swapped:', ok)
