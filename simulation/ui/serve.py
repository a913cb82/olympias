#!/usr/bin/env python3
"""Serve the replay UI locally (stdlib only — no dependencies).

Usage (from simulation/):
    python3 ui/serve.py                # http://localhost:8000/viewer.html
    python3 ui/serve.py --port 9000 --no-browser
"""

from __future__ import annotations

import argparse
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):  # "/" -> the viewer
        if self.path in ("/", "/index.html"):
            self.path = "/viewer.html"
        super().do_GET()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()
    url = f"http://localhost:{args.port}/viewer.html"
    print(f"replay UI: {url}  (ctrl-C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
