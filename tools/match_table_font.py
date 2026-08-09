import sys
from PIL import Image, ImageFont, ImageDraw

def render(fontfile, char, size=120):
    font = ImageFont.truetype(fontfile, size)
    img = Image.new("L", (size * 2, size * 2), 255)
    d = ImageDraw.Draw(img)
    d.text((size // 2, size), char, font=font, fill=0)
    bbox = img.getbbox()
    if not bbox:
        return None
    img = img.crop(bbox)
    return img

def norm(img, w=32, h=32):
    if img is None:
        return [0] * (w * h)
    im = img.resize((w, h))
    return list(im.getdata())

def dist(a, b):
    return sum(1 for i in range(len(a)) if (a[i] < 128) != (b[i] < 128))

# reference character set: ASCII + common symbols
ref_chars = (
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    ".,+-*/='():;%#&$@_"
    "\u00b0\u00b1\u00d7\u00b2\u00b3\u00b4\u2013\u2014\u2018\u2019\u201c\u201d"
    "\u00a0\u00c5\u03a9\u03c9\u03a6\u03c6\u03b8\u03b2\u03c1\u03bb"
    "m\u207b\u207a\u2192\u2190\u2248\u2265\u2264\u221e\u221a\u2022"
    "Ww\u210a"
)
ref_fonts = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/droid/DroidSerif-Regular.ttf",
]

def main():
    fontfile = sys.argv[1]
    n = int(sys.argv[2])
    # build ref map from all ref fonts
    refmap = {}
    for rf in ref_fonts:
        for c in ref_chars:
            try:
                img = render(rf, c)
            except Exception:
                continue
            if img is None:
                continue
            refmap[c] = norm(img)
    for i in range(1, n + 1):
        ch = chr(0xF000 + i)
        try:
            img = render(fontfile, ch)
        except Exception as e:
            print(f"U+{ord(ch):04X}: ERR {e}")
            continue
        if img is None:
            print(f"U+{ord(ch):04X}: EMPTY")
            continue
        un = norm(img)
        best = sorted(((dist(un, r), c) for c, r in refmap.items()), key=lambda t: t[0])[:4]
        print(f"U+{ord(ch):04X}: " + ", ".join(f"{c!r}({d})" for d, c in best))

main()
