#!/usr/bin/env python3
"""Team migration v3 — final approach.

React 19's flight payload must match SSR markup exactly; editing the member
grid makes hydration fail fatally on team pages. Solution: make team pages
fully static — all K&K content edits applied, then all React flight/bootstrap
scripts stripped. Result: clean, fast, purely-HTML team pages (CSS animations
intact since Tailwind CSS still loads; only JS-driven widgets like the clock
video loop are lost on these pages).
"""
import re, json, os, html as H

bios = json.load(open('.kktmp/bios.json'))
TEMPLATE = open('.kktmp/orig-melih.html', encoding='utf-8').read()

BIO_CLASS = 'text-[16px] md:text-[max(14px,1.042vw)] leading-[26px] md:leading-[max(22px,1.667vw)] mb-[12px] md:mb-[1vw]'

def photo_path(m):
    name = m['slug'].replace('-', '_')
    for ext in ('png', 'jpg'):
        if os.path.exists(f'public/images/teams/{name}.{ext}'):
            return f'/images/teams/{name}.{ext}'
    return None

def bio_paras(m):
    raw = m.get('bio', '')
    t = re.sub(r'^[^A-Za-z]*', '', raw)
    t = re.sub(r'^' + re.escape(m['name']) + r'\s*' + re.escape(m['role']) + r'?', '', t)
    t = re.sub(r'OFFICE\s+\S[^A-Z]*PRACTICE AREA\s+[^A-Z]*', '', t, flags=re.I)
    return [p.strip() for p in re.split(r'(?<=[.!?])\s+', t) if len(p.strip()) > 60][:8]

def esc(s):
    return H.escape(s, quote=False).replace('&', '&amp;')

def card_li(m):
    ph = photo_path(m)
    name, role = esc(m['name']), esc(m['role'])
    img = (f'<img alt="{name} — {role}" loading="lazy" class="object-cover object-[center_10%]" '
           f'style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0" '
           f'src="{ph}"/>') if ph else '<div></div>'
    return (f'<li><a href="/team/{m["slug"]}" aria-label="View {name} details" '
            f'class="flex flex-col items-center text-center w-full cursor-pointer group/card">'
            f'<div class="relative aspect-[4/5] overflow-hidden w-full">{img}</div>'
            f'<p class="mt-[10px] font-forum uppercase text-white/90 text-[13px] tracking-[0.08em]">{name}</p>'
            f'<p class="text-[12px] text-white/50">{role}</p></a></li>')

GRID_UL = ('<ul class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-[16px] md:gap-[1.2vw] w-full">'
           + ''.join(card_li(m) for m in bios) + '</ul>')

def swap_grid(s):
    pos = 0
    while True:
        ui = s.find('<ul', pos)
        if ui < 0:
            return s, False
        ue = s.find('</ul>', ui)
        if ue < 0:
            return s, False
        if 'aria-label="View' in s[ui:ue + 5]:
            return s[:ui] + GRID_UL + s[ue + 5:], True
        pos = ue + 5

def strip_react(s):
    s = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.S)
    s = re.sub(r'<link[^>]*as="script"[^>]*/>', '', s)
    return s

built = []
for m in bios:
    s = TEMPLATE
    name, role = m['name'], m['role']
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(name)} | Khurana &amp; Khurana</title>', s, count=1, flags=re.S)
    meta_txt = H.escape((m.get('bio') or f'{name} — {role} at Khurana & Khurana.')[:220], quote=True).replace('&', '&amp;')
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
            end = s.find('<div class="mt-[24px]', start)
            if end < 0:
                end = s.find('</div>', start)
            s = s[:start] + new_paras + s[end:]
    ph = photo_path(m)
    if ph:
        enc = H.escape(ph, quote=True)
        s = re.sub(r'srcSet="/_next/image\?url=%2Fuploads%2Fimages%2F[^"]*"', f'srcSet="{ph}"', s, count=1)
        s = re.sub(r'src="/_next/image\?url=%2Fuploads%2Fimages%2F[^"]*"', f'src="{ph}"', s, count=1)
    # hero photo alt
    s = re.sub(r'alt="Dr\. Melih Can Korkmaz — Founder"', f'alt="{esc(name)} — {esc(role)}"', s)
    # email link on profile: generic info@ (already rebranded globally)
    s, ok = swap_grid(s)
    s = strip_react(s)
    open(f'public/team/{m["slug"]}.html', 'w', encoding='utf-8').write(s)
    built.append(m['slug'])

print('static profiles:', len(built))

ti = open('public/team.html', encoding='utf-8').read()
ti, ok = swap_grid(ti)
ti = strip_react(ti)
open('public/team.html', 'w', encoding='utf-8').write(ti)
print('index static, grid swapped:', ok)
