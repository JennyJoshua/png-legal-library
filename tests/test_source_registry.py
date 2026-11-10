import importlib.util
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validator", ROOT / "scripts" / "validate_documents.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

class SourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = validator.load_yaml(validator.SOURCE_REGISTRY)
        cls.schema = validator.load_json(validator.SOURCE_REGISTRY_SCHEMA)
        cls.queue = validator.load_json(validator.REVIEW_QUEUE)

    def test_existing_registry_and_queue_provenance_pass(self):
        errors, count = validator.validate_source_registry(self.registry, self.schema, self.queue)
        self.assertEqual(errors, [])
        self.assertEqual(count, len(self.registry["sources"]))

    def test_duplicate_source_ids_are_rejected(self):
        registry = dict(self.registry)
        registry["sources"] = list(self.registry["sources"]) + [dict(self.registry["sources"][0])]
        errors, _ = validator.validate_source_registry(registry, self.schema, {"candidates": []})
        self.assertTrue(any("Duplicate source_id" in error for error in errors))

    def test_unknown_candidate_source_is_rejected(self):
        queue = {"candidates": [{"candidate_id": "0123456789abcdef", "source_id": "missing_source"}]}
        errors, _ = validator.validate_source_registry(self.registry, self.schema, queue)
        self.assertTrue(any("unknown source_id" in error for error in errors))

    def test_registry_requires_https_source_urls(self):
        registry = dict(self.registry)
        registry["sources"] = [dict(item) for item in self.registry["sources"]]
        registry["sources"][0]["url"] = "http://example.org"
        errors, _ = validator.validate_source_registry(registry, self.schema, {"candidates": []})
        self.assertTrue(any("https://" in error for error in errors))

    def test_automatic_legal_and_redistribution_approval_remain_disabled(self):
        registry = dict(self.registry)
        registry["discovery_rules"] = dict(self.registry["discovery_rules"])
        registry["discovery_rules"]["automatic_legal_status_changes"] = True
        errors, _ = validator.validate_source_registry(registry, self.schema, {"candidates": []})
        self.assertTrue(errors)

    def test_unknown_source_observation_is_rejected(self):
        queue = {
            "candidates": [{
                "candidate_id": "0123456789abcdef",
                "source_id": "png_parliament",
                "source_observations": [
                    {"source_id": "missing_secondary_source"}
                ]
            }]
        }
        errors, _ = validator.validate_source_registry(self.registry, self.schema, queue)
        self.assertTrue(any("source observation references unknown source_id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
