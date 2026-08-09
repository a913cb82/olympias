from fontTools.ttLib import TTFont
f = TTFont('tt292.ttf')
print('tables:', sorted(f.keys()))
print('glyph order (first 100):')
for i,n in enumerate(f.getGlyphOrder()[:100]):
    print(i, n)
