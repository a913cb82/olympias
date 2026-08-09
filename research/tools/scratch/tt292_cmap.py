from fontTools.ttLib import TTFont
f = TTFont('tt292.ttf')
best = f.getBestCmap() or {}
print('best cmap entries:', len(best))
digits = {k:v for k,v in best.items() if 0x30<=k<=0x39}
print('digit cmap:', sorted(digits.items()))
# build gid->unicode reverse
g2u = {}
for t in f['cmap'].tables:
    if t.cmap:
        for code, gname in t.cmap.items():
            g2u.setdefault(gname, code)
print('n gname mappings:', len(g2u))
for gname in ['uniF001','uniF002','uniF005','uniF008','uniF00C','uniF00F']:
    print(gname, hex(g2u.get(gname,0)))
