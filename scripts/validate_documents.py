#!/usr/bin/env python3
"""Validate the PNG Legal Library document register.

This checks metadata structure only. It does not verify legal accuracy,
authenticity, amendments, or whether a law is currently in force.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

REGISTER = Path("data/documents.json")

REQUIRED_FIELDS = {
    "document_id",
    "title",
    "document_type",
    "jurisdiction",
    "source_url",
    "verification_status",
    "legal_status",
    "date_added",
}

DOCUMENT_TYPES = {
    "constitution",
    "act",
    "regulation",
    "gazette_notice",
    "court_judgment",
    "court_rule",
    "official_form",
    "government_guidance",
    "legal_aid_information",
    "other",
}

VERIFICATION_STATUSES = {
    "discovered",
    "pending_review",
    "verified",
    "verification_failed",
}

LEGAL_STATUSES = {
    "in_force",
    "amended",
    "partially_repealed",
    "repealed",
    "superseded",
    "not_yet_in_force",
    "status_unknown",
    "not_applicable",
}

DOCUMENT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def valid_date(value):
    """Return True for a valid YYYY-MM-DD date."""
    if not isinstance(value, str):
        return False

    try:
        date.fromisoformat(value)
        return len(value) == 10
    except ValueError:
        return False


def main():
    errors = []

    if not REGISTER.exists():
        print(f"ERROR: Register not found: {REGISTER}")
        return 1

    try:
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"ERROR: Cannot read valid JSON: {exc}")
        return 1

    if not isinstance(data, dict):
        print("ERROR: Register root must be a JSON object.")
        return 1

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1.")

    if data.get("jurisdiction") != "Papua New Guinea":
        errors.append("jurisdiction must be Papua New Guinea.")

    documents = data.get("documents")

    if not isinstance(documents, list):
        errors.append("'documents' must be a list.")
        documents = []

    seen_ids = set()

    for index, document in enumerate(documents):
        location = f"documents[{index}]"

        if not isinstance(document, dict):
            errors.append(f"{location} must be an object.")
            continue

        missing = REQUIRED_FIELDS - document.keys()
        if missing:
            errors.append(
                f"{location} is missing fields: {', '.join(sorted(missing))}"
            )

        document_id = document.get("document_id")

        if not isinstance(document_id, str) or not DOCUMENT_ID_PATTERN.fullmatch(
            document_id
        ):
            errors.append(f"{location}: invalid document_id.")
        elif document_id in seen_ids:
            errors.append(f"{location}: duplicate document_id '{document_id}'.")
        else:
            seen_ids.add(document_id)

        if not isinstance(document.get("title"), str) or not document.get("title", "").strip():
            errors.append(f"{location}: title must not be empty.")

        if document.get("document_type") not in DOCUMENT_TYPES:
            errors.append(f"{location}: invalid document_type.")

        if document.get("jurisdiction") != "Papua New Guinea":
            errors.append(f"{location}: invalid jurisdiction.")

        source_url = document.get("source_url")
        if not isinstance(source_url, str) or not source_url.startswith(
            ("https://", "http://")
        ):
            errors.append(f"{location}: source_url must be an HTTP(S) URL.")

        if document.get("verification_status") not in VERIFICATION_STATUSES:
            errors.append(f"{location}: invalid verification_status.")

        if document.get("legal_status") not in LEGAL_STATUSES:
            errors.append(f"{location}: invalid legal_status.")

        if not valid_date(document.get("date_added")):
            errors.append(f"{location}: date_added must be a valid YYYY-MM-DD date.")

        for field in ("publication_date", "commencement_date", "last_verified_date"):
            value = document.get(field)
            if value is not None and not valid_date(value):
                errors.append(
                    f"{location}: {field} must be null or a valid YYYY-MM-DD date."
                )

        if (
            document.get("verification_status") != "verified"
            and document.get("legal_status") == "in_force"
        ):
            errors.append(
                f"{location}: unverified record cannot claim legal_status in_force."
            )

    if errors:
        print("DOCUMENT REGISTER VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"DOCUMENT REGISTER VALIDATION PASSED: {len(documents)} record(s).")
    print("Note: Metadata validation does not establish legal accuracy or status.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
