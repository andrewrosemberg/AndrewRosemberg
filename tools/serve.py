#!/usr/bin/env python3
"""Serve _site/ under /AndrewRosemberg/ on port 8767, the same subpath as GitHub Pages,
so root-absolute links that would break in production also break here."""

import functools
import http.server
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "_site"
PREFIX = "/AndrewRosemberg"


class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path == PREFIX or path.startswith(PREFIX + "/"):
            return super().translate_path(path[len(PREFIX):] or "/")
        return str(SITE / "__outside_subpath__")  # 404, as in production

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # rebuilt files replace old ones under the same name
        super().end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
    handler = functools.partial(Handler, directory=str(SITE))
    print(f"Serving _site/ at http://127.0.0.1:{port}{PREFIX}/")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
