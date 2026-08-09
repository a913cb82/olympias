import pymupdf
import os
_BASE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(_BASE, '..', 'sources', 'rankov2012.pdf')
doc = pymupdf.open(DOC)
for pno in [84, 85]:  # printed pp. 72-73 (Table 8.3 area)
    page = doc[pno]
    print(f"===== PAGE {pno} =====")
    print(page.get_text())
