import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import portal_server


class PortalHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.index = Path(cls.temp.name) / "index.json"
        cls.index.write_text(json.dumps({"records": [{
            "document_id": "http-act", "version_id": "1234567890abcdef",
            "source_checksum_sha256": "d" * 64, "document_title": "HTTP Test Act",
            "source_reference": "PDF page 8", "structure_path": [{"kind": "section", "number": "8"}],
            "page_number": 8, "text": "A court may make an order.", "number": "8",
            "kind": "section", "source_url": "https://example.gov.pg/act"
        }]}), encoding="utf-8")
        portal_server.PortalHandler.index_path = cls.index
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), portal_server.PortalHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def test_homepage_served(self):
        with urlopen(self.base + "/") as response:
            self.assertEqual(response.status, 200)
            self.assertIn("PNG Legal Library", response.read().decode())

    def test_health_endpoint(self):
        with urlopen(self.base + "/api/health") as response:
            self.assertEqual(json.load(response)["status"], "ready")

    def test_search_endpoint_and_security_headers(self):
        request = Request(self.base + "/api/search",
                          data=json.dumps({"query": "court order"}).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request) as response:
            result = json.load(response)
            self.assertEqual(result["result_count"], 1)
            self.assertEqual(result["results"][0]["document_id"], "http-act")
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
            self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])

    def test_unknown_api_route_rejected(self):
        with self.assertRaises(Exception):
            urlopen(self.base + "/api/unknown")


if __name__ == "__main__":
    unittest.main()
