import sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from PIL import Image, ImageDraw

def _add_q(cur, p0, c, p1, n=9):
    for t in range(1, n + 1):
        u = t / (n + 1.0)
        cur.append(((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
                    (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1]))

def glyph_bitmap(font, gid, size=140, pad=8):
    glyf = font['glyf']
    gname = font.getGlyphOrder()[gid]
    g = glyf[gname]
    if g.isComposite() or g.numberOfContours == 0:
        return None
    pen = RecordingPen()
    g.draw(pen, glyf)
    contours = []
    cur = []
    for op, args in pen.value:
        if op == 'moveTo':
            if cur: contours.append(cur)
            cur = [args[0]]
        elif op == 'lineTo':
            cur.append(args[0])
        elif op == 'qCurveTo':
            if not cur:
                cur.append(args[0])
                if len(args) == 1: continue
                prev = args[0]
            elif len(args) == 1:
                cur.append(args[0]); continue
            else:
                prev = cur[-1]
                pts = list(args); i = 0
                while i < len(pts):
                    if i + 1 == len(pts) - 1:
                        _add_q(cur, prev, pts[i], pts[i + 1]); prev = pts[i + 1]; i += 2
                    else:
                        mx = (pts[i][0] + pts[i + 1][0]) / 2.0; my = (pts[i][1] + pts[i + 1][1]) / 2.0
                        _add_q(cur, prev, pts[i], (mx, my)); prev = (mx, my); i += 1
                cur.append(prev)
        elif op == 'curveTo':
            p0 = cur[-1]
            for t in range(1, 14):
                u = t / 14.0
                x = (1-u)**3*p0[0] + 3*(1-u)**2*u*args[0][0] + 3*(1-u)*u*u*args[1][0] + u**3*args[2][0]
                y = (1-u)**3*p0[1] + 3*(1-u)**2*u*args[0][1] + 3*(1-u)*u*u*args[1][1] + u**3*args[2][1]
                cur.append((x, y))
        elif op == 'closePath':
            if cur: contours.append(cur)
            cur = []
    if cur: contours.append(cur)
    xs = [p[0] for c in contours for p in c]; ys = [p[1] for c in contours for p in c]
    if not xs: return None
    x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
    w = max(x1 - x0, 1); h = max(y1 - y0, 1)
    scale = (size - 2 * pad) / max(w, h)
    canvas = [0] * (size * size)
    for c in contours:
        pts = [((p[0] - x0) * scale + pad, (p[1] - y0) * scale + pad) for p in c]
        if len(pts) < 3: continue
        layer = Image.new("L", (size, size), 0)
        ImageDraw.Draw(layer).polygon(pts, fill=255)
        data = list(layer.getdata())
        canvas = [canvas[i] ^ data[i] for i in range(len(canvas))]
    img = Image.new("L", (size, size))
    img.putdata(canvas)
    return img

def norm(img, w=36, h=36):
    if img is None: return None
    bb = img.getbbox()
    if not bb: return None
    img = img.crop(bb)
    im = img.resize((w, h))
    return list(im.getdata())

def dist(a, b):
    return sum(1 for i in range(len(a)) if (a[i] < 128) != (b[i] < 128))

REF_CHARS = ("0123456789"
             "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
             ".,+-*/='():;%#&$@_\u2013\u2014\u00b0\u00b1\u00d7\u00b2\u00b3"
             "\u00c5\u03a9\u03c9\u03a6\u03c6\u03b8\u03b2\u03c1\u03bb\u03a8"
             "Wwm\u221a\u2248\u2265\u2264\u2192\u2022\u00a7\u00b6\u00b5\u00b7\u0394")

def build_refmap(reffonts):
    refmap = {}
    for rf in reffonts:
        f = TTFont(rf)
        cmap = f.getBestCmap()
        gset = f.getGlyphOrder()
        for c in REF_CHARS:
            gname = cmap.get(ord(c))
            if gname is None: continue
            gid = gset.index(gname)
            img = glyph_bitmap(f, gid)
            u = norm(img)
            if u is not None:
                refmap.setdefault(c, u)
    return refmap

def main():
    ttf = sys.argv[1]
    reverse = {}
    for line in sys.stdin.read().splitlines():
        line = line.strip()
        if line.startswith('<') and '>' in line:
            a, b = line.split()
            reverse.setdefault(b.strip('<>'), a.strip('<>'))
    f = TTFont(ttf)
    gset = f.getGlyphOrder()
    refmap = build_refmap(sys.argv[2:])
    for pua in sorted(reverse):
        gid = int(reverse[pua], 16)
        img = glyph_bitmap(f, gid)
        u = norm(img)
        if u is None:
            print(f"F{pua}: EMPTY"); continue
        best = sorted(((dist(u, r), c) for c, r in refmap.items()), key=lambda t: t[0])[:5]
        print(f"F{pua} (gid {gid}): " + ", ".join(f"{c!r}({d})" for d, c in best))


if __name__ == "__main__":
    main()
