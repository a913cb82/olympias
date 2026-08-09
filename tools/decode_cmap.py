import pymupdf
from fontTools.ttLib import TTFont

import os
_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
_CACHE = os.path.join(_BASE, '.cache')
doc = pymupdf.open(DOC)

for xref in [1518, 1520, 1521]:
    f = TTFont(os.path.join(_CACHE, f"font_{xref}.ttf"))
    cmap = f.getBestCmap()
    rev = {}
    if cmap:
        for uni, gid in cmap.items():
            rev.setdefault(gid, []).append(uni)
    name = doc.extract_font(xref)[2]
    print(f"\n===== font xref {xref} ({name}) =====", flush=True)
    if not cmap:
        print("  no best cmap; tables:", f.keys(), flush=True)
    for gid in sorted(rev):
        parts = []
        for u in rev[gid]:
            parts.append(chr(u) if 0x20 <= u < 0x7f else f"U+{u:04X}")
        print(f"  GID {gid}: {'/'.join(parts)}", flush=True)
