#!/usr/bin/env python3
"""Find every escaped asset reference (flight-data form) across the fresh HTML."""
import re, glob

pat = re.compile(r'images\\u002F(teams|insights|header|footer|home|uploads)\\u002F([A-Za-z0-9_.-]+)')
found = {}
for f in glob.glob('public/**/*.html', recursive=True):
    txt = open(f, encoding='utf-8', errors='ignore').read()
    for m in pat.finditer(txt):
        key = f'{m.group(1)}/{m.group(2)}'
        found.setdefault(key, set()).add(f)

for k in sorted(found):
    print(k, '<-', len(found[k]), 'files')
print('total unique refs:', len(found))
