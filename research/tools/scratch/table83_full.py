import pymupdf
TT292 = {1:'f',2:'e',3:'t',4:'c',5:'h',6:' ',7:'k',8:'m',9:'d',0xA:'u',0xB:'r',0xC:'a',0xD:'i',0xE:'o',0xF:'n',0x10:'s',0x11:'W',0x12:'=',0x13:'4',0x14:'.',0x15:'5',0x16:'7',0x17:'0'}
TT293 = {1:'5',2:'0',3:' ',4:'3',5:'.',6:'2',7:'4',8:'1',9:'7',10:'9',11:'6',12:'8',13:'*'}
import os
_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
doc = pymupdf.open(DOC)
page = doc[84]
rd = page.get_text("rawdict")
for block in rd["blocks"]:
    for line in block.get("lines", []):
        spans = [s for s in line["spans"] if s["font"].startswith("TT")]
        if not spans: continue
        parts = []
        for span in spans:
            M = TT292 if span["font"].startswith("TT292") else TT293
            txt = "".join(M.get(ord(ch["c"])-0xF000, "?") for ch in span["chars"])
            parts.append((round(span["bbox"][0],1), txt, span["font"]))
        parts.sort()
        y = round(line["bbox"][1],1)
        print(f"y={y:7} " + "  ".join(f"x={x:7} {txt!r}[{font[:5]}]" for x,txt,font in parts))
