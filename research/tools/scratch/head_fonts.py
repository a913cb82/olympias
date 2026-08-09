import pymupdf
doc = pymupdf.open('rankov2012.pdf')
page = doc[61]  # page 62
trace = page.get_texttrace()
for item in trace:
    if not item['chars']: continue
    fname = item['font']
    for (uni,gid,origin,bbox) in item['chars']:
        if 100 <= origin[1] <= 200:
            print(fname, 'x',round(origin[0]),'y',round(origin[1]),'uni',uni,'gid',gid)
