#!/usr/bin/env python3
"""Loopback-only web server for the local PNG legal library portal."""
import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
PORTAL = ROOT / "portal"
from portal_api import search_request, health_response


class PortalHandler(SimpleHTTPRequestHandler):
    index_path = ROOT / "legal-index" / "index.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PORTAL), **kwargs)

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json(200, health_response(self.index_path))
        if path.startswith("/api/"):
            return self._json(404, {"error": "API endpoint not found."})
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/search":
            return self._json(404, {"error": "API endpoint not found."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 16384:
                return self._json(413, {"error": "Request must be between 1 and 16 KB."})
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            return self._json(200, search_request(payload, self.index_path))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return self._json(400, {"error": str(exc)})
        except FileNotFoundError:
            return self._json(503, {"error": "Local legal index is not available."})
        except Exception:
            return self._json(500, {"error": "Search could not be completed."})


def main():
    parser = argparse.ArgumentParser(description="Run the PNG legal library portal locally.")
    parser.add_argument("--index", default=str(ROOT / "legal-index" / "index.json"))
    parser.add_argument("--host", default="127.0.0.1",
                        help="Must remain loopback-only; remote binding is blocked.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.host not in ("127.0.0.1", "::1", "localhost"):
        parser.error("For privacy and safety, this server only binds to loopback addresses.")
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    PortalHandler.index_path = Path(args.index).resolve()
    server = ThreadingHTTPServer((args.host, args.port), PortalHandler)
    print(f"PNG Legal Library portal: http://{args.host}:{args.port}")
    print("Local-only server. Do not expose this development server to the public internet.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
