import pymupdf, re, sys
from fontTools.cffLib import CFFFontSet
import io

# Build glyph-name -> char map from font1.cff (same subset used throughout body)
raw = open('font1.cff','rb').read()
cff = CFFFontSet()
cff.decompile(io.BytesIO(raw), None)
font = cff['ZDIKFF+AGaramondPro-Regular']
charset = list(font.charset)
m = {'zero':'0','one':'1','two':'2','three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','period':'.','colon':':','hyphen':'-','comma':',','slash':'/','percent':'%','space':' ','bracketleft':'[','bracketright':']','parenleft':'(','parenright':')','equal':'=','less':'<','greater':'>','quotedbl':'"','quoteleft':'`','quoteright':"'",'exclam':'!','question':'?','semicolon':';','plus':'+','dollar':'$','numbersign':'#','ampersand':'&','asterisk':'*','endash':chr(0x2013),'emdash':chr(0x2014),'degree':chr(0xB0),'onehalf':chr(0xBD),'plusminus':chr(0xB1),'onequarter':chr(0xBC),'threequarters':chr(0xBE),'multiply':chr(0xD7),'minus':chr(0x2212),'approxequal':chr(0x2248),'section':chr(0xA7),'paragraph':chr(0xB6),'dagger':chr(0x2020),'oneeighth':chr(0x215B),'threeeighths':chr(0x215C),'seveneighths':chr(0x215E)}
def gname_to_char(n):
    if n in m: return m[n]
    if n and len(n)==1: return n
    if n and n.startswith('uni'):
        try: return chr(int(n[3:],16))
        except: return '?'
    return '['+n+']'
def gid_to_char(gid):
    n = charset[gid] if 0<=gid<len(charset) else '?'
    return gname_to_char(n)

doc = pymupdf.open('rankov2012.pdf')
# For each page get fonts: xref -> font name, and whether it's the same charset (all subsets share base names)
for pno in [61,62,64,65]:
    page = doc[pno-1]
    cstream = b''
    for c in page.get_contents():
        cstream += doc.xref_stream(c)
    # find fonts dict for page
    fonts = {}
    for f in page.get_fonts(full=True):
        fonts[f[3]] = f[1]
    # get the char codes as bytes, tracking current font via Tf
    # We'll extract all (font, bytes) by scanning text operators
    tokens = re.findall(rb'/([A-Za-z0-9_.+]+)\s+([\d.]+)\s+Tf|\[?\(([^)]*)\)\]?\s*Tj|\[?<([0-9A-Fa-f]+)>\]?\s*Tj|TJ', cstream)
    cur = None
    out = []
    i = 0
    data = cstream
    # manual scan
    mfont = None
    # regex with alternating
    pat = re.compile(rb'/([A-Za-z0-9_.+]+)\s+([\d.]+)\s+Tf|\(((?:[^()\\]|\\.)*)\)\s*Tj|<([0-9A-Fa-f]+)>\s*Tj|((?:[\(][^()]*[\)]|[<\w>])\s*)*TJ')
    pos = 0
    segs = []  # (font, textbytes)
    curfont = None
    for mm in re.finditer(rb'/([A-Za-z0-9_.+]+)\s+[\d.]+\s+Tf|\(([^()]*(?:\([^()]*\)[^()]*)*)\)|\[(.*?)\]', cstream):
        pass
    # simpler: find Tf and Tj/TJ sequentially
    items = re.findall(rb'/([A-Za-z0-9_.+]+)\s+[\d.]+\s+Tf|Tj|TJ', cstream)
    strings = re.findall(rb'[<][0-9A-Fa-f]+[>]|\([^)]*\)', cstream)
    # The above doesn't preserve order reliably. Instead, use pymupdf's rawtext for chars but with the correct font mapping.
    # Use page.get_texttrace which gives gid per char (correct) - we just need gid->char via correct font per span.
    # get_texttrace 'chars' gid is relative to the span's font subset. We need per-span font mapping.
    trace = page.get_texttrace()
    for item in trace:
        fname = item['font']
        # determine subset: look up font; all AGaramondPro subsets share same charset? no.
        pass
    print('skip', pno)
