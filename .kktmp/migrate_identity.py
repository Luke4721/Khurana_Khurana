#!/usr/bin/env python3
"""
Khurana & Khurana identity pass over the cloned site.
Replaces text/identity/markup in-place across all HTML pages:
- titles, meta descriptions
- header wordmark (Momento logo img -> typographic K&K wordmark)
- footer contact block, socials, copyright
- contact page office details
- team names/roles/bios + photos (index + 39 profile pages -> 24 K&K profiles)
- insight articles (8 -> 15 real K&K articles)
- hides Awwwards badge via injected CSS
"""
import re, json, glob, html as H, os, shutil

# ---------------------------------------------------------------- data
ROOT = 'public'
bios = json.load(open('.kktmp/bios.json'))
posts = json.load(open('.kktmp/posts_full.json'))

EMAIL_OLD, EMAIL_NEW = 'info@momentolegal.com', 'info@khuranaandkhurana.com'
PHONE_OLD_DISPLAY, PHONE_NEW_DISPLAY = '0212 890 80 55', '+91-(120) 3132513'
PHONE_OLD_TEL, PHONE_NEW_TEL = 'tel:02128908055', 'tel:+911203132513'
ADDR_OLD = 'ISTANBUL / TURKEY'

WORDMARK = (
    '<div class="flex flex-col items-start select-none" aria-label="Khurana &amp; Khurana">'
    '<span class="font-forum uppercase text-white leading-none tracking-[0.28em] '
    'text-[15px] md:text-[clamp(15px,1.25vw,22px)] whitespace-nowrap">Khurana &amp; Khurana</span>'
    '<span class="font-forum uppercase text-white/55 leading-none tracking-[0.24em] '
    'text-[7px] md:text-[clamp(6px,0.42vw,9px)] mt-[4px] whitespace-nowrap">'
    'Advocates &amp; IP Attorneys &#183; An ISO 9001:2022 Certified Firm</span></div>'
)

LOGO_IMG_RE = re.compile(
    r'<img[^>]*alt="brand logo"[^>]*>')

AWWWARDS_CSS = (
    '<style>a[aria-label="Awwwards Honors"],div[class*="awwwards"]'
    '{display:none!important}</style>')

def read(p):
    with open(p, encoding='utf-8') as f: return f.read()

def write(p, s):
    with open(p, 'w', encoding='utf-8') as f: f.write(s)

def replace_all_map(s, pairs):
    for a, b in pairs:
        s = s.replace(a, b)
    return s

IDENTITY_PAIRS = [
    # brand strings
    ('MOMENTO LEGAL', 'KHURANA & KHURANA'),
    ('Momento Legal', 'Khurana & Khurana'),
    ('momentolegal.com', 'khuranaandkhurana.com'),
    ('info@momentolegal.com', EMAIL_NEW),
    ('0212 890 80 55', PHONE_NEW_DISPLAY),
    ('tel:02128908055', PHONE_NEW_TEL),
    ('ISTANBUL / TURKEY', 'GREATER NOIDA / INDIA'),
    ('An independent legal and advisory platform providing strategic counsel to companies, investors, entrepreneurs, and private clients on high-stakes legal and commercial matters.',
     'A leading IP and Commercial law firm, rendering sage legal advice for pro-active enforcement — from idea inception to successful commercialization.'),
    ('Law, strategy, and timing. An independent legal and advisory platform offering integrated, strategic counsel to our clients at their most critical decisions.',
     'Founded in 2007, K&amp;K specializes in IP Prosecution, Litigation, and Commercialization, serving 3000+ corporates with expertise across 10 Indian offices.'),
    ('Copyright © 2026 Khurana &amp; Khurana.', '© 2007-2026 Khurana &amp; Khurana.'),
    ('Copyright © 2026 Khurana & Khurana.', '© 2007-2026 Khurana & Khurana.'),
    # socials
    ('href="https://www.instagram.com/momentolegal/"', 'href="https://www.instagram.com/khuranaandkhurana/"'),
    ('href="https://www.linkedin.com/company/momentolegal"', 'href="https://www.linkedin.com/company/khurana-&-khurana-advocates-and-ip-attorneys"'),
    # istcode credit -> K&K site credit
    ('Visit Istcode that is 360 Degree Digital Agency: https://www.istcode.com/', 'Khurana &amp; Khurana — Advocates and IP Attorneys'),
    ('https://www.istcode.com/', 'https://www.khuranaandkhurana.com/'),
]

pages = [p for p in glob.glob(f'{ROOT}/**/*.html', recursive=True)]

# ---------------------------------------------------------------- pass 1: identity on every page
for f in pages:
    s = read(f)
    orig = s
    s = replace_all_map(s, IDENTITY_PAIRS)
    # wordmark swap (every page has exactly one header logo img)
    s = LOGO_IMG_RE.sub(WORDMARK, s, count=1)
    # footer istcode img (if not already replaced) -> plain K&K mark text
    s = re.sub(r'<img[^>]*istcode-logo\.png[^>]*>',
               '<span class="font-forum uppercase text-white/70 tracking-[0.3em] text-[11px]">K&amp;K</span>', s)
    # hide awwwards badge
    if 'AwwwardsBadge' in s and 'awwwards-hide' not in s:
        s = s.replace('</head>', AWWWARDS_CSS.replace('awwwards-hide', 'awwwards-hide') + '</head>')
        s = s.replace(AWWWARDS_CSS + '</head>', '</head>')
        # inject once with marker
        s = s.replace('</head>', '<style id="kk-hide-awwwards">' + AWWWARDS_CSS[len('<style>'):-len('</style>')] + '</style></head>', 1)
    if s != orig:
        write(f, s)
print("identity pass done on", len(pages), "pages")

# ---------------------------------------------------------------- pass 2: titles & meta per page
TITLE_MAP = {
    'index.html': ("IP &amp; Commercial Law Firm | Khurana &amp; Khurana — India's Trusted Legal Partner",
                   "Khurana &amp; Khurana (K&amp;K), founded in 2007, is a leading IP and Commercial Law firm with over 330 professionals across 10 Indian offices, offering end-to-end IP Prosecution, Litigation, and Commercialization services."),
    'about.html': ("About Us | Khurana &amp; Khurana",
                   "Khurana &amp; Khurana is a distinguished full-service law firm with over 18 years of experience delivering precise, commercially viable, and client-centric legal services."),
    'culture.html': ("Pro Bono &amp; Culture | Khurana &amp; Khurana",
                     "How we work and what we value at Khurana &amp; Khurana."),
    'team.html': ("Our Team | Khurana &amp; Khurana",
                  "Meet the core practitioners of Khurana &amp; Khurana — patent attorneys, litigators, and commercial lawyers."),
    'expertise.html': ("Practice Areas | Khurana &amp; Khurana",
                       "Our areas of legal expertise across Intellectual Property, Corporate &amp; Commercial Law, Litigation, and Taxation."),
    'insights.html': ("Insights | Khurana &amp; Khurana",
                      "Articles and commentary on IP, IBC, competition, and commercial law developments by K&amp;K attorneys."),
    'contact.html': ("Contact Us | Khurana &amp; Khurana",
                     "Reach Khurana &amp; Khurana across 10 Indian offices. Email: info@khuranaandkhurana.com, Tel: +91-(120) 3132513."),
    'policies.html': ("Policies | Khurana &amp; Khurana",
                      "Policies of Khurana &amp; Khurana — privacy, terms, and Bar Council compliance."),
    '404.html': ("Page Not Found | Khurana &amp; Khurana", "The page you requested could not be found."),
}
for f, (t, d) in TITLE_MAP.items():
    p = os.path.join(ROOT, f)
    if not os.path.exists(p): continue
    s = read(p)
    s = re.sub(r'<title>.*?</title>', f'<title>{t}</title>', s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + d + m.group(2), s, count=1)
    write(p, s)

print("titles updated")
