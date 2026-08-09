import pymupdf
MAP = {1:'5',2:'0',3:' ',4:'3',5:'.',6:'2',7:'4',8:'1',9:'7',10:'9',11:'6',12:'8',13:'*'}
import os
_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
doc = pymupdf.open(DOC)
page = doc[84]
rd = page.get_text("rawdict")
spans = []
for block in rd["blocks"]:
    for line in block.get("lines", []):
        for span in line["spans"]:
            if span["font"].startswith("TT"):
                txt = "".join(MAP.get(ord(ch["c"])-0xF000, "?") for ch in span["chars"])
                spans.append((round(span["bbox"][1],1), round(span["bbox"][0],1), span["font"], txt))
spans.sort()
for s in spans:
    print(f"y={s[0]:7} x={s[1]:7} {s[2]} : {s[3]}")
