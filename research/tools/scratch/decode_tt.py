from fontTools.ttLib import TTFont
f = TTFont('tt292.ttf')
cmap = f.getBestCmap()
g = f.getGlyphOrder()
print('glyphs:', len(g))
print('cmap entries:', len(cmap))
# print a few
for k in sorted(cmap)[:30]:
    print(hex(k), cmap[k])
