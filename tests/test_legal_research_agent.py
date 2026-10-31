import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from legal_research_agent import build_model_request, research, validate_model_answer

class LegalResearchAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.index = Path(self.temp.name) / "index.json"
        self.record = {
            "node_id": "n1", "document_id": "sample-act",
            "version_id": "1234567890abcdef", "document_title": "Sample Act",
            "source_id": "png_source", "source_url": "https://example.gov.pg/sample",
            "source_checksum_sha256": "b" * 64, "kind": "section",
            "number": "5", "title": "Interpretation",
            "text": "A court means a court of competent jurisdiction.",
            "source_reference": "PDF page 7", "page_number": 7,
            "paragraph_number": None, "structure_path": [{"kind": "section", "number": "5"}]
        }
        self.write([self.record])

    def tearDown(self):
        self.temp.cleanup()

    def write(self, records):
        self.index.write_text(json.dumps({"records": records}), encoding="utf-8")

    def test_no_model_does_not_fake_an_answer(self):
        result = research("court competent", self.index)
        self.assertEqual(result["status"], "model_not_configured")
        self.assertIn("No legal answer", result["message"])

    def test_no_matching_evidence_returns_insufficient(self):
        result = research("criminal sentencing", self.index)
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertEqual(result["claims"], [])

    def test_model_request_contains_only_retrieved_evidence(self):
        evidence = {"results": [{"citation_id": "pnglaw:test", "excerpt": "passage"}]}
        request = build_model_request("What is a court?", evidence)
        self.assertIn("ONLY the supplied evidence", request["system"])
        self.assertIn("pnglaw:test", request["user"])

    def test_accepts_answer_with_valid_citation(self):
        evidence = {"results": [{"citation_id": "pnglaw:valid", "document_id": "act"}]}
        result = validate_model_answer({
            "answer": "The passage defines court.",
            "claims": [{"text": "Court means a court of competent jurisdiction.", "citation_ids": ["pnglaw:valid"]}],
            "limitations": [], "insufficient_evidence": False
        }, evidence)
        self.assertEqual(result["citations"][0]["citation_id"], "pnglaw:valid")

    def test_rejects_fabricated_citation(self):
        evidence = {"results": [{"citation_id": "pnglaw:valid"}]}
        with self.assertRaisesRegex(ValueError, "not present"):
            validate_model_answer({
                "answer": "Answer", "claims": [{"text": "Claim", "citation_ids": ["pnglaw:fake"]}],
                "limitations": [], "insufficient_evidence": False
            }, evidence)

    def test_rejects_uncited_claim(self):
        with self.assertRaisesRegex(ValueError, "no supporting citation"):
            validate_model_answer({
                "answer": "Answer", "claims": [{"text": "Claim", "citation_ids": []}],
                "limitations": [], "insufficient_evidence": False
            }, {"results": []})

    def test_rejects_missing_claims_array(self):
        with self.assertRaisesRegex(ValueError, "claims must be an array"):
            validate_model_answer({"answer": "Answer"}, {"results": []})

    def test_rejects_empty_answer(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            validate_model_answer({"answer": " ", "claims": [], "limitations": [], "insufficient_evidence": True}, {"results": []})

    def test_model_adapter_is_called_and_answer_is_checked(self):
        def fake_model(request):
            self.assertIn("court competent", request["user"])
            return {
                "answer": "The supplied passage defines court.",
                "claims": [{"text": "Court means a court of competent jurisdiction.", "citation_ids": ["pnglaw:" + __import__("hashlib").sha256(("sample-act|1234567890abcdef|" + "b"*64 + "|PDF page 7|" + str([{"kind":"section","number":"5"}]) + "|" + self.record["text"]).encode()).hexdigest()[:20]]}],
                "limitations": ["This does not establish current legal status."],
                "insufficient_evidence": False
            }
        # Build citation via the same retrieval function to avoid hard-coding identity internals.
        from retrieve_legal_evidence import retrieve
        evidence = retrieve(self.index, "court competent")
        citation = evidence["results"][0]["citation_id"]
        def valid_model(request):
            return {"answer": "The supplied passage defines court.",
                    "claims": [{"text": "Court means a court of competent jurisdiction.", "citation_ids": [citation]}],
                    "limitations": [], "insufficient_evidence": False}
        result = research("court competent", self.index, model=valid_model)
        self.assertEqual(result["status"], "answer_generated")
        self.assertEqual(result["claims"][0]["citation_ids"], [citation])

if __name__ == "__main__":
    unittest.main()
