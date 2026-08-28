#!/usr/bin/env python3
"""Parse Richard Braithwaite's profile activity stream for topic 21958 reply snippets."""

import html as H
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))


def parse_stream(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    text = re.sub(r"<script.*?</script>", "", raw, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL)
    # Each stream item: snippet in data-ipsTruncate div, time, and findComment link
    items = []
    # Split on stream items
    chunks = re.split(r'<li class=[\'"]ipsStreamItem', text)
    for chunk in chunks[1:]:
        # skip non-21958 items early
        if "topic/21958" not in chunk:
            continue
        # snippet
        sm = re.search(r"data-ipsTruncate(?:[^>]*)>(.*?)</div>", chunk, re.DOTALL)
        snippet = re.sub(r"<[^>]+>", " ", sm.group(1)) if sm else ""
        snippet = H.unescape(re.sub(r"\s+", " ", snippet)).strip()
        # date
        dm = re.search(r"<time datetime='([^']+)'", chunk)
        date = dm.group(1) if dm else None
        # comment id
        cm = re.search(r"findComment&amp;comment=(\d+)", chunk)
        cid = cm.group(1) if cm else None
        # replies
        rm = re.search(r"(\d+) replies", chunk)
        replies = rm.group(1) if rm else None
        items.append(
            {"commentid": cid, "date": date, "snippet": snippet, "replies": replies}
        )
    return items


if __name__ == "__main__":
    items = parse_stream(os.path.join(BASE, "html", "profile_33794_2025.html"))
    print(f"{len(items)} items for topic 21958")
    for it in items:
        print("---", it["commentid"], it["date"], "replies=" + str(it["replies"]))
        print(it["snippet"])
