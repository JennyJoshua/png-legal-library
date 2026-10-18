#!/usr/bin/env python3
"""Validate PNG Legal Library registers, catalogue, and review queue."""

import json
import re
import sys
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent

DOCUMENT_REGISTER = ROOT / "data" / "documents.json"
DOCUMENT_SCHEMA = ROOT / "schemas" / "document.schema.json"

RESOURCE_REGISTER = ROOT / "data" / "legal-resources.json"
RESOURCE_SCHEMA = ROOT / "schemas" / "legal-resources.schema.json"

REVIEW_QUEUE = ROOT / "data" / "legal-resource-review-queue.json"
REVIEW_QUEUE_SCHEMA = (
    ROOT / "schemas" / "legal-resource-review-queue.schema.json"
)

CANDIDATE_ID_PATTERN = re.compile(r"^[a-f0-9]{16}$")


def load_json(path):
    """Load JSON and report readable errors."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise ValueError(
            f"Required file not found: {path.relative_to(ROOT)}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path.relative_to(ROOT)}: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def valid_date(value):
    """Check an ISO YYYY-MM-DD date."""
    if not isinstance(value, str):
        return False

    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def schema_errors(data, schema, label):
    """Return JSON Schema validation errors."""
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    errors = []

    for error in sorted(
        validator.iter_errors(data),
        key=lambda item: list(map(str, item.absolute_path)),
    ):
        field = ".".join(str(part) for part in error.absolute_path)
        location = f"{label}.{field}" if field else label
        errors.append(f"{location}: {error.message}")

    return errors


def validate_documents(register, schema):
    """Validate the existing document register."""
    errors = []

    if not isinstance(register, dict):
        return ["Document register root must be a JSON object."], 0

    errors.extend(schema_errors(register, schema, "documents"))

    documents = register.get("documents")

    if not isinstance(documents, list):
        errors.append("'documents' must be a JSON array.")
        return errors, 0

    seen_ids = set()

    for index, document in enumerate(documents):
        if not isinstance(document, dict):
            errors.append(
                f"documents.documents[{index}] must be a JSON object."
            )
            continue

        document_id = document.get("document_id")

        if document_id:
            if document_id in seen_ids:
                errors.append(
                    f"Duplicate document_id: {document_id}"
                )
            seen_ids.add(document_id)

        verification_status = document.get("verification_status")
        legal_status = document.get("legal_status")

        if (
            legal_status == "in_force"
            and verification_status != "verified"
        ):
            errors.append(
                f"Document {document_id or index}: "
                "'in_force' requires verification_status 'verified'."
            )

        if verification_status == "verified":
            last_verified_date = document.get("last_verified_date")
            evidence = document.get("legal_status_evidence")

            if not valid_date(last_verified_date):
                errors.append(
                    f"Document {document_id or index}: "
                    "verified records require a valid "
                    "last_verified_date (YYYY-MM-DD)."
                )

            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(
                    f"Document {document_id or index}: "
                    "verified records require legal_status_evidence."
                )

    return errors, len(documents)


def validate_resources(register, schema):
    """Validate the legal resources catalogue."""
    errors = []

    if not isinstance(register, dict):
        return ["Legal resources root must be a JSON object."], 0

    errors.extend(schema_errors(register, schema, "legal_resources"))

    resources = register.get("resources")

    if not isinstance(resources, list):
        errors.append("'resources' must be a JSON array.")
        return errors, 0

    seen_ids = set()

    for index, resource in enumerate(resources):
        if not isinstance(resource, dict):
            errors.append(
                f"legal_resources.resources[{index}] "
                "must be a JSON object."
            )
            continue

        resource_id = resource.get("resource_id")

        if resource_id:
            if resource_id in seen_ids:
                errors.append(
                    f"Duplicate resource_id: {resource_id}"
                )
            seen_ids.add(resource_id)

        if resource.get("legal_status") == "in_force":
            evidence = resource.get("legal_status_evidence")

            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(
                    f"Resource {resource_id or index}: "
                    "'in_force' requires legal_status_evidence."
                )

    return errors, len(resources)


def validate_review_queue(queue, schema):
    """Validate the human-review queue."""
    errors = []

    if not isinstance(queue, dict):
        return ["Review queue root must be a JSON object."], 0

    errors.extend(schema_errors(queue, schema, "review_queue"))

    candidates = queue.get("candidates")

    if not isinstance(candidates, list):
        errors.append("'candidates' must be a JSON array.")
        return errors, 0

    seen_ids = set()

    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(
                f"review_queue.candidates[{index}] "
                "must be a JSON object."
            )
            continue

        candidate_id = candidate.get("candidate_id")
        review_status = candidate.get("review_status")
        legal_status = candidate.get("legal_status")

        if candidate_id:
            if not CANDIDATE_ID_PATTERN.fullmatch(candidate_id):
                errors.append(
                    f"Candidate at index {index}: candidate_id "
                    "must contain exactly 16 lowercase hexadecimal "
                    "characters."
                )

            if candidate_id in seen_ids:
                errors.append(
                    f"Duplicate candidate_id: {candidate_id}"
                )

            seen_ids.add(candidate_id)

        if review_status == "approved_for_catalogue":
            required_fields = (
                "resource_type",
                "classification",
                "reviewed_by",
                "reviewed_date",
            )

            for field in required_fields:
                value = candidate.get(field)

                if not isinstance(value, str) or not value.strip():
                    errors.append(
                        f"Candidate {candidate_id or index}: "
                        f"approved records require '{field}'."
                    )

            if not valid_date(candidate.get("reviewed_date")):
                errors.append(
                    f"Candidate {candidate_id or index}: "
                    "reviewed_date must be a valid YYYY-MM-DD date."
                )

        if legal_status == "in_force":
            evidence = candidate.get("legal_status_evidence")

            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(
                    f"Candidate {candidate_id or index}: "
                    "'in_force' requires legal_status_evidence."
                )

        if review_status == "duplicate":
            duplicate_of = candidate.get("duplicate_of")

            if not isinstance(duplicate_of, str) or not duplicate_of.strip():
                errors.append(
                    f"Candidate {candidate_id or index}: "
                    "duplicate records require duplicate_of."
                )

    return errors, len(candidates)


def main():
    """Run all validation checks."""
    all_errors = []

    try:
        document_register = load_json(DOCUMENT_REGISTER)
        document_schema = load_json(DOCUMENT_SCHEMA)

        resource_register = load_json(RESOURCE_REGISTER)
        resource_schema = load_json(RESOURCE_SCHEMA)

        review_queue = load_json(REVIEW_QUEUE)
        review_queue_schema = load_json(REVIEW_QUEUE_SCHEMA)

        document_errors, document_count = validate_documents(
            document_register,
            document_schema,
        )

        resource_errors, resource_count = validate_resources(
            resource_register,
            resource_schema,
        )

        queue_errors, candidate_count = validate_review_queue(
            review_queue,
            review_queue_schema,
        )

        all_errors.extend(document_errors)
        all_errors.extend(resource_errors)
        all_errors.extend(queue_errors)

    except ValueError as exc:
        print(f"VALIDATION ERROR: {exc}")
        return 1

    if all_errors:
        print("LEGAL LIBRARY VALIDATION FAILED")
        print()

        for error in all_errors:
            print(f"ERROR: {error}")

        print()
        print(f"Total errors: {len(all_errors)}")
        return 1

    print("LEGAL LIBRARY VALIDATION PASSED")
    print(f"Document register: {document_count} record(s).")
    print(f"Legal resources catalogue: {resource_count} resource(s).")
    print(f"Legal resource review queue: {candidate_count} candidate(s).")
    print("All three JSON structures passed schema validation.")
    print("Metadata consistency checks passed.")
    print(
        "Reminder: automated validation does not establish legal "
        "authenticity, current legal status, or redistribution rights."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
