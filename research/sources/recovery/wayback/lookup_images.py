#!/usr/bin/env python3
"""Look up each image URL in the Wayback CDX to find archived copies."""

import json
import os
import subprocess
import time
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))


def cdx_query(url):
    q = (
        "http://web.archive.org/cdx/search/cdx?url="
        + urllib.parse.quote(url, safe="")
        + "&output=json&fl=timestamp,original,statuscode,mimetype&filter=statuscode:200&collapse=timestamp:6"
    )
    try:
        r = subprocess.run(
            ["curl", "-s", "--max-time", "30", q],
            capture_output=True,
            text=True,
            check=False,
        )
        return json.loads(r.stdout) if r.stdout.strip() else []
    except (json.JSONDecodeError, OSError):
        return []


def main():
    with open("/tmp/allimgs.txt") as fh:
        urls = [l.strip() for l in fh if l.strip()]
    results = {}
    for i, u in enumerate(urls):
        rows = cdx_query(u)
        results[u] = rows[1:] if rows else []
        ts = results[u][0][0] if results[u] else "NONE"
        print(f"[{i + 1}/{len(urls)}] {ts}  {u}")
        time.sleep(2)
    with open(os.path.join(BASE, "image_archive_map.json"), "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
