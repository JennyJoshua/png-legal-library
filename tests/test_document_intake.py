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
VALIDATOR_SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "validate_documents.py")
validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validator)

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
        self.assertEqual(doc["current_version_id"], result["version_id"])
        version = self.load(self.history_path)["versions"][0]
        self.assertEqual(version["verification_status"], "pending_review")
        self.assertIsNone(version["verification_evidence"])
        self.assertIsNone(version["verified_at"])
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
        self.assertEqual(versions[1]["verification_status"], "pending_review")
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

    def test_new_version_resets_current_verification_but_preserves_notes(self):
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
        self.assertEqual(doc["verification_status"], "pending_review")
        self.assertIsNone(doc["last_verified_date"])
        self.assertEqual(doc["legal_status"], "status_unknown")
        self.assertIsNone(doc["legal_status_evidence"])
        self.assertEqual(doc["reviewer_notes"], "Do not overwrite this note")
        versions = self.load(self.history_path)["versions"]
        self.assertEqual(doc["current_version_id"], versions[-1]["version_id"])
        self.assertEqual(versions[-1]["verification_status"], "pending_review")

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

    def test_lookalike_hostname_is_rejected(self):
        args = self.args()
        args.source_url = "https://parliament.gov.pg.attacker.example/file.pdf"
        with self.assertRaisesRegex(ValueError, "exact registered HTTPS host"):
            intake.intake(args)

    def test_credentials_in_source_url_are_rejected(self):
        args = self.args()
        args.source_url = "https://user:password@parliament.gov.pg/file.pdf"
        with self.assertRaisesRegex(ValueError, "credential-free HTTPS"):
            intake.intake(args)

    def test_registered_path_prefix_boundary_is_enforced(self):
        args = self.args()
        args.source_url = "https://parliament.gov.pg.evil.example/file.pdf"
        with self.assertRaisesRegex(ValueError, "exact registered HTTPS host"):
            intake.intake(args)

    def test_symlink_rejected(self):
        link = self.base / "linked.pdf"
        link.symlink_to(self.file)
        args = self.args()
        args.file = str(link)
        with self.assertRaisesRegex(ValueError, "symlink"):
            intake.intake(args)


class DocumentVersionValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = validator.load_json(ROOT / "schemas" / "document-versions.schema.json")

    def version(self, number, version_id, checksum, previous=None, document_id="sample-act"):
        return {
            "version_id": version_id, "document_id": document_id,
            "version_number": number, "checksum_sha256": checksum * 64,
            "file_name": "sample.pdf", "file_size_bytes": 20,
            "media_type": "application/pdf", "source_url": "https://parliament.gov.pg/sample",
            "source_id": "png_parliament", "observed_at": "2026-10-31T00:00:00Z",
            "previous_version_id": previous, "review_status": "pending_review",
            "redistribution_permission": "unknown", "archived_path": None
        }

    def test_valid_sequential_history_passes(self):
        first = self.version(1, "1111111111111111", "a", None)
        second = self.version(2, "2222222222222222", "b", first["version_id"])
        history = {"history_version": "1.0", "jurisdiction": "Papua New Guinea", "versions": [first, second]}
        register = {"documents": [{"document_id": "sample-act"}]}
        errors, count = validator.validate_document_versions(history, self.schema, register)
        self.assertEqual(errors, [])
        self.assertEqual(count, 2)

    def test_broken_previous_version_link_is_rejected(self):
        first = self.version(1, "1111111111111111", "a", None)
        second = self.version(2, "2222222222222222", "b", "3333333333333333")
        history = {"history_version": "1.0", "jurisdiction": "Papua New Guinea", "versions": [first, second]}
        errors, _ = validator.validate_document_versions(history, self.schema, {"documents": [{"document_id": "sample-act"}]})
        self.assertTrue(any("broken previous_version_id" in error for error in errors))

    def test_version_must_reference_existing_document(self):
        version = self.version(1, "1111111111111111", "a")
        history = {"history_version": "1.0", "jurisdiction": "Papua New Guinea", "versions": [version]}
        errors, _ = validator.validate_document_versions(history, self.schema, {"documents": []})
        self.assertTrue(any("unknown document_id" in error for error in errors))

    def test_duplicate_hash_is_rejected(self):
        first = self.version(1, "1111111111111111", "a", None)
        second = self.version(2, "2222222222222222", "a", first["version_id"])
        history = {"history_version": "1.0", "jurisdiction": "Papua New Guinea", "versions": [first, second]}
        errors, _ = validator.validate_document_versions(history, self.schema, {"documents": [{"document_id": "sample-act"}]})
        self.assertTrue(any("Duplicate checksum" in error for error in errors))


if __name__ == "__main__":
    unittest.main()