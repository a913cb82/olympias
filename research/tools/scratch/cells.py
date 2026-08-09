import pymupdf
doc = pymupdf.open('rankov2012.pdf')
page = doc[64]  # page 65
trace = page.get_texttrace()
# group by y
rows = {}
for item in trace:
    if not item['chars']: continue
    for (uni,gid,origin,bbox) in item['chars']:
        y = round(origin[1])
        x = origin[0]
        rows.setdefault(y,[]).append((x, uni, gid, item['font']))
for y in sorted(rows):
    if 140 <= y <= 225:
        line = ' '.join(f"{x}:u{uni},g{gid}" for x,uni,gid,f in sorted(rows[y], key=lambda t:t[0]))
        print(y, line)
