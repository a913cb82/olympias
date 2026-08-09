import pymupdf
doc = pymupdf.open('rankov2012.pdf')
seen={}
for pno in [61,62,64,65]:
    page = doc[pno-1]
    for row in page.get_fonts(full=True):
        xref=row[0]; name=row[3]; ftype=row[4]
        key=xref
        if key not in seen:
            seen[key]=name
        print(pno, xref, name, ftype)
