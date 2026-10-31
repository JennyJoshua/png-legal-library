import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "index.html"


class StaticPortalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_portal_page_exists_and_is_mobile_ready(self):
        self.assertIn('name="viewport"', self.html)
        self.assertIn("<title>PNG Legal Library</title>", self.html)

    def test_index_is_selected_locally_in_browser(self):
        self.assertIn('type="file"', self.html)
        self.assertIn("await file.text()", self.html)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_dynamic_text_is_html_escaped(self):
        self.assertIn("const esc=value=>", self.html)
        self.assertIn("esc(r.text)", self.html)
        self.assertIn("esc(title)", self.html)

    def test_source_links_are_restricted_to_https(self):
        self.assertIn("function safeHttpUrl(value)", self.html)
        self.assertIn('url.protocol==="https:"', self.html)
        self.assertIn("safeHttpUrl(r.source_url)", self.html)
        self.assertIn('rel="noopener noreferrer"', self.html)

    def test_user_can_clear_the_loaded_index(self):
        self.assertIn('id="clearBtn"', self.html)
        self.assertIn('addEventListener("click",()=>{records=[];', self.html)

    def test_no_result_message_does_not_claim_no_law_exists(self):
        self.assertIn("This does not prove that no relevant PNG law exists.", self.html)


if __name__ == "__main__":
    unittest.main()
