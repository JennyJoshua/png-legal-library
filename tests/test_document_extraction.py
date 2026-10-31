import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pymupdf as fitz
from docx import Document
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("extract_document", ROOT / "scripts" / "extract_document.py")
extractor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extractor)


class DocumentExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.input_dir = self.base / "input"
        self.output_dir = self.base / "output"
        self.input_dir.mkdir()
        self.pdf_path = self.input_dir / "sample.pdf"
        with fitz.open() as pdf:
            page = pdf.new_page()
            page.insert_text((72, 72), "Papua New Guinea Example Act 2026")
            page.insert_text((72, 100), "Section 1. This is a test provision.")
            pdf.save(self.pdf_path)
        self.docx_path = self.input_dir / "sample.docx"
        doc = Document()
        doc.add_heading("Part 1 - Preliminary", level=1)
        doc.add_paragraph("Section 1. This Act is a sample.")
        table = doc.add_table(rows=1, cols=2)
        table.rows[0].cells[0].text = "Section"
        table.rows[0].cells[1].text = "Subject"
        doc.save(self.docx_path)
        self.digest = hashlib.sha256(self.pdf_path.read_bytes()).hexdigest()
        self.register = self.base / "documents.json"
        self.history = self.base / "versions.json"
        self.register.write_text(json.dumps({"documents": [{"document_id": "sample-act", "title": "Sample Act 2026"}]}))
        self.history.write_text(json.dumps({"versions": [{
            "version_id": "1234567890abcdef", "document_id": "sample-act",
            "checksum_sha256": self.digest, "source_url": "https://parliament.gov.pg/sample",
            "source_id": "png_parliament", "media_type": "application/pdf"
        }]}))
        self.patches = [
            patch.object(extractor, "REGISTER", self.register),
            patch.object(extractor, "HISTORY", self.history),
        ]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        self.temp.cleanup()

    def args(self, path=None):
        return extractor.parse_args([
            "--file", str(path or self.pdf_path),
            "--document-id", "sample-act", "--version-id", "1234567890abcdef",
            "--output-dir", str(self.output_dir)
        ])

    def test_pdf_page_extraction_preserves_page_references(self):
        segments, info = extractor.extract_pdf(self.pdf_path)
        self.assertEqual(info["page_count"], 1)
        self.assertIn("PDF page 1", segments[0]["reference"])
        self.assertIn("Section 1", segments[0]["text"])

    def test_pdf_cli_writes_json_and_text_with_provenance(self):
        result = extractor.run(self.args())
        self.assertEqual(result["result"], "extracted")
        data = json.loads(Path(result["json_output"]).read_text())
        self.assertEqual(data["document_id"], "sample-act")
        self.assertEqual(data["version_id"], "1234567890abcdef")
        self.assertEqual(data["source_checksum_sha256"], self.digest)
        self.assertIn("[PDF page 1]", Path(result["text_output"]).read_text())
        schema = json.loads((ROOT / "schemas" / "extraction-result.schema.json").read_text())
        validate(data, schema)

    def test_docx_extracts_paragraphs_headings_and_tables(self):
        segments, info = extractor.extract_docx(self.docx_path)
        self.assertGreaterEqual(info["paragraph_count"], 2)
        self.assertTrue(any(s.get("heading_context") == "Part 1 - Preliminary" for s in segments))
        self.assertTrue(any("Section | Subject" in s["text"] for s in segments))
        self.assertTrue(all(s["reference"].startswith("DOCX") for s in segments))

    def test_docx_cli_uses_matching_registered_checksum(self):
        digest = hashlib.sha256(self.docx_path.read_bytes()).hexdigest()
        history = json.loads(self.history.read_text())
        history["versions"][0]["checksum_sha256"] = digest
        history["versions"][0]["media_type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        self.history.write_text(json.dumps(history))
        result = extractor.run(self.args(self.docx_path))
        self.assertEqual(result["result"], "extracted")
        data = json.loads(Path(result["json_output"]).read_text())
        self.assertEqual(data["format"], "docx")

    def test_checksum_mismatch_is_rejected(self):
        self.pdf_path.write_bytes(self.pdf_path.read_bytes() + b"changed")
        with self.assertRaisesRegex(ValueError, "checksum"):
            extractor.run(self.args())

    def test_version_must_belong_to_document(self):
        history = json.loads(self.history.read_text())
        history["versions"][0]["document_id"] = "another-doc"
        self.history.write_text(json.dumps(history))
        with self.assertRaisesRegex(ValueError, "different document"):
            extractor.run(self.args())

    def test_unknown_version_rejected(self):
        args = self.args()
        args.version_id = "ffffffffffffffff"
        with self.assertRaisesRegex(ValueError, "Unknown version"):
            extractor.run(args)

    def test_unknown_document_rejected(self):
        args = self.args()
        args.document_id = "not-in-register"
        with self.assertRaisesRegex(ValueError, "Unknown document"):
            extractor.run(args)

    def test_unsupported_file_extension_rejected(self):
        path = self.input_dir / "sample.txt"
        path.write_text("not a supported document")
        history = json.loads(self.history.read_text())
        history["versions"][0]["checksum_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.history.write_text(json.dumps(history))
        args = self.args(path)
        with self.assertRaisesRegex(ValueError, "Unsupported file type"):
            extractor.run(args)

    def test_symlink_rejected(self):
        link = self.input_dir / "link.pdf"
        link.symlink_to(self.pdf_path)
        with self.assertRaisesRegex(ValueError, "symlink"):
            extractor.run(self.args(link))

    def test_ocr_requires_tesseract_when_page_has_no_text(self):
        blank = self.input_dir / "scanned.pdf"
        with fitz.open() as pdf:
            pdf.new_page()
            pdf.save(blank)
        with patch.object(extractor.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "Tesseract OCR executable"):
                extractor.extract_pdf(blank, use_ocr=True)


    def test_ocr_page_limit_is_enforced(self):
        blank = self.input_dir / "multi.pdf"
        with fitz.open() as pdf:
            pdf.new_page()
            pdf.new_page()
            pdf.save(blank)
        with patch.object(extractor, "MAX_OCR_PAGES", 1):
            with self.assertRaisesRegex(ValueError, "limited to 1 pages"):
                extractor.extract_pdf(blank, use_ocr=True)


if __name__ == "__main__":
    unittest.main()