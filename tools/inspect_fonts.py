import pymupdf
doc = pymupdf.open('rankov2012.pdf')
page = doc[61]  # page 62
trace = page.get_texttrace()
from collections import defaultdict
fontchars = defaultdict(list)
for item in trace:
    if not item['chars']: continue
    fname = item['font']
    for (uni,gid,origin,bbox) in item['chars']:
        if origin[1] > 180 and origin[1] < 290:  # table region roughly
            fontchars[fname].append((round(origin[0]),round(origin[1]),uni,gid))
for fname, lst in fontchars.items():
    print('FONT', fname, 'chars in table region:', len(lst))
    for x,y,u,g in sorted(lst, key=lambda t:(t[1],t[0])):
        print('   x',x,'y',y,'uni',u,'gid',g)
