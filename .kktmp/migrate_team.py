#!/usr/bin/env python3
"""Team migration: 39 Momento profiles -> 24 real K&K practitioner profiles.

Approach: reuse the existing profile-page template (dr-melih-can-korkmaz.html)
as the base for each K&K member. Swap: title, meta, h1 name, role line,
bio paragraphs, photo srcset, ld+json, and the member-grid card data
(all profile pages carry the full 41-member grid; rebuilt to 24 cards).
Delete surplus pages. Rebuild team.html index grid the same way.
"""
import re, json, os, glob, html as H

bios = json.load(open('.kktmp/bios.json'))

TEMPLATE = 'public/team/dr-melih-can-korkmaz.html'
base = open(TEMPLATE, encoding='utf-8').read()

def slug_of(m):
    return m['slug']

def photo_path(m):
    name = m['slug'].replace('-', '_')
    for ext in ('png', 'jpg'):
        p = f'public/images/teams/{name}.{ext}'
        if os.path.exists(p):
            return f'/images/teams/{name}.{ext}'
    return None

def esc(s):
    return H.escape(s, quote=False).replace('&', '&amp;')

def bio_paras(m):
    raw = m.get('bio', '')
    # bios.json bio begins with "Name Role OFFICE x PRACTICE AREA y" then text
    t = re.sub(r'^[^A-Za-z]*', '', raw)
    t = re.sub(r'^' + re.escape(m['name']) + r'\s*' + re.escape(m['role']) + r'?', '', t)
    t = re.sub(r'OFFICE\s+\S[^A-Z]*PRACTICE AREA\s+[^A-Z]*', '', t, flags=re.I)
    paras = [p.strip() for p in t.split('  ') if len(p.strip()) > 40]
    if not paras:
        paras = [p.strip() for p in re.split(r'(?<=[.!?])\s+', t) if len(p.strip()) > 40]
    return paras[:8]

BIO_CLASS = 'text-[16px] md:text-[max(14px,1.042vw)] leading-[26px] md:leading-[max(22px,1.667vw)] mb-[12px] md:mb-[1vw]'

def make_profile(m):
    s = base
    name = m['name']
    role = m['role']
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(name)} | Khurana &amp; Khurana</title>', s, count=1, flags=re.S)
    meta = (m.get('bio') or f'{name} — {role} at Khurana & Khurana.')[:230]
    s = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda mm: mm.group(1) + H.escape(meta, quote=True)[:230].replace('&','&amp;') + mm.group(2), s, count=1)
    # h1 + role
    s = re.sub(r'(<h1 id="team-member-title"[^>]*>).*?(</h1>)', lambda mm: mm.group(1) + esc(name) + mm.group(2), s, count=1, flags=re.S)
    s = re.sub(r'(<p class=" text-\[16px\] md:text-\[max\(14px,1\.25vw\)\][^>]*>).*?(</p>)',
               lambda mm: mm.group(1) + esc(role) + mm.group(2), s, count=1, flags=re.S)
    # bio paragraphs
    paras = bio_paras(m)
    new_paras = ''.join(f'<p class="{BIO_CLASS}">{esc(p)}</p>' for p in paras)
    # replace the run of bio <p>s inside the max-w-[600px] div
    run_re = re.compile(r'(mt-\[32px\] md:mt-\[3vw\] text-white/50 max-w-\[600px\] md:max-w-\[43vw\]">)(.*?)(</div>)', re.S)
    s = run_re.sub(lambda mm: mm.group(1) + new_paras + mm.group(3), s, count=1)
    # photo: main hero photo img (uploads/images/...) -> K&K photo
    ph = photo_path(m)
    if ph:
        s = re.sub(r'srcSet="/_next/image\?url=%2Fuploads%2Fimages%2F[^"]*"',
                   f'srcSet="{ph}"', s, count=1)
        s = re.sub(r'src="/_next/image\?url=%2Fuploads%2Fimages%2F[^"]*"',
                   f'src="{ph}"', s, count=1)
    # ld+json person
    s = re.sub(r'(\\"@type\\":\\"Person\\",\\"name\\":\\")[^"\\]*(\\")',
               lambda mm: mm.group(1) + name + mm.group(2), s, count=1)
    # aria-labels on cards stay grid-wide; fine.
    return s

# ------------------------------------------------ build 24 profile files
built = []
for m in bios:
    html_out = make_profile(m)
    p = f'public/team/{m["slug"]}.html'
    open(p, 'w', encoding='utf-8').write(html_out)
    built.append(m['slug'])
print('built profiles:', len(built))

# ------------------------------------------------ delete surplus profiles
existing = [os.path.basename(p)[:-5] for p in glob.glob('public/team/*.html')]
keep = set(built)
removed = 0
for slug in existing:
    if slug not in keep:
        os.remove(f'public/team/{slug}.html')
        removed += 1
print('removed surplus profiles:', removed)

# ------------------------------------------------ rebuild grid in team.html + profiles
def card(m):
    ph = photo_path(m)
    ph_url = f'/_next/image?url={H.escape(ph, quote=True)}&amp;w=640&amp;q=75' if ph else ''
    name, role = esc(m['name']), esc(m['role'])
    return (f'<button type="button" aria-label="View {name} details" aria-haspopup="dialog" '
            f'class="flex flex-col items-center text-center w-full cursor-pointer group/card">'
            f'<div class="relative aspect-[4/5] overflow-hidden w-full">'
            f'<img alt="{name} — {role}" loading="lazy" decoding="async" data-nimg="fill" '
            f'class="object-cover object-[center_10%] transition duration-[600ms] ease-out md:group-hover/card:grayscale-[0.4]! md:group-hover/card:scale-[1.06] md:grayscale-[0.4] md:scale-[1.06]" '
            f'style="position:absolute;height:100%;width:100%;left:0;top:0;right:0;bottom:0;color:transparent" src="{ph_url}"/></div>'
            f'<p class="mt-[10px] font-forum uppercase text-white/90 text-[13px] tracking-[0.08em]">{name}</p>'
            f'<p class="text-[12px] text-white/50">{role}</p></button>')

cards = ''.join(card(m) for m in bios)

for p in ['public/team.html'] + [f'public/team/{s}.html' for s in built]:
    s = open(p, encoding='utf-8').read()
    # replace each old card button (they start with aria-label="View ... details") with nothing, then inject all new cards before </ul> of members section
    s = re.sub(r'<button type="button" aria-label="View [^"]+" aria-haspopup="dialog".*?</button>', '', s, flags=re.S)
    s = s.replace('</ul></section>', '<li class="contents"></li></ul>'.join('') + '</ul></section>', 1)
    # inject cards inside the <ul>
    s = re.sub(r'(<ul[^>]*>)', lambda mm: mm.group(1) + ''.join(f'<li>{card(m)}</li>' for m in bios), s, count=1)
    open(p, 'w', encoding='utf-8').write(s)
print('grids rebuilt')
