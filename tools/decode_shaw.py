import pymupdf, json, hashlib, os, io, sys
import numpy as np
from PIL import Image, ImageDraw
from matplotlib import ft2font
from scipy import ndimage

_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
CACHE = os.path.join(_BASE, '.cache', 'glyph_map3.json')
W, H = 18, 22

REF_FONTS = [os.path.abspath(x) for x in [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"]]
REF_CHARS = "0123456789.,+-*/=():'mHLCWkwx\u2013abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "


def _write_ttf(fontbytes, tag):
    os.makedirs(os.path.join(_BASE, '.cache'), exist_ok=True)
    path = os.path.join(_BASE, '.cache', f'_ft_{tag}.ttf')
    open(path, 'wb').write(fontbytes)
    return path


def render_mask(fontpath, char, size=72, dpi=100):
    ft = ft2font.FT2Font(fontpath)
    ft.set_size(size, dpi)
    ft.load_char(ord(char))
    verts, codes = ft.get_path()
    contours = []
    cur = []
    for (v, c) in zip(verts, codes):
        if c == 1:  # MOVETO
            if cur:
                contours.append(cur)
            cur = [tuple(v)]
        elif c == 2:  # LINETO
            cur.append(tuple(v))
        elif c == 3:  # CURVE3 (quadratic)
            p0 = cur[-1]
            p1, p2 = tuple(verts[0]), tuple(v)
            for i in range(1, 9):
                u = i / 9.0
                cur.append(((1-u)**2*p0[0] + 2*(1-u)*u*p1[0] + u*u*p2[0],
                            (1-u)**2*p0[1] + 2*(1-u)*u*p1[1] + u*u*p2[1]))
        elif c == 4:  # CURVE4 (cubic)
            p0 = cur[-1]
            for i in range(1, 13):
                u = i / 12.0
                x = (1-u)**3*p0[0] + 3*(1-u)**2*u*verts[0][0] + 3*(1-u)*u*u*verts[1][0] + u**3*v[0]
                y = (1-u)**3*p0[1] + 3*(1-u)**2*u*verts[0][1] + 3*(1-u)*u*u*verts[1][1] + u**3*v[1]
                cur.append((x, y))
        elif c == 79:  # CLOSEPOLY
            if cur:
                contours.append(cur)
            cur = []
    if cur:
        contours.append(cur)
    if not contours:
        return None
    xs = [p[0] for c in contours for p in c]
    ys = [p[1] for c in contours for p in c]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    w = max(x1 - x0, 1e-3)
    h = max(y1 - y0, 1e-3)
    scale = 84.0 / max(w, h)
    img = Image.new("L", (96, 96), 0)
    d = ImageDraw.Draw(img)
    for c in contours:
        pts = [((p[0] - x0) * scale + 6, (p[1] - y0) * scale + 6) for p in c]
        if len(pts) >= 3:
            d.line(pts + [pts[0]], fill=255, width=3)
    arr = np.array(img)
    ys_i, xs_i = np.nonzero(arr)
    if not len(ys_i):
        return None
    arr = arr[ys_i.min():ys_i.max() + 1, xs_i.min():xs_i.max() + 1]
    im = Image.fromarray(arr).resize((W, H))
    return np.array(im) > 0


REFS = {}
for fp in REF_FONTS:
    for c in REF_CHARS:
        if c in REFS:
            continue
        m = render_mask(fp, c)
        if m is not None:
            REFS[c] = m
REF_EDT = {c: ndimage.distance_transform_edt(~m) for c, m in REFS.items()}
print(f"[init] {len(REFS)} reference glyphs", file=sys.stderr)


def classify_font(fontbytes, tag):
    fpath = _write_ttf(fontbytes, tag)
    ft = ft2font.FT2Font(fpath)
    mapping = {}
    for cp in range(0xF000, 0xF100):
        idx = ft.get_char_index(cp)
        if idx == 0:
            continue
        ft.load_char(cp)
        m = render_mask(fpath, chr(cp))
        p = cp - 0xF000
        if m is None or not m.any():
            mapping[str(p)] = ' '
            continue
        res = sorted(((REF_EDT[c][m].mean(), c) for c in REF_EDT), key=lambda t: t[0])
        if res[0][0] < 1.6:
            mapping[str(p)] = res[0][1]
        else:
            mapping[str(p)] = ' '
    return mapping


def get_mapping(font_bytes):
    key = hashlib.sha1(font_bytes).hexdigest()
    db = {}
    if os.path.exists(CACHE):
        db = json.load(open(CACHE))
    if key in db:
        return db[key]
    m = classify_font(font_bytes, key[:10])
    db[key] = m
    json.dump(db, open(CACHE, 'w'))
    return m


def decode_page(doc, pno, cache):
    page = doc[pno]
    fonts = {}
    for finfo in page.get_fonts(full=True):
        basefont = finfo[3]
        if '+TT' in basefont or 'TT2' in basefont:
            fonts[basefont.split('+')[-1]] = finfo[0]
    rd = page.get_text('rawdict')
    out = []
    for block in rd['blocks']:
        for line in block.get('lines', []):
            spans = []
            for span in line['spans']:
                fname = span['font']
                if fname.startswith('TT'):
                    xref = fonts.get(fname)
                    if xref is not None and xref not in cache:
                        try:
                            cache[xref] = get_mapping(doc.extract_font(xref)[3])
                        except Exception as e:
                            print(f"[warn] page {pno} font {fname} xref {xref}: {e}", file=sys.stderr)
                            cache[xref] = {}
                    m = cache.get(xref, {})
                    txt = ''.join(m.get(str(ord(ch['c']) - 0xF000), '?') for ch in span['chars'])
                    spans.append((round(span['bbox'][0], 1), txt))
                else:
                    txt = ''.join(ch['c'] for ch in span['chars'])
                    spans.append((round(span['bbox'][0], 1), txt))
            spans.sort()
            y = round(line['bbox'][1], 1)
            out.append((y, spans))
    return out


if __name__ == '__main__':
    pages = [int(x) for x in sys.argv[1:]]
    doc = pymupdf.open(DOC)
    cache = {}
    for pno in pages:
        print(f"\n################ PDF PAGE {pno} ################")
        for y, spans in decode_page(doc, pno, cache):
            line = '  '.join(f"x={x:5} {t!r}" for x, t in spans)
            print(f"y={y:6} {line}")
