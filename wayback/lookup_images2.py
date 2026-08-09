#!/usr/bin/env python3
"""Fetch per-monthly-dir CDX listings and match our image filenames."""
import subprocess, json, time, urllib.parse, re, collections, os
BASE = os.path.dirname(os.path.abspath(__file__))

IMAGES = [l.strip() for l in open('/tmp/allimgs.txt') if l.strip()]
dirs = collections.OrderedDict()
for u in IMAGES:
    d = '/'.join(u.split('/')[:5])  # https://modelshipworld.com/uploads/monthly_XXXX_XX
    dirs.setdefault(d, []).append(u.split('/')[-1])

os.makedirs(os.path.join(BASE, 'dirlists'), exist_ok=True)
all_rows = {}
for d, files in dirs.items():
    month = d.split('/')[-1]
    out = os.path.join(BASE, 'dirlists', f'{month}.json')
    if not os.path.exists(out):
        q = 'http://web.archive.org/cdx/search/cdx?url=' + urllib.parse.quote(d + '/', safe='') + '&matchType=prefix&output=json&fl=timestamp,original,statuscode,mimetype&filter=statuscode:200&limit=20000'
        r = subprocess.run(['curl', '-s', '--max-time', '60', q], capture_output=True, text=True)
        try:
            rows = json.loads(r.stdout)
        except Exception:
            rows = []
        with open(out, 'w') as f:
            json.dump(rows, f)
        print(f"{month}: {len(rows)-1 if rows else 0} rows")
        time.sleep(6)
    else:
        rows = json.load(open(out))
    # build map from filename -> list of (ts, url)
    for row in rows[1:]:
        ts, orig, status, mime = row[0], row[1], row[2], row[3]
        fname = orig.split('/')[-1]
        all_rows.setdefault(fname, []).append((ts, orig))

# Now match each of our images
print("\n=== MATCHES ===")
results = {}
def norm(fname):
    """Normalize an upload filename to its clean base (strip .thumb and 32-char hash)."""
    n = re.sub(r'\.thumb\.', '.', fname)
    n = re.sub(r'\.[a-f0-9]{32}\.(jpe?g|png|gif|webp|JPG|JPEG|PNG|GIF)$', '.\\1', n)
    return n

for u in IMAGES:
    fname = u.split('/')[-1]
    base = norm(fname)
    matches = all_rows.get(fname, [])
    cands = []
    for cand, rows in all_rows.items():
        if norm(cand) == base and cand != fname:
            cands.extend((cand, ts, orig) for ts, orig in rows)
    results[u] = {
        'base': base,
        'exact': matches,
        'thumb_variants': sorted(set((c, t) for c, t, o in cands)),
        'thumb_urls': sorted(set(o for c, t, o in cands)),
    }
    if matches:
        print(f"EXACT   {matches[0][0]}  {fname}")
    elif cands:
        print(f"THUMB   {cands[0][1]}  {fname} -> {cands[0][0]}")
    else:
        print(f"MISS    {fname}")

with open(os.path.join(BASE, 'image_archive_map.json'), 'w') as f:
    json.dump(results, f, indent=2)
