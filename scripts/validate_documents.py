#!/usr/bin/env python3
"""Validate PNG Legal Library registers and metadata."""

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

DOCUMENT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
RESOURCE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_json(path):
    """Load JSON and report readable errors."""
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

    if register.get("schema_version") != 1:
        errors.append("Document register schema_version must be 1.")

    if register.get("jurisdiction") != "Papua New Guinea":
        errors.append(
            "Document register jurisdiction must be Papua New Guinea."
        )

    documents = register.get("documents")

    if not isinstance(documents, list):
        errors.append("'documents' must be a JSON array.")
        return errors, 0

    seen_ids = set()

    for index, document in enumerate(documents):
        label = f"documents[{index}]"

        if not isinstance(document, dict):
            errors.append(f"{label} must be a JSON object.")
            continue

        errors.extend(schema_errors(document, schema, label))

        document_id = document.get("document_id")

        if isinstance(document_id, str):
            if not DOCUMENT_ID_PATTERN.fullmatch(document_id):
                errors.append(
                    f"{label}: invalid document_id format."
                )

            if document_id in seen_ids:
                errors.append(
                    f"{label}: duplicate document_id '{document_id}'."
                )
            else:
                seen_ids.add(document_id)

        if (
            document.get("verification_status") != "verified"
            and document.get("legal_status") == "in_force"
        ):
            errors.append(
                f"{label}: legal_status is 'in_force', but "
                "verification_status is not 'verified'."
            )

        if document.get("verification_status") == "verified":
            if not valid_date(document.get("last_verified_date")):
                errors.append(
                    f"{label}: verified records need a valid "
                    "last_verified_date."
                )

            evidence = document.get("legal_status_evidence")

            if not isinstance(evidence, str) or not evidence.strip():
                errors.append(
                    f"{label}: verified records need "
                    "legal_status_evidence."
                )

    return errors, len(documents)


def validate_resources(register, schema):
    """Validate the legal resources catalogue."""
    errors = []

    if not isinstance(register, dict):
        return [
            "Legal resources catalogue root must be a JSON object."
        ], 0

    errors.extend(
        schema_errors(register, schema, "legal_resources")
    )

    resources = register.get("resources")

    if not isinstance(resources, list):
        errors.append("'resources' must be a JSON array.")
        return errors, 0

    declared_types = register.get("resource_types", [])

    if not isinstance(declared_types, list):
        declared_types = []

    seen_ids = set()

    for index, resource in enumerate(resources):
        label = f"resources[{index}]"

        if not isinstance(resource, dict):
            errors.append(f"{label} must be a JSON object.")
            continue

        resource_id = resource.get("resource_id")

        if isinstance(resource_id, str):
            if not RESOURCE_ID_PATTERN.fullmatch(resource_id):
                errors.append(
                    f"{label}: resource_id must use lowercase letters, "
                    "numbers, and single hyphens between parts."
                )

            if resource_id in seen_ids:
                errors.append(
                    f"{label}: duplicate resource_id '{resource_id}'."
                )
            else:
                seen_ids.add(resource_id)

        resource_type = resource.get("resource_type")

        if (
            isinstance(resource_type, str)
            and resource_type not in declared_types
        ):
            errors.append(
                f"{label}: resource_type is not listed in "
                "the catalogue's resource_types."
            )

        if (
            resource.get("verification_status") != "verified"
            and resource.get("legal_status") == "in_force"
        ):
            errors.append(
                f"{label}: legal_status is 'in_force', but "
                "verification_status is not 'verified'."
            )

        if resource.get("verification_status") == "verified":
            if not valid_date(resource.get("last_checked")):
                errors.append(
                    f"{label}: verified resources need a valid "
                    "last_checked date."
                )

            source_url = resource.get("source_url")

            if not isinstance(source_url, str) or not source_url.strip():
                errors.append(
                    f"{label}: verified resources need a source_url."
                )

    return errors, len(resources)


def main():
    try:
        document_register = load_json(DOCUMENT_REGISTER)
        document_schema = load_json(DOCUMENT_SCHEMA)
        resource_register = load_json(RESOURCE_REGISTER)
        resource_schema = load_json(RESOURCE_SCHEMA)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    document_errors, document_count = validate_documents(
        document_register,
        document_schema,
    )

    resource_errors, resource_count = validate_resources(
        resource_register,
        resource_schema,
    )

    errors = document_errors + resource_errors

    if errors:
        print("LEGAL LIBRARY VALIDATION FAILED")

        for error in errors:
            print(f"- {error}")

        return 1

    print("LEGAL LIBRARY VALIDATION PASSED")
    print(f"Document register: {document_count} record(s).")
    print(f"Legal resources catalogue: {resource_count} resource(s).")
    print("JSON Schema validation passed.")
    print("Metadata consistency checks passed.")
    print(
        "Reminder: automated validation does not establish "
        "legal authenticity, current legal status, or redistribution rights."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
