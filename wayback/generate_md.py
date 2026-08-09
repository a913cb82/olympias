#!/usr/bin/env python3
"""Generate the recovered old-log markdown archive and recovery report."""
import json, re, datetime
import os
BASE = os.path.dirname(os.path.abspath(__file__))

posts = json.load(open(os.path.join(BASE, 'richard_posts.json')))
imgmap = json.load(open(os.path.join(BASE, 'image_archive_map.json')))

def fmt_date(iso):
    try:
        d = datetime.datetime.fromisoformat(iso.replace('Z', '+00:00'))
        return d.strftime('%B %d, %Y')
    except Exception:
        return iso

def resolve_image(url):
    """Return best display URL: archived copy if available, else original."""
    info = imgmap.get(url)
    if not info:
        return url, None
    if info['exact']:
        ts, orig = info['exact'][0]
        return f"https://web.archive.org/web/{ts}id_/{orig}", f"wayback-full-{ts}"
    if info['thumb_urls']:
        # thumb archived
        tu = info['thumb_urls'][0]
        # find ts
        for cand, ts in info['thumb_variants']:
            if cand in tu:
                return f"https://web.archive.org/web/{ts}id_/{tu}", f"wayback-thumb-{ts}"
        return f"https://web.archive.org/web/{info['thumb_variants'][0][1]}id_/{tu}", "wayback-thumb"
    return url, None

def rewrite_body(body):
    out = []
    for line in body.split('\n'):
        m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)$', line)
        if m:
            src, tag = resolve_image(m.group(2))
            out.append(f"![{m.group(1)}]({src})")
        else:
            out.append(line)
    return '\n'.join(out)

# ---- build markdown ----
lines = []
lines.append('# Trireme "Olympias" by Richard Braithwaite — Recovered Pre-Hack Build Log (Topic 21958)')
lines.append('')
lines.append('Source: [Model Ship World — archived topic 21958](https://web.archive.org/web/20250427010555/https://modelshipworld.com/topic/21958-trireme-olympias-by-richard-braithwaite/), recovered from the Internet Archive Wayback Machine after the site was hacked.')
lines.append('')
lines.append('This is the **pre-hack build log** (topic 21958, "Trireme Olympias by Richard Braithwaite", started September 2019). It is **separate from** the newer re-posted log (topic 424) which is recorded in `trireme-olympias-build-log-richard-braithwaite.md`.')
lines.append('')
lines.append('### Recovery summary')
lines.append('')
lines.append('- The archived thread had **9 pages** (per the pagination of the latest page-1 snapshot).')
lines.append('- Wayback captured **pages 1–5** (posts 1–126 of the thread). **Pages 6–9 were never archived** and their full text is lost.')
lines.append('- **49 of Richard\'s posts** (Sep 2019 – May 2022) were recovered in full from pages 1–5, in chronological order below.')
lines.append('- **8 additional post snippets** (June–July 2025, i.e. the missing pages) were recovered from Richard\'s profile activity stream and are listed in a separate section below as *fragments*.')
lines.append('- Images: where an image was archived by Wayback, the link points to the archived copy; otherwise the original (now-broken) URL is kept.')
lines.append('')
lines.append('---')
lines.append('')

order = sorted(posts, key=lambda p: p['date'])
for i, p in enumerate(order, 1):
    lines.append(f"## Post {i} — {p['author']} — #{p['postnum']} in thread ({fmt_date(p['date'])})")
    lines.append('')
    body = rewrite_body(p['body'])
    lines.append(body)
    lines.append('')
    if p['edited']:
        ed, ea = p['edited']
        lines.append(f"**Edited {fmt_date(ed)} by {ea}**")
        lines.append('')
    lines.append('---')
    lines.append('')

# ---- fragments from profile stream ----
fragments = [
    ('1103343', '2025-06-11T16:05:49Z',
     'Tapering of oar blades: Image top left: jig, made of holly... used with all 62 Thranite oar blades. Top right: set up in machinists vice on Unimat with spacers cut to incline the top surface of the jig correctly for the taper to be cut... Finally 62 Tranite blades tapered (about 16 mins/blade...)'),
    ('1103684', '2025-06-14T21:32:29Z',
     'Next steps: Jig fixing tabs removed from blades and blades shaped to plan view using a ply template pattern... Blades fixed to oar shafts between prongs... Total time taken for all this approximately 40 mins/blade. Quite a lot longer than just fitting 0.5mm ply blades and probably almost impossible to see the difference once they are finished and painted white, but so be it...'),
    ('1103809', '2025-06-15T21:33:07Z',
     'I actually find this production line stuff quite theraputic. Once all the thinking is done and I know what im doing I can just sit in my workshop and go through the motions, one after another. Not so much of an issue now Im retired, but I used to find it very relaxing after a stressfull day at work!'),
    ('1104002', '2025-06-17T15:54:09Z',
     'Since turning the handle on this oar production line doesn\'t use up much mental bandwidth I\'ve been listening to podcasts as I go. I\'ve been finding the style of "The Rest is History" just about the right level... Thermopylae and Salamis: Athens and the Birth of Democracy: Herodotus, the birth of history: Sparta:'),
    ('1105024', '2025-06-27T15:51:19Z',
     'All blades fitted... Now cutting a radius onto two of the faces of that thickened part of the oar shaft inboard of the thole pins... Cutting a piece of plastic pipe in two longitudinally and then lining with sandpaper, however seemed to work surprizingly well... (extract of Plans 15 © Estate of John F. Coates, reproduced with permission).'),
    ('1105134', '2025-06-28T17:47:41Z',
     'Some statistics for the oars at this stage (i.e. shaping complete prior to painting) WEIGHT: So my oars scale at 11.71 kg/oar... compared to 12.3 kg/oar on the full size Olympias... LABOUR: So, to get to this stage has taken me 3.25 hours per oar... Duration wise its taken me about 4 months to make 62 of them... the cost of an oar for Olympias in 1987 is quoted as £300 (ref the Trireme Trials 1988)'),
    ('1106198', '2025-07-08T17:39:51Z',
     'An exciting post about paint! I need to coat my oars. Shafts varnished and blades painted. Products Ive tried below: Four different trial combos below. 1. 4 coats of varnish... 2. 4 coats of varnish over bothe areas... 3. 3 coats white matt enamel on bare wood. 4. 1 coat Humbro undercoat... Apparently the shellac in the BIN undercoat will slow the discoloration of the white paint... so Im probably going with option 1...'),
    ('1106329', '2025-07-09T21:39:11Z',
     'Yes the philosophy throughout has been waterproofness, hence use of expoxy for bonding and polyurethane for sealing. But aesthetics are just as important (probably more so now, given how much further Ive ended going with this model than I origianlly envisaged...)'),
]

lines.append('## Fragments from the un-archived pages 6–9 (via Richard\'s profile activity stream)')
lines.append('')
lines.append('These are the only recoverable text from the final pages of the old thread (June–July 2025). They were captured as snippet excerpts on Richard\'s MSW profile page, not as full posts.')
lines.append('')
for cid, date, snippet in fragments:
    lines.append(f'### Post fragment (comment {cid}, {fmt_date(date)})')
    lines.append('')
    lines.append('> ' + snippet.replace('\n', '\n> '))
    lines.append('')

content = '\n'.join(lines)

# ---- write ----
outpath = '/home/acbraith/projects/sandbox/trireme-olympias-archived-build-log-21958-richard-braithwaite.md'
with open(outpath, 'w') as f:
    f.write(content)
print(f"Wrote {outpath} ({len(content.splitlines())} lines)")
