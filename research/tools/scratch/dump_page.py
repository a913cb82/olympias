import sys
from fontTools.cffLib import CFFFontSet
import io, pymupdf
raw = open('font1.cff','rb').read()
cff = CFFFontSet()
cff.decompile(io.BytesIO(raw), None)
font = cff['ZDIKFF+AGaramondPro-Regular']
charset = list(font.charset)
m = {'zero':'0','one':'1','two':'2','three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','period':'.','colon':':','hyphen':'-','comma':',','slash':'/','percent':'%','space':' ','bracketleft':'[','bracketright':']','parenleft':'(','parenright':')','equal':'=','less':'<','greater':'>','quotedbl':'"','quoteleft':'`','quoteright':"'",'exclam':'!','question':'?','semicolon':';','plus':'+','dollar':'$','numbersign':'#','ampersand':'&','asterisk':'*','endash':chr(0x2013),'emdash':chr(0x2014),'degree':chr(0xB0),'onehalf':chr(0xBD),'plusminus':chr(0xB1),'onequarter':chr(0xBC),'threequarters':chr(0xBE),'multiply':chr(0xD7),'minus':chr(0x2212),'approxequal':chr(0x2248),'section':chr(0xA7),'paragraph':chr(0xB6)}
def gchar(gid):
    n = charset[gid] if 0<=gid<len(charset) else '?'
    if n in m: return m[n]
    if n and len(n)==1: return n
    if n and n.startswith('uni'):
        try: return chr(int(n[3:],16))
        except: return '?'
    return '['+n+']'

doc = pymupdf.open('rankov2012.pdf')
pno = int(sys.argv[1])
page = doc[pno-1]
trace = page.get_texttrace()
rows = {}
for item in trace:
    if not item['chars']: continue
    for (uni,gid,origin,bbox) in item['chars']:
        if uni is None and gid is None: continue
        if uni is not None and 32<=uni<0x3000 and not (0xF000<=uni<=0xF0FF):
            ch = chr(uni)
        else:
            ch = gchar(gid)
        y = round(origin[1])
        x = origin[0]
        rows.setdefault(y,[]).append((x,ch))
for y in sorted(rows):
    line = ''.join(c for _,c in sorted(rows[y], key=lambda t:t[0]))
    if line.strip():
        print(line)
