#!/usr/bin/env python3
"""Expertise pages: rewrite each clone practice page as a K&K practice area."""
import re, json, os, html as H

kk = json.load(open('.kktmp/pages.json'))

def body_of(key, limit=4200):
    """Extract the main body text of a scraped K&K page."""
    t = kk.get(key, {}).get('text', '')
    m = re.search(r'Careers & Internships Contact Us', t)
    if m:
        t = t[m.end():]
    end_m = re.search(r'Contact Us Tel: \+91-\(120\) 3132513', t)
    if end_m:
        t = t[:end_m.start()]
    # drop trailing nav-ish repeats
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:limit]

def paragraphs(text, minlen=60):
    """Split into sentence-ish paragraphs (heuristic on headings being short)."""
    parts = re.split(r'(?<=[.!?]) (?=[A-Z])', text)
    return [p.strip() for p in parts if len(p) >= minlen or p.isupper()]

# Clone page -> (K&K source key, new title, new meta description, hero heading)
MAPPING = [
    ('corporate-law', 'trademark-filing-portfolio', 'IP Protection & Portfolio Management',
     'End-to-end IP procurement, protection, and portfolio management — patents, trademarks, copyright, and designs, from idea inception to successful commercialization.',
     'IP Protection & Portfolio Management'),
    ('mergers-and-acquisitions', 'ip-litigation', 'IP Litigation & Enforcement',
     '18+ years of IP litigation experience — infringement actions, due diligence, claim mapping, and enforcement before Indian courts and tribunals.',
     'IP Litigation & Enforcement'),
    ('banking-and-finance', 'advisories-and-opinions', 'IP Advisory & Opinions',
     'Expert legal opinions on Prior Art, Freedom-to-Operate, Validity, and Non-infringement, with clear, commercially aware litigation strategies.',
     'IP Advisory & Opinions'),
    ('capital-markets-law', 'commercial-litigation', 'Commercial Law Practice',
     'Contract drafting and vetting, company law, corporate secretarial practice, and comprehensive commercial litigation support.',
     'Commercial Law Practice'),
    ('energy-and-mining-law', 'domain-name-resolution-practice', 'Domain Name Resolution Practice',
     'UDRP and ICANN-accredited dispute resolution for gTLD domain names, plus civil-court remedies where registrants or registrars are located.',
     'Domain Name Resolution'),
    ('arbitration', 'anti-counterfeiting', 'Anti-Counterfeiting Practice',
     'Anti-counterfeiting strategies across FMCG, Pharma, Apparel, Footwear, and Medical Devices — criminal actions, seizure orders, and border enforcement.',
     'Anti-Counterfeiting Practice'),
    ('dispute-resolution', 'litigation-support', 'Litigation Support',
     'Litigation support across IP and commercial disputes — evidence, expert testimony, damages analysis, and coordinated multi-forum strategy.',
     'Litigation Support'),
    ('international-trade-law', 'international', 'International Practice',
     'Patent and trademark filing and prosecution across the Gulf, South-East Asia, and worldwide through K&K\u2019s trusted international associate network.',
     'International Practice'),
    ('competition-law', 'patent-search-mapping-analysis', 'IP Research & Analytics',
     'Patent searches, landscape mapping, claim charts, due diligence, and IP strategy advisory powered by IIPRD\u2019s research bench.',
     'IP Research & Analytics'),
    ('data-protection', 'ibc-advisory', 'IBC & Insolvency Advisory',
     'Insolvency-related IP and commercial advisory — claims, moratorium interplay, and enforcement strategy under the IBC, 2016.',
     'IBC & Insolvency Advisory'),
]

def esc(s):
    return s.replace('&', '&amp;')

def rewrite_page(clone_slug, src_key, title, meta, hero):
    path = f'public/expertise/{clone_slug}.html'
    s = open(path, encoding='utf-8').read()

    # title + meta
    s = re.sub(r'<title>.*?</title>', f'<title>{esc(title)} | Khurana &amp; Khurana</title>', s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + esc(meta) + m.group(2), s, count=1)

    body_text = body_of(src_key)
    paras = paragraphs(body_text)

    # 1) hero h1 (the big page title)
    s = re.sub(r'(<h1[^>]*>).*?(</h1>)',
               lambda m: m.group(1) + esc(hero) + m.group(2), s, count=1, flags=re.S)

    # 2) replace the intro/quote paragraph if present (blockquote area)
    # 3) body: locate the first long content paragraph and replace the paragraph run after it
    # Strategy: find the region of consecutive <p class="text-[16px]... "> ... and rebuild with K&K copy
    p_re = re.compile(r'<p class="text-\[16px\][^"]*"[^>]*>.*?</p>', re.S)
    p_matches = list(p_re.finditer(s))
    if p_matches:
        first, last = p_matches[0], p_matches[-1]
        new_html = ''.join(
            f'<p class="text-[16px] md:leading-[1.25vw] text-white/67 mb-[16px] md:mb-[1.5vw] md:text-[0.938vw]">{esc(p)}</p>'
            for p in paras) or first.group(0)
        s = s[:first.start()] + new_html + s[last.end():]

    # 4) meta description + any leftover practice copy
    open(path, 'w', encoding='utf-8').write(s)
    return len(paras)

results = {}
for clone_slug, src_key, title, meta, hero in MAPPING:
    try:
        n = rewrite_page(clone_slug, src_key, title, meta, hero)
        results[clone_slug] = ('ok', n)
    except Exception as e:
        results[clone_slug] = ('err', str(e))
for k, v in results.items():
    print(k, v)
