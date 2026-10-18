#!/usr/bin/env python3
"""Validate PNG Legal Library document records."""

import json
import re
import sys
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "data" / "documents.json"
SCHEMA = ROOT / "schemas" / "document.schema.json"

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def load_json(path):
    """Load JSON and report readable errors."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"Required file not found: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {path.relative_to(ROOT)}: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )


def valid_date(value):
    """Check an ISO YYYY-MM-DD date."""
    if not isinstance(value, str):
        return False

    try:
        parsed = date.fromisoformat(value)
        return parsed.isoformat() == value
    except ValueError:
        return False


def main():
    errors = []

    try:
        register = load_json(REGISTER)
        schema = load_json(SCHEMA)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    if not isinstance(register, dict):
        print("ERROR: The register root must be a JSON object.")
        return 1

    if register.get("schema_version") != 1:
        errors.append("Register schema_version must be 1.")

    if register.get("jurisdiction") != "Papua New Guinea":
        errors.append("Register jurisdiction must be Papua New Guinea.")

    documents = register.get("documents")

    if not isinstance(documents, list):
        errors.append("'documents' must be a JSON array.")
        documents = []

    # Check each document against the formal JSON Schema.
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    seen_ids = set()

    for index, document in enumerate(documents):
        label = f"documents[{index}]"

        if not isinstance(document, dict):
            errors.append(f"{label} must be a JSON object.")
            continue

        for error in sorted(
            validator.iter_errors(document),
            key=lambda item: list(map(str, item.absolute_path)),
        ):
            field = ".".join(str(part) for part in error.absolute_path)
            location = f"{label}.{field}" if field else label
            errors.append(f"{location}: {error.message}")

        document_id = document.get("document_id")

        if isinstance(document_id, str):
            if not ID_PATTERN.fullmatch(document_id):
                errors.append(f"{label}: invalid document_id format.")

            if document_id in seen_ids:
                errors.append(
                    f"{label}: duplicate document_id '{document_id}'."
                )
            else:
                seen_ids.add(document_id)

        # A document cannot claim verified current law without
        # the record itself being marked verified.
        if (
            document.get("verification_status") != "verified"
            and document.get("legal_status") == "in_force"
        ):
            errors.append(
                f"{label}: legal_status is 'in_force', but "
                "verification_status is not 'verified'."
            )

        # A verified record should have a verification date and evidence.
        if document.get("verification_status") == "verified":
            if not valid_date(document.get("last_verified_date")):
                errors.append(
                    f"{label}: verified records need a valid "
                    "last_verified_date."
                )

            evidence = document.get("legal_status_evidence")
            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(
                    f"{label}: verified records need legal_status_evidence."
                )

    if errors:
        print("DOCUMENT REGISTER VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"DOCUMENT REGISTER VALIDATION PASSED: "
        f"{len(documents)} record(s)."
    )
    print("JSON Schema validation passed.")
    print("Metadata consistency checks passed.")
    print(
        "Reminder: automated validation does not establish "
        "legal authenticity or current legal status."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
