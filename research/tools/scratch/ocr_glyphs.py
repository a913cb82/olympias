import pymupdf, sys
from PIL import Image

def render_char(fontfile, char, size=64):
    font = pymupdf.Font(fontfile=fontfile)
    doc = pymupdf.open()
    page = doc.new_page(width=400, height=300)
    tw = pymupdf.TextWriter(page.rect)
    tw.append((200, 150), char, font=font, fontsize=size)
    tw.write_text(page)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
    img = img.point(lambda v: 255 if v < 128 else 0)
    bb = img.getbbox()
    if bb:
        img = img.crop(bb)
        return img
    return None

def norm(img, w=24, h=28):
    if img is None:
        return [0] * (w * h)
    im = img.resize((w, h))
    return list(im.getdata())

def distance(a, b):
    return sum(1 for i in range(len(a)) if a[i] != b[i])

def main():
    embedded = sys.argv[1]
    xref = sys.argv[2]
    n = int(sys.argv[3])
    chars = [chr(0xF000 + i) for i in range(1, n + 1)]
    ref_font = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    ref_chars = "0123456789.,+-*/='():mHLCWkwx\u2013"
    refmap = {c: norm(render_char(ref_font, c)) for c in ref_chars}
    print(f"=== embedded font xref {xref} glyph matching ===")
    for ch in chars:
        u = norm(render_char(embedded, ch))
        best = sorted(((distance(u, r), c) for c, r in refmap.items()), key=lambda t: t[0])[:3]
        print(f"{ch} (U+{ord(ch):04X}): " + ", ".join(f"{c}({d})" for d, c in best))

main()
