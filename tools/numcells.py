import pymupdf
doc = pymupdf.open('rankov2012.pdf')
page = doc[64]  # page 65 = Table 4.2
trace = page.get_texttrace()
rows = {}
for item in trace:
    if not item['chars']: continue
    fname = item['font']
    if 'Regular' not in fname: continue   # only body font
    for (uni,gid,origin,bbox) in item['chars']:
        if uni is None or uni<0x20: continue
        ch = chr(uni)
        if ch in '0123456789.':
            y = round(origin[1])
            rows.setdefault(y,[]).append((origin[0], ch))
for y in sorted(rows):
    line = ''.join(c for _,c in sorted(rows[y], key=lambda t:t[0]))
    print(y, line)
