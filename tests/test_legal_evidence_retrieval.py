import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from retrieve_legal_evidence import retrieve
import retrieve_legal_evidence as retrieval_module

class EvidenceRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.index = Path(self.temp.name) / "index.json"
        self.record = {
            "node_id": "sample-1", "document_id": "sample-act",
            "version_id": "1234567890abcdef", "document_title": "Sample Act",
            "source_id": "png_parliament", "source_url": "https://example.gov.pg/sample",
            "source_checksum_sha256": "a" * 64, "kind": "section",
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

    def test_returns_traceable_citation_and_exact_provenance(self):
        result = retrieve(self.index, "court competent")
        self.assertEqual(result["result_count"], 1)
        hit = result["results"][0]
        self.assertEqual(hit["document_id"], "sample-act")
        self.assertEqual(hit["version_id"], "1234567890abcdef")
        self.assertEqual(hit["source_checksum_sha256"], "a" * 64)
        self.assertEqual(hit["location"]["page_number"], 7)
        self.assertTrue(hit["citation_id"].startswith("pnglaw:"))

    def test_missing_provenance_is_rejected_not_cited(self):
        bad = dict(self.record)
        bad.pop("source_checksum_sha256")
        self.write([bad])
        result = retrieve(self.index, "court")
        self.assertEqual(result["result_count"], 0)
        self.assertEqual(result["rejected_untraceable_records"], 1)

    def test_bad_checksum_is_rejected(self):
        bad = dict(self.record, source_checksum_sha256="not-a-hash")
        self.write([bad])
        self.assertEqual(retrieve(self.index, "court")["result_count"], 0)

    def test_all_terms_default_and_any_mode(self):
        self.assertEqual(retrieve(self.index, "court missing")["result_count"], 0)
        self.assertEqual(retrieve(self.index, "court missing", "any")["result_count"], 1)

    def test_empty_query_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            retrieve(self.index, "  ")

    def test_limit_validation(self):
        with self.assertRaisesRegex(ValueError, "limit"):
            retrieve(self.index, "court", limit=101)

    def test_index_byte_limit_is_enforced_before_json_parse(self):
        self.index.write_bytes(b" " * 33)
        with patch.object(retrieval_module, "MAX_INDEX_BYTES", 32):
            with self.assertRaisesRegex(ValueError, "byte limit"):
                retrieve(self.index, "court")

    def test_index_record_count_limit_is_enforced(self):
        self.write([self.record, self.record])
        with patch.object(retrieval_module, "MAX_INDEX_RECORDS", 1):
            with self.assertRaisesRegex(ValueError, "record limit"):
                retrieve(self.index, "court")

    def test_non_object_index_root_is_rejected(self):
        self.index.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "root"):
            retrieve(self.index, "court")

    def test_malformed_json_is_reported_as_invalid_index(self):
        self.index.write_text("{not-json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "valid UTF-8 JSON"):
            retrieve(self.index, "court")

    def test_repeatable_citation_id(self):
        first = retrieve(self.index, "court")["results"][0]["citation_id"]
        second = retrieve(self.index, "court")["results"][0]["citation_id"]
        self.assertEqual(first, second)

if __name__ == "__main__":
    unittest.main()
