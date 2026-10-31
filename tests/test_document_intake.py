import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("intake_document", ROOT / "scripts" / "intake_document.py")
intake = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(intake)

class DocumentIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.register_path = self.base / "documents.json"
        self.history_path = self.base / "versions.json"
        self.sources_path = self.base / "sources.yml"
        self.register_path.write_text(json.dumps({"schema_version": 1, "jurisdiction": "Papua New Guinea", "documents": []}))
        self.history_path.write_text(json.dumps({"history_version": "1.0", "jurisdiction": "Papua New Guinea", "versions": []}))
        self.sources_path.write_text("sources:\n  - source_id: png_parliament\n    url: https://parliament.gov.pg/\n")
        self.file = self.base / "sample.pdf"
        self.file.write_bytes(b"%PDF-1.4\nfirst-version")
        self.patches = [
            patch.object(intake, "ROOT", self.base),
            patch.object(intake, "REGISTER", self.register_path),
            patch.object(intake, "HISTORY", self.history_path),
            patch.object(intake, "SOURCE_REGISTRY", self.sources_path),
        ]
        for item in self.patches: item.start()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()
        self.temp.cleanup()

    def args(self, permission="unknown"):
        return intake.parse_args([
            "--file", str(self.file), "--document-id", "sample-act",
            "--title", "Sample Act", "--document-type", "act",
            "--source-id", "png_parliament",
            "--source-url", "https://parliament.gov.pg/legislation/sample-act",
            "--redistribution-permission", permission
        ])

    def load(self, path):
        return json.loads(path.read_text())

    def test_new_intake_creates_pending_record_and_checksum(self):
        result = intake.intake(self.args())
        self.assertEqual(result["result"], "recorded")
        doc = self.load(self.register_path)["documents"][0]
        self.assertEqual(doc["verification_status"], "pending_review")
        self.assertEqual(doc["legal_status"], "status_unknown")
        self.assertIsNone(doc["file_path"])
        self.assertEqual(doc["checksum_sha256"], result["checksum_sha256"])
        self.assertFalse(result["archived"])

    def test_same_file_is_idempotent(self):
        first = intake.intake(self.args())
        second = intake.intake(self.args())
        self.assertEqual(second["result"], "already_recorded")
        self.assertEqual(len(self.load(self.history_path)["versions"]), 1)
        self.assertEqual(first["version_id"], second["version_id"])

    def test_changed_file_appends_linked_version(self):
        first = intake.intake(self.args())
        self.file.write_bytes(b"%PDF-1.4\nsecond-version")
        second = intake.intake(self.args())
        versions = self.load(self.history_path)["versions"]
        self.assertEqual(second["version_number"], 2)
        self.assertEqual(versions[1]["previous_version_id"], first["version_id"])
        self.assertEqual(len(versions), 2)

    def test_unknown_permission_never_archives_copy(self):
        result = intake.intake(self.args("unknown"))
        self.assertFalse(result["archived"])
        self.assertFalse((self.base / ".private").exists())

    def test_explicit_permitted_archives_private_copy(self):
        result = intake.intake(self.args("permitted"))
        self.assertTrue(result["archived"])
        archived_path = self.load(self.history_path)["versions"][0]["archived_path"]
        self.assertTrue((self.base / archived_path).is_file())

    def test_existing_reviewer_decisions_are_preserved(self):
        intake.intake(self.args())
        data = self.load(self.register_path)
        data["documents"][0]["verification_status"] = "verified"
        data["documents"][0]["legal_status"] = "in_force"
        data["documents"][0]["legal_status_evidence"] = "review evidence"
        data["documents"][0]["reviewer_notes"] = "Do not overwrite this note"
        self.register_path.write_text(json.dumps(data))
        self.file.write_bytes(b"%PDF-1.4\nnew-version")
        intake.intake(self.args())
        doc = self.load(self.register_path)["documents"][0]
        self.assertEqual(doc["verification_status"], "verified")
        self.assertEqual(doc["legal_status"], "in_force")
        self.assertEqual(doc["legal_status_evidence"], "review evidence")
        self.assertEqual(doc["reviewer_notes"], "Do not overwrite this note")

    def test_unknown_source_rejected(self):
        args = self.args()
        args.source_id = "unregistered"
        with self.assertRaisesRegex(ValueError, "Unknown source-id"):
            intake.intake(args)

    def test_non_https_source_rejected(self):
        args = self.args()
        args.source_url = "http://parliament.gov.pg/file.pdf"
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            intake.intake(args)

    def test_symlink_rejected(self):
        link = self.base / "linked.pdf"
        link.symlink_to(self.file)
        args = self.args()
        args.file = str(link)
        with self.assertRaisesRegex(ValueError, "symlink"):
            intake.intake(args)

if __name__ == "__main__":
    unittest.main()