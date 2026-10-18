#!/usr/bin/env python3
"""Safely merge discovery results into the PNG legal-resource review queue.

This script preserves human decisions. Discovery never establishes legal
authenticity, current legal status, or permission to redistribute materials.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DISCOVERY_REPORT = (
    ROOT / "reports" / "discovered-source-candidates.json"
)

REVIEW_QUEUE = (
    ROOT / "data" / "legal-resource-review-queue.json"
)


def load_json(path):
    """Read JSON and report useful errors."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(
            f"Required file not found: {path.relative_to(ROOT)}"
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path.relative_to(ROOT)}: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )


def validate_queue_structure(queue):
    """Refuse to overwrite a malformed review queue."""
    if not isinstance(queue, dict):
        raise ValueError("Review queue root must be a JSON object.")

    if queue.get("queue_version") != "1.0":
        raise ValueError("Review queue queue_version must be 1.0.")

    if queue.get("jurisdiction") != "Papua New Guinea":
        raise ValueError(
            "Review queue jurisdiction must be Papua New Guinea."
        )

    if not isinstance(queue.get("candidates"), list):
        raise ValueError(
            "Review queue must contain a candidates array."
        )

    policy = queue.get("review_policy")

    if not isinstance(policy, dict):
        raise ValueError("Review queue review_policy must be an object.")

    required_safeguards = {
        "automatic_approval": False,
        "automatic_legal_status_changes": False,
        "automatic_redistribution_approval": False,
        "require_human_review": True,
        "preserve_source_url": True,
        "protect_personal_information": True,
    }

    for field, expected in required_safeguards.items():
        if policy.get(field) is not expected:
            raise ValueError(
                f"Review queue safety setting '{field}' "
                f"must be {expected}."
            )


def validate_discovery_report(report):
    """Check the minimum expected discovery-report structure."""
    if not isinstance(report, dict):
        raise ValueError("Discovery report root must be an object.")

    sources = report.get("sources")

    if not isinstance(sources, list):
        raise ValueError(
            "Discovery report must contain a sources array."
        )

    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(
                f"Discovery report source {index} must be an object."
            )

        candidates = source.get("candidates", [])

        if not isinstance(candidates, list):
            raise ValueError(
                f"Discovery report source {index} candidates "
                "must be an array."
            )

        for candidate_index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                raise ValueError(
                    f"Source {index}, candidate {candidate_index} "
                    "must be an object."
                )

            candidate_id = candidate.get("candidate_id")
            url = candidate.get("url")

            if (
                not isinstance(candidate_id, str)
                or len(candidate_id) != 16
                or any(
                    char not in "0123456789abcdef"
                    for char in candidate_id
                )
            ):
                raise ValueError(
                    f"Source {index}, candidate {candidate_index} "
                    "has an invalid candidate_id."
                )

            if (
                not isinstance(url, str)
                or not url.startswith(("https://", "http://"))
            ):
                raise ValueError(
                    f"Source {index}, candidate {candidate_index} "
                    "has an invalid URL."
                )


def merge_candidates(report, queue):
    """Add candidates and refresh discovery metadata without approval."""
    candidates = queue["candidates"]
    by_id = {}

    for index, existing in enumerate(candidates):
        if not isinstance(existing, dict):
            raise ValueError(
                f"Existing queue candidate {index} must be an object."
            )

        candidate_id = existing.get("candidate_id")

        if not isinstance(candidate_id, str) or not candidate_id:
            raise ValueError(
                f"Existing queue candidate {index} has no candidate_id."
            )

        if candidate_id in by_id:
            raise ValueError(
                f"Duplicate candidate_id already in queue: {candidate_id}"
            )

        by_id[candidate_id] = existing

    original_candidates = json.dumps(
        candidates,
        sort_keys=True,
        ensure_ascii=False,
    )

    discovered_count = 0
    new_count = 0
    refreshed_count = 0
    seen_this_run = set()

    # These are observations, not human review decisions.
    refresh_fields = (
        "url",
        "final_url",
        "title",
        "available_date",
        "discovery_method",
        "candidate_type",
        "technical_access",
        "http_status",
        "access_error",
    )

    for source in report["sources"]:
        source_metadata = {
            "source_id": source.get("source_id"),
            "source_name": source.get("source_name"),
            "source_url": source.get("source_url"),
            "source_type": source.get("source_type"),
            "source_review_status": source.get(
                "source_review_status"
            ),
            "jurisdiction": "Papua New Guinea",
        }

        for discovered in source.get("candidates", []):
            discovered_count += 1
            candidate_id = discovered["candidate_id"]

            existing = by_id.get(candidate_id)

            if existing is None:
                new_candidate = {
                    "candidate_id": candidate_id,
                    "url": discovered["url"],
                    "final_url": discovered.get("final_url"),
                    "title": discovered.get("title"),
                    "available_date": discovered.get(
                        "available_date"
                    ),
                    "discovery_method": discovered.get(
                        "discovery_method"
                    ),
                    "candidate_type": discovered.get(
                        "candidate_type",
                        "legal_related_page_unclassified",
                    ),
                    **source_metadata,
                    "technical_access": discovered.get(
                        "technical_access", "not_checked"
                    ),
                    "http_status": discovered.get("http_status"),
                    "access_error": discovered.get("access_error"),
                    "review_status": "pending_review",
                    "legal_status": "status_unknown",
                    "legal_status_evidence": None,
                    "redistribution_permission": "unknown",
                }

                candidates.append(new_candidate)
                by_id[candidate_id] = new_candidate
                seen_this_run.add(candidate_id)
                new_count += 1
                continue

            # Preserve the original source attribution if this URL appears
            # under multiple sources during the same discovery run.
            if candidate_id in seen_this_run:
                continue

            seen_this_run.add(candidate_id)
            refreshed = False

            for field in refresh_fields:
                value = discovered.get(field)

                # Do not erase useful metadata because a later inspection
                # could not retrieve a title, date, or final URL.
                if (
                    field in ("final_url", "title", "available_date")
                    and value is None
                ):
                    continue

                if existing.get(field) != value:
                    existing[field] = value
                    refreshed = True

            # Populate missing source details, but do not silently replace
            # the provenance already recorded for an existing candidate.
            for field, value in source_metadata.items():
                if field not in existing and value is not None:
                    existing[field] = value
                    refreshed = True

            if refreshed:
                refreshed_count += 1

    updated_candidates = json.dumps(
        candidates,
        sort_keys=True,
        ensure_ascii=False,
    )

    changed = original_candidates != updated_candidates

    if changed:
        queue["last_updated"] = (
            datetime.now(timezone.utc).date().isoformat()
        )

        temporary_path = REVIEW_QUEUE.with_suffix(".json.tmp")

        temporary_path.write_text(
            json.dumps(queue, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        temporary_path.replace(REVIEW_QUEUE)

    print("REVIEW QUEUE MERGE COMPLETED")
    print(f"Discovery results processed: {discovered_count}")
    print(f"New candidates added: {new_count}")
    print(f"Existing candidates refreshed: {refreshed_count}")
    print(f"Total candidates in queue: {len(candidates)}")
    print(f"Queue file changed: {'yes' if changed else 'no'}")
    print()
    print("Safety checks:")
    print("- New candidates remain pending human review.")
    print("- Legal status is not automatically approved or changed.")
    print("- Redistribution permission is not automatically approved.")
    print("- Existing review decisions are preserved.")

    return changed


def main():
    try:
        report = load_json(DISCOVERY_REPORT)
        queue = load_json(REVIEW_QUEUE)

        validate_discovery_report(report)
        validate_queue_structure(queue)

        merge_candidates(report, queue)

    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
