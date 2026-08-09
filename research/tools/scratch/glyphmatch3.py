import freetype, numpy as np, io

def load_face(path):
    return freetype.Face(path)

tt_face = load_face('tt292.ttf')
# CFF face: freetype can load .cff? write font1.cff content is a CFF; freetype needs sfnt container usually.
# Instead rasterize TT292 glyphs and compare within TT292 itself using structural features, OR
# build references from the PDF-rendered AGaramond digits (already have) but with alignment via scipy.
from scipy.ndimage import shift
import pymupdf

doc = pymupdf.open('rankov2012.pdf')
page = doc[64]
pix = page.get_pixmap(matrix=pymupdf.Matrix(8,8))
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:,:,:3]

def crop_bbox(bbox):
    x0,y0,x1,y1 = bbox
    cx=int(x0*8); cy=int(y0*8); cx1=int(x1*8); cy1=int(y1*8)
    return np.mean(img[cy:cy1, cx:cx1], axis=2)

# references: AGaramond digits from body text
refs = {}
trace = page.get_texttrace()
for item in trace:
    if 'Regular' not in item['font']: continue
    for (uni,gid,origin,bbox) in item['chars']:
        if uni is not None and chr(uni) in '0123456789.':
            crop = crop_bbox(bbox)
            if crop.size and crop.max()>0:
                refs.setdefault(chr(uni), crop)
def normmask(g):
    return (255-g)/255.0
def pad(g):
    # pad to square
    h,w = g.shape
    s = max(h,w)
    out = np.zeros((s,s))
    out[:h,:w] = g
    return out

# translation-invariant correlation via FFT
def match(cand, ref):
    c = normmask(cand); r = normmask(ref)
    c = pad(c); r = pad(r)
    # zero-pad both to same size
    n = max(c.shape[0], r.shape[0]) + 8
    C = np.zeros((n,n)); R = np.zeros((n,n))
    C[:c.shape[0],:c.shape[1]] = c; R[:r.shape[0],:r.shape[1]] = r
    from numpy.fft import fft2, ifft2
    cc = ifft2(fft2(R)*np.conj(fft2(C))).real
    # normalized: use the max cross-correlation normalized by norms
    best = cc.max()
    return best/max(1e-9, np.sqrt((C*C).sum()*(R*R).sum()))

rows={}
for item in trace:
    if 'TT292' not in item['font']: continue
    for (uni,gid,origin,bbox) in item['chars']:
        if 140 <= origin[1] <= 230:
            crop = crop_bbox(bbox)
            if crop.size==0 or crop.max()==0: continue
            best=None; bs=-1
            for ch,rc in refs.items():
                s = match(crop, rc)
                if s>bs: bs=s; best=ch
            y=round(origin[1]); x=origin[0]
            rows.setdefault(y,[]).append((x,best,round(bs,2)))
for y in sorted(rows):
    line = ''.join(b for _,b,_ in sorted(rows[y],key=lambda t:t[0]))
    print(y, line)
