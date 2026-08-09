import freetype, numpy as np
from fontTools.ttLib import TTFont

ttf = TTFont('tt292.ttf')
gorder = ttf.getGlyphOrder()

face = freetype.Face('tt292.ttf')
face.set_pixel_sizes(0, 64)

def raster_face(face, name, size=64):
    face.set_pixel_sizes(0, size)
    try:
        face.load_glyph(face.get_char_index(ord(name[0])))
    except Exception:
        return None
    # For glyph-by-name, use load_glyph with glyph index from cmap when possible
    idx = face.get_name_index(name)
    if idx == 0 and len(name)==1:
        idx = face.get_char_index(ord(name))
    face.load_glyph(idx, freetype.FT_LOAD_RENDER)
    buf = np.array(face.glyph.bitmap.buffer, dtype=np.uint8).reshape(face.glyph.bitmap.rows, face.glyph.bitmap.width)
    return buf

def raster_glyph_byindex(face, idx, size=64):
    face.set_pixel_sizes(0, size)
    face.load_glyph(idx, freetype.FT_LOAD_RENDER)
    return np.array(face.glyph.bitmap.buffer, dtype=np.uint8).reshape(face.glyph.bitmap.rows, face.glyph.bitmap.width)

# Build reference chars from AGaramond CFF via fontTools is hard; instead use the SAME TT292 font but
# with knowledge that the subset has lost unicode. Alternative: use a system serif? No.
# Better: build references by finding on-page AGaramond digits (body text) via pymupdf bbox crops.
import pymupdf, cv2
doc = pymupdf.open('rankov2012.pdf')
page = doc[64]
pix = page.get_pixmap(matrix=pymupdf.Matrix(6,6))
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:,:,:3]
# reference chars: grab digits from body text (Regular font) e.g. the numbers on page 65 body text at y=399 '1994130' etc.
# find chars in AGaramond Regular in table-adjacent body text
refs = {}
trace = page.get_texttrace()
for item in trace:
    if 'Regular' not in item['font']: continue
    for (uni,gid,origin,bbox) in item['chars']:
        if uni is not None and chr(uni) in '0123456789.':
            x0,y0,x1,y1 = bbox
            cx = int(x0*6); cy = int(y0*6); cx1=int(x1*6); cy1=int(y1*6)
            crop = img[cy:cy1, cx:cx1]
            if crop.size and crop.shape[0]>0 and crop.shape[1]>0:
                refs.setdefault(chr(uni), crop)
print('refs found:', {k:v.shape for k,v in refs.items()})

# now match table TT292 glyphs by bbox crop
def score(a,b):
    h=int(max(a.shape[0],b.shape[0])*1.2); w=int(max(a.shape[1],b.shape[1])*1.2)
    A=np.zeros((h,w)); B=np.zeros((h,w))
    A[:a.shape[0],:a.shape[1]]=a.astype(float); B[:b.shape[0],:b.shape[1]]=b.astype(float)
    A/=max(1,A.max()); B/=max(1,B.max())
    return np.sum(A*B)/max(1e-6,np.sqrt(np.sum(A*A)*np.sum(B*B)))

for item in trace:
    if 'TT292' not in item['font']: continue
    for (uni,gid,origin,bbox) in item['chars']:
        if 140 <= origin[1] <= 230:
            x0,y0,x1,y1 = bbox
            cx=int(x0*6); cy=int(y0*6); cx1=int(x1*6); cy1=int(y1*6)
            crop = img[cy:cy1, cx:cx1]
            if crop.size==0 or crop.shape[0]==0 or crop.shape[1]==0: continue
            gray = np.mean(crop, axis=2)
            inv = 255-gray
            best=None; bs=-1
            for ch, rc in refs.items():
                rg = np.mean(rc, axis=2); rin = 255-rg
                s = score(inv, rin)
                if s>bs: bs=s; best=ch
            print('gid',gid,'x',round(x0),'y',round(y0),'->',best, round(bs,2))
