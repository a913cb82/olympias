import pymupdf
doc = pymupdf.open('rankov2012.pdf')
for pno in [61,62,64,65]:
    page = doc[pno-1]
    trace = page.get_texttrace()
    pts = []
    for item in trace:
        if not item['chars']: continue
        for (uni,gid,origin,bbox) in item['chars']:
            if uni is not None and 0xF000<=uni<=0xF0FF:
                pts.append((round(origin[0]), round(origin[1])))
    xs = sorted(set(x for x,y in pts))
    ys = sorted(set(y for x,y in pts))
    if pts:
        print('page',pno,'nPUA',len(pts),'x range',min(xs),max(xs),'y range',min(ys),max(ys))
