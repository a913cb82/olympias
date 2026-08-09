import pymupdf
doc = pymupdf.open('rankov2012.pdf')
for xref,out in [(1438,'tt292.ttf'),(1458,'tt291b.ttf'),(1453,'tt293.ttf')]:
    try:
        name, ext, ftype, buffer = doc.extract_font(xref)
        open(out,'wb').write(buffer)
        print(out, name, len(buffer))
    except Exception as e:
        print('err',xref,e)
