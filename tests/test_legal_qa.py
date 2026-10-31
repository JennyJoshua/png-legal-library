import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from legal_qa import build_qa_response, format_citation, render_text
from retrieve_legal_evidence import retrieve


class LegalQATests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.index = Path(self.temp.name) / "index.json"
        self.record = {
            "node_id": "n1", "document_id": "sample-act",
            "version_id": "1234567890abcdef", "document_title": "Sample PNG Act",
            "source_id": "png_source", "source_url": "https://example.gov.pg/sample",
            "source_checksum_sha256": "c" * 64, "kind": "section",
            "number": "5", "title": "Interpretation",
            "text": "A court means a court of competent jurisdiction.",
            "source_reference": "PDF page 7", "page_number": 7,
            "paragraph_number": None, "structure_path": [{"kind": "section", "number": "5"}]
        }
        self.write([self.record])
        self.citation = retrieve(self.index, "court competent")["results"][0]["citation_id"]

    def tearDown(self):
        self.temp.cleanup()

    def write(self, records):
        self.index.write_text(json.dumps({"records": records}), encoding="utf-8")

    def fake_model(self, request):
        return {
            "answer": "The supplied passage defines the term court.",
            "claims": [{"text": "A court means a court of competent jurisdiction.",
                        "citation_ids": [self.citation]}],
            "limitations": ["This passage does not establish whether the Act is currently in force."],
            "insufficient_evidence": False
        }

    def test_no_model_shows_sources_but_not_fake_answer(self):
        response = build_qa_response("court competent", self.index)
        self.assertEqual(response["status"], "model_not_configured")
        self.assertEqual(response["claims"], [])
        self.assertEqual(len(response["citations"]), 1)
        self.assertIn("No legal answer", response["answer"])

    def test_no_results_returns_insufficient_evidence(self):
        response = build_qa_response("criminal sentencing", self.index)
        self.assertEqual(response["status"], "insufficient_evidence")
        self.assertTrue(response["follow_up_needed"])
        self.assertEqual(response["citations"], [])

    def test_claims_get_numbered_source_labels(self):
        response = build_qa_response("court competent", self.index, model=self.fake_model)
        self.assertEqual(response["claims"][0]["citation_labels"], ["[1]"])
        self.assertEqual(response["citations"][0]["label"], "[1]")
        self.assertIn("PDF page 7", response["citations"][0]["text"])

    def test_citation_includes_version_checksum_and_url(self):
        response = build_qa_response("court competent", self.index, model=self.fake_model)
        cite = response["citations"][0]
        self.assertEqual(cite["version_id"], self.record["version_id"])
        self.assertEqual(cite["source_checksum_sha256"], "c" * 64)
        self.assertEqual(cite["source_url"], self.record["source_url"])

    def test_text_renderer_prints_claim_and_sources(self):
        response = build_qa_response("court competent", self.index, model=self.fake_model)
        rendered = render_text(response)
        self.assertIn("Evidence-linked claims:", rendered)
        self.assertIn("[1]", rendered)
        self.assertIn("Sources:", rendered)

    def test_citation_formatter_uses_source_fallback(self):
        item = {"document_id": "doc-2", "version_id": "1234567890abcdef",
                "source_checksum_sha256": "d" * 64, "citation_id": "pnglaw:two",
                "location": {"source_reference": "paragraph 9"}}
        cite = format_citation(item, 2)
        self.assertIn("doc-2", cite["text"])
        self.assertIn("paragraph 9", cite["text"])

    def test_no_claims_from_uncited_model_answer(self):
        def bad_model(request):
            return {"answer": "Unsupported statement", "claims": [],
                    "limitations": [], "insufficient_evidence": False}
        with self.assertRaisesRegex(ValueError, "without cited claims"):
            build_qa_response("court competent", self.index, model=bad_model)


if __name__ == "__main__":
    unittest.main()
