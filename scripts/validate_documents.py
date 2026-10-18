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

DOCUMENT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
RESOURCE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CANDIDATE_ID_PATTERN = re.compile(r"^[a-f0-9]{16}$")


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
        errors.append("'documents' must be a
