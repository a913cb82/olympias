from fontTools.ttLib import TTFont
f = TTFont('tt292.ttf')
for t in f['cmap'].tables:
    print('platform',t.platformID,'encoding',t.platEncID,'n',len(t.cmap.items()) if t.cmap else 0)
    if t.cmap:
        items = sorted(t.cmap.items())
        print('  sample:', [(hex(k),v) for k,v in items[:10]])
        print('  PUA count:', sum(1 for k in items if 0xF000<=k<=0xF0FF))
        # show non-PUA entries
        nonpua = [i for i in items if not (0xF000<=i[0]<=0xF0FF)]
        print('  non-PUA sample:', [(hex(k),v) for k,v in nonpua[:20]])
