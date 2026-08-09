import pymupdf
from fontTools.ttLib import TTFont

import os
_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
_CACHE = os.path.join(_BASE, '.cache')
doc = pymupdf.open(DOC)
for xref in [1518, 1520, 1521]:
    f = TTFont(os.path.join(_CACHE, f"font_{xref}.ttf"))
    cmap = f['cmap']
    print(f"\n===== font xref {xref} cmap tables =====", flush=True)
    for t in cmap.tables:
        n = len(getattr(t, 'cmap', {}))
        print(f"  platformID={t.platformID} platEncID={t.platEncID} format={t.format} n={n}", flush=True)
    t4 = [t for t in cmap.tables if t.format==4]
    t0 = [t for t in cmap.tables if t.format==0]
    chosen = t4[0] if t4 else (t0[0] if t0 else None)
    if chosen:
        rev = {}
        for uni, gid in chosen.cmap.items():
            rev.setdefault(gid, []).append(uni)
        print(f"  format {chosen.format} reverse map ({len(rev)} gids):", flush=True)
        for gid in sorted(rev):
            parts = []
            for u in rev[gid]:
                parts.append(chr(u) if 0x20 <= u < 0x7f else f"U+{u:04X}")
            print(f"    GID {gid}: {'/'.join(parts)}", flush=True)
