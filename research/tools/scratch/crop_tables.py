import pymupdf
import os
_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
doc = pymupdf.open(DOC)
# printed p.72 = pdf index 84 ; table 8.3 is near bottom. Render a tighter crop at higher zoom.
page = doc[84]
r = page.rect
# crop lower third (table area)
clip = pymupdf.Rect(r.x0, r.y0 + 0.52*r.height, r.x1, r.y1 - 0.02*r.height)
pix = page.get_pixmap(matrix=pymupdf.Matrix(4,4), clip=clip)
pix.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache', "t83.png"))
print("saved", pix.width, pix.height)
