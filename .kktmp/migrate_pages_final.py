#!/usr/bin/env python3
"""Final content pass for the K&K rebrand."""
import re, json, os, html as H

kk = json.load(open('.kktmp/pages.json'))
bios = json.load(open('.kktmp/bios.json'))

def clean(t):
    return re.sub(r'\s+', ' ', t).strip()

def body(key, limit=9000):
    t = kk.get(key, {}).get('text', '')
    m = re.search(r'Careers & Internships Contact Us', t)
    if m: t = t[m.end():]
    e = re.search(r'Contact Us Tel: \+91-\(120\) 3132513', t)
    if e: t = t[:e.start()]
    return clean(t)[:limit]

def esc(s):
    return H.escape(s, quote=False).replace('&', '&amp;')

PARA = 'text-[16px] md:leading-[1.25vw] text-white/67 mb-[16px] md:mb-[1.5vw] md:text-[0.938vw]'
HEAD = 'font-forum text-[22px] md:text-[1.6vw] text-white mt-[28px] mb-[12px]'

def paras_html(text, limit=4200):
    out = ''
    for p in re.split(r'(?<=[.!?]) (?=[A-Z])', text[:limit]):
        p = p.strip()
        if len(p) < 40:
            continue
        t = esc(p)
        if t.isupper() or (len(t) < 70 and not t.endswith('.')):
            out += f'<h2 class="{HEAD}">{t}</h2>'
        else:
            out += f'<p class="{PARA}">{t}</p>'
    return out

def strip_react(s):
    s = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.S)
    return re.sub(r'<link[^>]*as="script"[^>]*/>', '', s)

# ---------------------------------------------------------------- ABOUT
s = open('public/about.html', encoding='utf-8').read()
about_body = body('about-us')
s = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda m: m.group(1) + 'About Khurana &amp; Khurana' + m.group(2), s, count=1, flags=re.S)
ps = list(re.finditer(r'<p class="text-\[16px\][^"]*"[^>]*>.*?</p>', s, re.S))
if ps:
    s = s[:ps[0].start()] + paras_html(about_body) + s[ps[-1].end():]
open('public/about.html', 'w', encoding='utf-8').write(strip_react(s))
print('about done')

# ---------------------------------------------------------------- CULTURE (pro bono + values)
s = open('public/culture.html', encoding='utf-8').read()
culture_body = body('pro-bono') or 'Committed to equal access to justice, K&K encourages every member of the firm to devote time pro bono.'
s = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda m: m.group(1) + 'Pro Bono &amp; Culture' + m.group(2), s, count=1, flags=re.S)
ps = list(re.finditer(r'<p class="text-\[16px\][^"]*"[^>]*>.*?</p>', s, re.S))
if ps:
    s = s[:ps[0].start()] + paras_html(culture_body) + s[ps[-1].end():]
open('public/culture.html', 'w', encoding='utf-8').write(strip_react(s))
print('culture done')

# ---------------------------------------------------------------- CONTACT offices
OFFICES = [
    ("NOIDA — HEAD OFFICE", "D-45, UPSIDC Site-IV, Greater Noida, UP 201315", "+91-(120) 3132513, +91-8076160683"),
    ("NEW DELHI", "S-378, Panchsheel Park, New Delhi 110017", "+91-(011) 40079530"),
    ("BANGALORE", "260, 15 Main Road, RMV Ext, Sadashivnagar, Bengaluru 560080", "+91-(080) 42506603"),
    ("PUNE", "Plot No 395 & 396, Shree Krishna Nagar, SB Road, Pune 411016", "+91-(020) 25652120"),
    ("MUMBAI", "B2-304, Kanakia Boomerang, Chandivali, Powai, Mumbai 400072", "+91-(022) 41002054"),
    ("HYDERABAD", "Coworkzone, Plot No 63, Kavuri Hills Phase 1, Jubilee Hills, Hyderabad 500033", "+91-(120) 3132513"),
    ("PUNJAB", "A2-905, Jal Vayu Vihar, Jalandhar, AFNHB, Punjab 144008", "+91-(120) 3132513"),
    ("CHENNAI", "2, New No. 21, 11th Street, Z Block, Anna Nagar, Chennai 600040", "+91-(044) 45011960"),
    ("AHMEDABAD", "Lilavati Chambers, Ashram Rd, Ellisbridge, Ahmedabad 380009", "+91-(011) 3132513"),
    ("INDORE", "62, Malgunj, Bhagat Singh Marg, Jawahar Marg, Indore 452002", "+91-(120) 3132513"),
]
s = open('public/contact.html', encoding='utf-8').read()
s = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda m: m.group(1) + 'Contact Us' + m.group(2), s, count=1, flags=re.S)
# Replace the old single location block (find "İSTANBUL" region) with an offices grid
i = s.find('LOCATION')
if i > 0:
    block_start = s.rfind('<div', 0, i)
    offices_html = ''.join(
        f'<div class="flex flex-col gap-[4px] mb-[14px]"><span class="font-forum uppercase text-[14px] text-white/90">{esc(name)}</span>'
        f'<span class="text-[13px] text-white/60">{esc(addr)}</span>'
        f'<span class="text-[13px] text-white/50">{esc(tel)}</span></div>'
        for name, addr, tel in OFFICES)
    # find the enclosing region end: the form area start
    j = s.find('First name', i)
    js = s.rfind('<div', 0, j) if j > 0 else i + 4000
    s = s[:block_start] + f'<div class="flex flex-col gap-[8px]">{offices_html}</div>' + s[js:]
s = strip_react(s)
open('public/contact.html', 'w', encoding='utf-8').write(s)
print('contact done')

# ---------------------------------------------------------------- POLICIES pages with K&K texts
PRIVACY = body('privacy-policy', 6000) or 'Privacy policy of Khurana & Khurana.'
TERMS = body('terms-and-conditions', 6000) or 'Terms and conditions governing the use of this website.'
BAR = body('compliance-to-bar-council-rules', 6000) or 'Compliance statement under the Bar Council of India rules.'
policy_pages = {
    'public/policies/privacy-policy.html': ('Privacy Policy', PRIVACY),
    'public/policies/terms-and-conditions.html': ('Terms & Conditions', TERMS),
    'public/policies/compliance-to-bar-council-rules.html': ('Compliance to Bar Council Rules', BAR),
    'public/policies/privacy-notice.html': ('Privacy Notice', PRIVACY),
    'public/policies/cv-privacy-notice.html': ('CV Privacy Notice', 'How Khurana & Khurana handles personal data in recruitment.'),
    'public/policies/data-request-form.html': ('Data Request Form', 'Submit a data access or correction request to Khurana & Khurana.'),
}
for path, (title, bodytext) in policy_pages.items():
    if not os.path.exists(path):
        continue
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(title)} | Khurana &amp; Khurana</title>', s, count=1, flags=re.S)
    s = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda m: m.group(1) + esc(title) + m.group(2), s, count=1, flags=re.S)
    ps = list(re.finditer(r'<p class="text-\[16px\][^"]*"[^>]*>.*?</p>', s, re.S))
    if ps:
        s = s[:ps[0].start()] + paras_html(bodytext, 5000) + s[ps[-1].end():]
    open(path, 'w', encoding='utf-8').write(strip_react(s))
print('policies done')

# ---------------------------------------------------------------- HOME specifics
s = open('public/index.html', encoding='utf-8').read()
# hero H1s (three instances: mobile + desktop copies)
s = re.sub(r'The Moment of Precision', 'Rendering Sage Legal Advice', s)
# partners strip names (home page carousel) — replace remaining Momento team names with K&K partners
kk_names = [(b['name'], b['role']) for b in bios[:15]]
# remaining old names on home
for old in ['Dr. Melih Can Korkmaz','Okan Yasan','Gizem Kalkavan','Özge Tekbudak Yasan','Mahmut Yılmaz','Nursen Maosai','Sercan Atila','Oğuz Efe Daşkın','Defne Boyacı','Ahmet Kağan Altıngemi','Esra Sürgit','Ece Sare Yaman','Alper Çetiner','Navruz Memilli','Mert Memilli']:
    s = s.replace(old, '')
s = s.replace('— Founder', '— Founding &amp; Managing Partner')
s = s.replace('Founder', 'Founding &amp; Managing Partner')
open('public/index.html', 'w', encoding='utf-8').write(s)
print('home done')
