from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cairoPen import CairoPen
from fontTools.cffLib import CFFFontSet
import io, os
os.environ['CAIRO']='1'
from PIL import Image, ImageDraw
import numpy as np

def raster_tt(font, gname, size=48):
    glyph = font.getGlyphSet()[gname]
    b = glyph.getBounds(font['hmtx'][gname][0] if False else 0)
    if b is None:
        return None
    x0,y0,x1,y1 = b
    w = max(1,int(x1-x0)); h = max(1,int(y1-y0))
    scale = size/max(w,h)
    pen = TTGlyphPen(font.getGlyphSet())
    glyph.draw(pen)
    from fontTools.pens.basePen import decomposeSuperBezierSegment
    # simpler: render via cairo
    import cairo
    surf = cairo.ImageSurface(cairo.FORMAT_A8, int(w*scale)+8, int(h*scale)+8)
    ctx = cairo.Context(surf)
    ctx.scale(scale, scale)
    ctx.translate(4/scale - x0, 4/scale - y0)
    ctx.move_to(0,0)
    pen2 = CairoPen(ctx, font.getGlyphSet())
    glyph.draw(pen2)
    ctx.set_source_rgba(1,1,1,1)
    ctx.fill()
    buf = surf.get_data()
    arr = np.frombuffer(buf, dtype=np.uint8).reshape(surf.get_height(), surf.get_width())
    return arr

def raster_cff(font, gname, size=48):
    import cairo
    try:
        gs = font.getGlyphSet()
        glyph = gs[gname]
    except Exception:
        return None
    b = glyph.getBounds()
    if b is None:
        return None
    x0,y0,x1,y1 = b
    w=max(1,int(x1-x0)); h=max(1,int(y1-y0))
    scale = size/max(w,h)
    surf = cairo.ImageSurface(cairo.FORMAT_A8, int(w*scale)+8, int(h*scale)+8)
    ctx = cairo.Context(surf)
    ctx.scale(scale, scale)
    ctx.translate(4/scale - x0, 4/scale - y0)
    from fontTools.pens.cairoPen import CairoPen
    pen = CairoPen(ctx, gs)
    glyph.draw(pen)
    ctx.fill()
    buf = surf.get_data()
    arr = np.frombuffer(buf, dtype=np.uint8).reshape(surf.get_height(), surf.get_width())
    return arr

def norm(arr):
    return arr.astype(float)/255.0

# Load TT292
ttf = TTFont('tt292.ttf')
# Load AGaramond regular (font1.cff)
raw = open('font1.cff','rb').read()
cff = CFFFontSet()
cff.decompile(io.BytesIO(raw), None)
gar = cff['ZDIKFF+AGaramondPro-Regular']


# candidate characters in AGaramond
cands = ['0','1','2','3','4','5','6','7','8','9','.']
names = {'0':'zero','1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven','8':'eight','9':'nine','.':'period'}
refs = {}
for c in cands:
    nm = names[c]
    idx = gar.charset  # list
    # get glyph name via charset index
    glyphname = gar.charset[cands.index(c)+17]
    arr = raster_cff(gar, glyphname)
    if arr is None:
        print('missing ref', c)
        continue
    refs[c] = norm(arr)

# Now iterate TT292 glyphs used in the table and match
# first get the list of gids used in table region on page 65
import pymupdf
doc = pymupdf.open('rankov2012.pdf')
page = doc[64]
trace = page.get_texttrace()
used = {}
for item in trace:
    if 'TT292' not in item['font']: continue
    for (uni,gid,origin,bbox) in item['chars']:
        if 140 <= origin[1] <= 230:
            used.setdefault(gid, (origin[0], origin[1]))
gorder = ttf.getGlyphOrder()
for gid,(x,y) in sorted(used.items(), key=lambda kv:(kv[1][1],kv[1][0])):
    gname = gorder[gid]
    arr = raster_tt(ttf, gname)
    if arr is None:
        print(gid, gname, '?')
        continue
    a = norm(arr)
    best = None; bestscore=-1
    for c,ra in refs.items():
        # resize to match
        import cv2
        if ra.shape!=a.shape:
            r2 = cv2.resize(ra, (a.shape[1], a.shape[0]))
        else:
            r2 = ra
        score = np.sum(a*r2)/max(1e-6, np.sqrt(np.sum(a*a)*np.sum(r2*r2)))
        if score>bestscore:
            bestscore=score; best=c
    print('gid',gid,'x',round(x),'y',round(y),'best',repr(best),'score',round(bestscore,2))
