import importlib.util
import tempfile
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "discovery", ROOT / "scripts" / "discover-legal-sources.py"
)
discovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(discovery)


class DiscoveryReliabilityTests(unittest.TestCase):
    def test_rejects_unsupported_and_credential_urls(self):
        self.assertIsNone(discovery.safe_urljoin("https://example.org", "javascript:alert(1)"))
        self.assertIsNone(discovery.safe_urljoin("https://example.org", "https://user:pass@example.org/private"))

    def test_normalize_removes_tracking_and_fragment(self):
        value = discovery.normalize_url(
            "https://example.org", "https://example.org/laws/act?utm_source=x&id=3#part"
        )
        self.assertEqual(value, "https://example.org/laws/act?id=3")

    def test_normalize_rejects_bad_port(self):
        self.assertIsNone(discovery.normalize_url("https://example.org", "https://example.org:bad/a"))

    def test_sitemap_parser_handles_namespaces(self):
        data = b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.org/act.pdf</loc></url></urlset>'
        self.assertEqual(discovery.parse_sitemap(data), ["https://example.org/act.pdf"])

    def test_sitemap_parser_handles_invalid_xml(self):
        self.assertEqual(discovery.parse_sitemap(b"<broken"), [])

    def test_candidate_classification_is_suggestion(self):
        self.assertEqual(discovery.classify_candidate("https://example.org/constitution.pdf"), "constitution")

    def test_http_errors_are_returned_not_raised(self):
        with patch.object(discovery, "fetch", return_value={
            "ok": False, "status": 403, "error": "Forbidden"
        }):
            result = discovery.inspect_page("https://example.org/private")
        self.assertEqual(result["access_result"], "forbidden")
        self.assertEqual(result["http_status"], 403)

    def test_source_budget_prevents_network_request(self):
        old_deadline = discovery.CURRENT_SOURCE_DEADLINE
        try:
            discovery.CURRENT_SOURCE_DEADLINE = 0
            result = discovery.fetch("https://example.org/")
            self.assertFalse(result["ok"])
            self.assertIn("budget", result["error"].lower())
        finally:
            discovery.CURRENT_SOURCE_DEADLINE = old_deadline

    def test_sitemap_depth_is_bounded(self):
        old_deadline = discovery.CURRENT_SOURCE_DEADLINE
        try:
            discovery.CURRENT_SOURCE_DEADLINE = None
            visited = set()
            found = {}
            with patch.object(discovery, "fetch") as mocked:
                discovery.inspect_sitemap(
                    "https://example.org/sitemap.xml", "example.org",
                    found, visited, depth=discovery.MAX_SITEMAP_DEPTH
                )
                mocked.assert_not_called()
            self.assertEqual(visited, set())
        finally:
            discovery.CURRENT_SOURCE_DEADLINE = old_deadline


    def test_merge_preserves_human_review_fields(self):
        merge_path = ROOT / "scripts" / "merge-discovery-review-queue.py"
        merge_spec = importlib.util.spec_from_file_location("merge_queue", merge_path)
        merge = importlib.util.module_from_spec(merge_spec)
        merge_spec.loader.exec_module(merge)
        existing = {
            "candidate_id": "0123456789abcdef", "url": "https://example.org/act.pdf",
            "review_status": "under_review", "legal_status": "status_unknown",
            "redistribution_permission": "unknown", "reviewer_notes": "Human note must remain",
            "reviewed_by": "reviewer"
        }
        queue = {
            "queue_version": "1.0", "jurisdiction": "Papua New Guinea",
            "candidates": [existing],
            "review_policy": {
                "automatic_approval": False, "automatic_legal_status_changes": False,
                "automatic_redistribution_approval": False, "require_human_review": True,
                "preserve_source_url": True, "protect_personal_information": True
            }
        }
        report = {"sources": [{
            "source_id": "source1", "source_name": "Test source",
            "source_url": "https://example.org/", "source_type": "official_government",
            "source_review_status": "candidate",
            "candidates": [{
                "candidate_id": "0123456789abcdef", "url": "https://example.org/act.pdf",
                "title": "Act", "technical_access": "accessible_non_html",
                "review_status": "pending_review"
            }]
        }]}
        with tempfile.TemporaryDirectory() as tmp:
            original_path = merge.REVIEW_QUEUE
            merge.REVIEW_QUEUE = Path(tmp) / "queue.json"
            try:
                merge.REVIEW_QUEUE.write_text(json.dumps(queue), encoding="utf-8")
                merge.merge_candidates(report, queue)
            finally:
                merge.REVIEW_QUEUE = original_path
        candidate = queue["candidates"][0]
        self.assertEqual(candidate["review_status"], "under_review")
        self.assertEqual(candidate["reviewer_notes"], "Human note must remain")
        self.assertEqual(candidate["reviewed_by"], "reviewer")

    def test_new_merge_candidate_defaults_to_pending_and_unknown(self):
        merge_path = ROOT / "scripts" / "merge-discovery-review-queue.py"
        merge_spec = importlib.util.spec_from_file_location("merge_queue_new", merge_path)
        merge = importlib.util.module_from_spec(merge_spec)
        merge_spec.loader.exec_module(merge)
        queue = {
            "queue_version": "1.0", "jurisdiction": "Papua New Guinea",
            "candidates": [],
            "review_policy": {
                "automatic_approval": False, "automatic_legal_status_changes": False,
                "automatic_redistribution_approval": False, "require_human_review": True,
                "preserve_source_url": True, "protect_personal_information": True
            }
        }
        report = {"sources": [{
            "source_id": "source1", "source_name": "Test source",
            "source_url": "https://example.org/", "source_type": "official_government",
            "source_review_status": "candidate",
            "candidates": [{
                "candidate_id": "fedcba9876543210", "url": "https://example.org/law.pdf",
                "technical_access": "not_checked"
            }]
        }]}
        with tempfile.TemporaryDirectory() as tmp:
            original_path = merge.REVIEW_QUEUE
            merge.REVIEW_QUEUE = Path(tmp) / "queue.json"
            try:
                merge.REVIEW_QUEUE.write_text(json.dumps(queue), encoding="utf-8")
                merge.merge_candidates(report, queue)
            finally:
                merge.REVIEW_QUEUE = original_path
        candidate = queue["candidates"][0]
        self.assertEqual(candidate["review_status"], "pending_review")
        self.assertEqual(candidate["legal_status"], "status_unknown")
        self.assertEqual(candidate["redistribution_permission"], "unknown")

    def test_workflow_is_read_only_and_does_not_push_main(self):
        workflow = (ROOT / ".github" / "workflows" / "discover-legal-sources.yml").read_text()
        self.assertIn("contents: read", workflow)
        self.assertNotIn("git push", workflow)
        self.assertIn("upload-artifact", workflow)


    def test_redirect_handler_blocks_cross_host_and_https_downgrade(self):
        from urllib.request import Request
        handler = discovery.SameHostRedirectHandler("https://example.org/start")
        request = Request("https://example.org/start")
        with self.assertRaises(discovery.UnsafeRedirectError):
            handler.redirect_request(
                request, None, 302, "Found", {}, "https://attacker.example/collect"
            )
        with self.assertRaises(discovery.UnsafeRedirectError):
            handler.redirect_request(
                request, None, 302, "Found", {}, "http://example.org/insecure"
            )

    def test_fetch_respects_robots_disallow_without_network_request(self):
        from urllib.robotparser import RobotFileParser
        parser = RobotFileParser()
        parser.parse(["User-agent: *", "Disallow: /private"])
        old_parser = discovery.CURRENT_ROBOTS_PARSER
        old_block = discovery.CURRENT_ROBOTS_BLOCK_ALL
        try:
            discovery.CURRENT_ROBOTS_PARSER = parser
            discovery.CURRENT_ROBOTS_BLOCK_ALL = False
            with patch.object(discovery, "build_opener") as mocked:
                result = discovery.fetch("https://example.org/private/act.pdf")
                mocked.assert_not_called()
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"], "Blocked by robots.txt")
        finally:
            discovery.CURRENT_ROBOTS_PARSER = old_parser
            discovery.CURRENT_ROBOTS_BLOCK_ALL = old_block

    def test_fetch_fails_closed_when_robots_policy_unavailable(self):
        old_parser = discovery.CURRENT_ROBOTS_PARSER
        old_block = discovery.CURRENT_ROBOTS_BLOCK_ALL
        try:
            discovery.CURRENT_ROBOTS_PARSER = None
            discovery.CURRENT_ROBOTS_BLOCK_ALL = True
            with patch.object(discovery, "build_opener") as mocked:
                result = discovery.fetch("https://example.org/law.pdf")
                mocked.assert_not_called()
            self.assertFalse(result["ok"])
            self.assertIn("robots.txt", result["error"])
        finally:
            discovery.CURRENT_ROBOTS_PARSER = old_parser
            discovery.CURRENT_ROBOTS_BLOCK_ALL = old_block


    def test_inspect_page_reports_redirect_blocks_distinctly(self):
        with patch.object(discovery, "fetch", return_value={
            "ok": False, "status": None,
            "error": "Redirect blocked: destination must remain on the original host."
        }):
            result = discovery.inspect_page("https://example.org/legal/act")
        self.assertEqual(result["access_result"], "redirect_blocked")


if __name__ == "__main__":
    unittest.main()
