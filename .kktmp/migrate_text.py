#!/usr/bin/env python3
"""Global K&K text mapping across all pages (names, taglines, headings)."""
import glob, os

PAIRS = [
    # hero
    ('The Moment of Precision', 'Rendering Sage Legal Advice'),
    # about block
    ('About Momento', 'About Khurana & Khurana'),
    ('We assess legal matters not only through the lens of legislation, but together with their commercial, financial, and operational dimensions, bringing academic depth and practical experience onto the same ground.',
     'Khurana & Khurana (K&K), founded in 2007, is a leading IP and Commercial Law firm with over 330 professionals across 10 Indian offices. K&K, along with its sister firm IIPRD, offers end-to-end IP Prosecution, Litigation, and Commercialization services to 3000+ corporates.'),
    ('Success often emerges where knowledge meets timing. We build our work on three core principles: excellence, discipline, and trust.',
     'Renowned for quality and consistency, K&K excels in creating IP value through a highly skilled team across legal and technical domains, building long-term client relationships.'),
    # services heading
    ('Insight turns complexity into clarity at the right Momento.',
     'K&K offers end-to-end services across Intellectual Property and Commercial Law — from research and prosecution to litigation and commercialization.'),
    # expertise card list (Momento practice areas -> K&K service blocks)
    ('Strong companies are built on strong legal foundations.',
     'Efficient IP creation, protection, and enforcement — from idea inception to successful commercialization.'),
    ('Strategic transactions require strategic counsel.',
     '18+ years of Patent Litigation experience: infringement, due diligence, claim mapping, and enforcement.'),
    ('Reliable legal support for complex financial transactions.',
     'Expert legal opinions on Prior Art, FTO, Validity, and Non-infringement with clear litigation strategies.'),
    ('The legal foundation of trust and transparency.',
     'Contract drafting and vetting, compliance, and comprehensive litigation support for businesses in India.'),
    ('Strategic legal solutions for strategic sectors.',
     'ICANN/UDRP domain disputes — complaints before accredited centers or civil courts.'),
    ('Effective representation in cross-border disputes.',
     'Anti-counterfeiting across FMCG, Pharma, Apparel, Footwear, and Medical Devices.'),
    ('Clear strategies in complex disputes.',
     'End-to-end IP prosecution: patents, trademarks, copyright, design, and geographical indications.'),
    ('Legal solutions beyond borders.',
     'Patent and trademark filing across the Gulf, South-East Asia, and beyond via trusted associates.'),
    ('Not just knowing the rules, but understanding how the authorities think.',
     'IP research and analytics: patent searches, mapping, due diligence, and IP strategy advisory.'),
    ('Data protection compliance is not an obligation, but the foundation of corporate trust.',
     'IP Litigation and Enforcement — protecting and enforcing your most valuable IP assets.'),
    # practice-area card titles
    ('Corporate Law', 'IP Protection & Portfolio Management'),
    ('Mergers & Acquisitions', 'IP Litigation & Enforcement'),
    ('Banking & Finance', 'IP Advisory'),
    ('Capital Markets Law', 'Commercial Law Practice'),
    ('Energy & Mining Law', 'Domain Name Resolution Practice'),
    ('Competition Law', 'IP Research & Analytics'),
    ('Data Protection & Privacy', 'Anti-Counterfeiting Practice'),
    # insights strip
    ('Insight turns complexity into clarity', 'Insight turns complexity into clarity'),
    # team strip heading
    ('OUR CORE PRACTITIONERS', 'OUR CORE PRACTITIONERS'),
    # footer quote
    ('Let those who work win, and those who do not, lose.',
     'Rendering sage legal advice for pro-active enforcement.'),
    ('Let those who work win, and those who don’t lose.',
     'Rendering sage legal advice for pro-active enforcement.'),
    # expertise page hero fallbacks
    ('Our areas of legal expertise.',
     'Our areas of legal expertise across IP, Corporate & Commercial, Litigation, and Taxation.'),
    # menu items handled separately (expertise titles reused there)
]

# Momento people on home/team strips -> replaced later by team pass; global safe swaps:
NAME_SWAPS = [
    ('Melih Can Korkmaz, PhD, Attorney at Law', 'Tarun Khurana, Managing Partner'),
    ('Melih Can Korkmaz', 'Tarun Khurana'),
]

count = 0
for root, dirs, files in os.walk('public'):
    for fn in files:
        if not fn.endswith('.html'):
            continue
        p = os.path.join(root, fn)
        s = open(p, encoding='utf-8').read()
        o = s
        for a, b in PAIRS:
            s = s.replace(a, b)
        for a, b in NAME_SWAPS:
            s = s.replace(a, b)
        if s != o:
            open(p, 'w', encoding='utf-8').write(s)
            count += 1
print('text-mapped pages:', count)
