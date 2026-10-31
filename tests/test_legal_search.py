import json, sys, tempfile, unittest
from jsonschema import validate
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from segment_legal_text import segment_text
from build_legal_index import build
from search_legal_index import search

class SegmentationTests(unittest.TestCase):
    def test_previous_section_keeps_its_own_structure_path(self):
        nodes = segment_text(
            "1. Interpretation\nCourt means a court.\n2. Application\nThis Act applies.",
            "PDF page 1", "sample", "1234567890abcdef"
        )
        self.assertEqual(nodes[0]["number"], "1")
        self.assertEqual(nodes[0]["structure_path"][-1]["number"], "1")
        self.assertEqual(nodes[1]["number"], "2")
        self.assertEqual(nodes[1]["structure_path"][-1]["number"], "2")

    def test_parts_divisions_sections_and_nested_provisions(self):
        text = "PART I—PRELIMINARY\nDIVISION 1—INTRODUCTORY\n1. Short title.\n(1) This Act may be cited as the Sample Act.\n(2) This Act applies in Papua New Guinea.\n(a) It applies to public authorities.\n2. Interpretation.\n(a) court means a court of competent jurisdiction."
        nodes = segment_text(text, "PDF page 4", "sample-act", "1234567890abcdef")
        self.assertTrue(any(n["kind"] == "section" and n["number"] == "1" for n in nodes))
        self.assertTrue(any(n["kind"] == "subsection" and n["number"] == "(1)" for n in nodes))
        self.assertTrue(any(n["kind"] == "paragraph" and n["number"] == "(a)" for n in nodes))
        self.assertTrue(all(n["page_number"] == 4 for n in nodes))
        self.assertIn("PRELIMINARY", nodes[0]["structure_path"][0]["title"])

    def test_unstructured_text_is_retained(self):
        nodes = segment_text("Preface paragraph.\nMore text.", "PDF page 1", "d", "1234567890abcdef")
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]["kind"], "unstructured")
        self.assertIn("More text", nodes[0]["text"])

    def test_section_heading_is_preserved(self):
        nodes = segment_text("Section 5. Interpretation\n(1) In this Act, court means...", "PDF page 9", "d", "1234567890abcdef")
        self.assertEqual(nodes[0]["kind"], "section")
        self.assertEqual(nodes[0]["title"], "Interpretation")
        self.assertEqual(nodes[1]["kind"], "subsection")

    def test_docx_reference_preserved(self):
        nodes = segment_text("1. Short title.\nThis Act may be cited.", "DOCX paragraph 8", "d", "1234567890abcdef")
        self.assertEqual(nodes[0]["paragraph_number"], 8)

class IndexSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name); self.input = self.root / "extracted"; self.output = self.root / "index"
        self.input.mkdir()
        record = {"document_id":"sample-act","version_id":"1234567890abcdef","document_title":"Sample Act 2026",
                  "source_url":"https://parliament.gov.pg/sample","source_id":"png_parliament",
                  "source_checksum_sha256":"a"*64,"format":"pdf",
                  "segments":[{"reference":"PDF page 7","text":"PART I—PRELIMINARY\n1. Interpretation.\n(1) In this Act, court means a court of competent jurisdiction."}]}
        (self.input / "sample.extraction.json").write_text(json.dumps(record), encoding="utf-8")
    def tearDown(self): self.temp.cleanup()
    def test_build_index_and_search_exact_keywords(self):
        result=build(self.input,self.output); self.assertGreaterEqual(result["indexed_records"],2)
        found=search(self.output/"index.json","court competent")
        self.assertTrue(found); self.assertEqual(found[0]["source_reference"],"PDF page 7")
        self.assertEqual(found[0]["document_id"],"sample-act")
        self.assertEqual(found[0]["source_checksum_sha256"],"a"*64)
        schema=json.loads((ROOT/"schemas"/"legal-search-index.schema.json").read_text())
        validate(json.loads((self.output/"index.json").read_text()), schema)
    def test_all_terms_default_and_any_terms_option(self):
        build(self.input,self.output)
        self.assertEqual(search(self.output/"index.json","court nonexistent","all"),[])
        self.assertTrue(search(self.output/"index.json","court nonexistent","any"))
    def test_empty_query_rejected(self):
        build(self.input,self.output)
        with self.assertRaisesRegex(ValueError,"at least one"): search(self.output/"index.json","   ")
    def test_matching_uses_token_boundaries(self):
        build(self.input,self.output)
        self.assertEqual(search(self.output/"index.json","compet"), [])
    def test_bad_checksum_rejected(self):
        path=next(self.input.glob("*.json")); data=json.loads(path.read_text()); data["source_checksum_sha256"]="bad"; path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"checksum"): build(self.input,self.output)

if __name__ == "__main__": unittest.main()
