#!/usr/bin/env python3
"""Assemble Richard Braithwaite's posts from archived topic 21958 pages into markdown."""

import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_t21958 import parse_file

PAGES = [
    ("html/t21958_p1_2025.html", "1", "2025-04-27"),
    ("html/t21958_p2.html", "2", "2022-05-25"),
    ("html/t21958_p3.html", "3", "2023-03-30"),
    ("html/t21958_p4.html", "4", "2023-03-30"),
    ("html/t21958_p5.html", "5", "2022-05-25"),
]


def fmt_date(iso):
    import datetime

    try:
        d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return d.strftime("%B %d, %Y")
    except ValueError:
        return iso


posts_by_id = {}
for path, pageno, snap in PAGES:
    for post in parse_file(path):
        cid = post["commentid"]
        # keep the version with a body if duplicate
        if cid in posts_by_id:
            continue
        post["page"] = pageno
        post["snapshot"] = snap
        posts_by_id[cid] = post

# filter Richard
richard = [
    p for p in posts_by_id.values() if p["author"] and "Braithwaite" in p["author"]
]
richard.sort(key=lambda p: (p["date"] or "", int(p["postnum"] or 0)))

print(f"Total unique posts: {len(posts_by_id)}")
print(f"Richard posts: {len(richard)}")
print(f"Date range: {richard[0]['date']} .. {richard[-1]['date']}")
print(f"Post numbers: {[p['postnum'] for p in richard]}")

# save raw json for later phases
with open(os.path.join(BASE, "richard_posts.json"), "w") as f:
    json.dump(richard, f, indent=2)
