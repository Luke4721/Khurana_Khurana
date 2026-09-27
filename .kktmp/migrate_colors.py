#!/usr/bin/env python3
"""Rebrand color pass: Momento indigo -> Khurana & Khurana charcoal/maroon/slate.

Mapping (old -> new):
  #000321 (primary indigo)   -> #14100e (warm charcoal, maroon-tinted)
  #000320                    -> #14100e
  #010320                    -> #14100e
  #000218 (dark indigo)      -> #100d0b (deeper charcoal)
  #000214 (darkest indigo)   -> #0d0a09 (near-black warm)
  #00021d                    -> #100d0b
  #05071C / #05071c          -> #171110
  #0a1240 (lighter indigo)   -> #241a17
  #131a2d                    -> #241c19
  #1e2842 (elevated indigo)  -> #2c211d
  #10234f (slate navy)       -> #2b5672 (K&K slate)
  #6B6D7F (cool gray-lilac)  -> #8a8578 (warm stone gray)
  #7E7E97                    -> #9a948a
  #70738F                    -> #96908a
  #AEB0C6                    -> #b8b2a6
  #4A4D66 (mid indigo gray)  -> #5c564d
  #4A4A4A                    -> #4a4642

  Amber/gold accents:
  #ff8b1a, #f99c00           -> #b3542f (ember, harmonizes with maroon+bronze)
  Amber tailwind classes bg-amber-500 etc -> ember hexes in CSS var layer

  rgba() indigo equivalents:
  rgba(0,3,33,x)  -> rgba(20,16,14,x)   (charcoal)
  rgba(0,2,24,x)  -> rgba(16,13,11,x)
  rgba(0,2,20,x)  -> rgba(13,10,9,x)
"""
import re, glob, os

HEX_MAP = {
    '#000321': '#14100e', '#000320': '#14100e', '#010320': '#14100e',
    '#000218': '#100d0b', '#000214': '#0d0a09', '#00021d': '#100d0b',
    '#05071C': '#171110', '#05071c': '#171110',
    '#0a1240': '#241a17', '#131a2d': '#241c19', '#1e2842': '#2c211d',
    '#10234f': '#2b5672',
    '#6B6D7F': '#8a8578', '#7E7E97': '#9a948a', '#70738F': '#96908a',
    '#AEB0C6': '#b8b2a6', '#4A4D66': '#5c564d', '#4A4A4A': '#4a4642',
    '#ff8b1a': '#b3542f', '#f99c00': '#b3542f', '#FF8B1A': '#b3542f', '#F99C00': '#b3542f',
    # K&K signature accents that were already amber-adjacent:
    '#dd7400': '#9A0000', '#b75000': '#7C0303',  # tailwind amber-600/700 vars -> K&K deep reds
    '#B75000': '#7C0303', '#DD7400': '#9A0000',
}

def map_rgb(m):
    r, g, b, rest = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    if (r, g, b) == (0, 3, 33):   rgb = (20, 16, 14)
    elif (r, g, b) == (0, 2, 24): rgb = (16, 13, 11)
    elif (r, g, b) == (0, 2, 20): rgb = (13, 10, 9)
    elif (r, g, b) == (255, 139, 26): rgb = (179, 84, 47)
    elif (r, g, b) == (249, 156, 0):  rgb = (179, 84, 47)
    else: return m.group(0)
    return f"rgba({rgb[0]},{rgb[1]},{rgb[2]},{rest}"

changed_files = 0
targets = glob.glob('public/**/*.html', recursive=True) + [
    'public/_next/static/chunks/0.fcycf--gwr..css',
    'public/_next/static/chunks/103fz6ow0gz4j.css',
    'public/_next/static/chunks/0o7s~nivrs1sq.css',
]
for f in targets:
    try:
        s = open(f, encoding='utf-8').read()
    except Exception:
        continue
    orig = s
    for old, new in HEX_MAP.items():
        s = s.replace(old, new)
    s = re.sub(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([^)]+)\)', map_rgb, s)
    # bg-red-400 is a stray utility on the clock section; neutralize to charcoal
    s = s.replace('bg-red-400', 'bg-[#14100e]')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
        changed_files += 1
print("files recolored:", changed_files)
