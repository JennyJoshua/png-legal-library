#!/usr/bin/env python3
"""Evidence-linked retrieval over the local PNG legal passage index."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9]+")
CHECKSUM = re.compile(r"^[a-f0-9]{64}$")
ROOT = Path(__file__).resolve().parent.parent
MAX_INDEX_BYTES = 50 * 1024 * 1024
MAX_INDEX_RECORDS = 100_000


def _terms(value):
    return list(dict.fromkeys(TOKEN.findall(str(value).casefold())))


def _citation_id(record):
    identity = "|".join(str(record.get(k) or "") for k in (
        "document_id", "version_id", "source_checksum_sha256",
        "source_reference", "structure_path", "text"))
    return "pnglaw:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]


def _validate_record(record):
    required = ("document_id", "version_id", "source_checksum_sha256",
                "document_title", "text", "source_reference")
    missing = [key for key in required if not record.get(key)]
    if missing:
        return "missing required provenance: " + ", ".join(missing)
    if not re.fullmatch(r"[a-f0-9]{16}", str(record["version_id"])):
        return "invalid version_id"
    if not CHECKSUM.fullmatch(str(record["source_checksum_sha256"])):
        return "invalid source checksum"
    if not isinstance(record.get("structure_path"), list):
        return "missing structural path"
    if not (record.get("page_number") or record.get("paragraph_number") or record.get("source_reference")):
        return "missing location reference"
    return None


def retrieve(index_path, query, match="all", limit=10):
    terms = _terms(query)
    if not terms:
        raise ValueError("Enter at least one searchable word or number.")
    if match not in ("all", "any"):
        raise ValueError("match must be 'all' or 'any'")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    with Path(index_path).open("rb") as handle:
        raw = handle.read(MAX_INDEX_BYTES + 1)
    if len(raw) > MAX_INDEX_BYTES:
        raise ValueError(f"Index exceeds the configured {MAX_INDEX_BYTES}-byte limit.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Index must be valid UTF-8 JSON.") from exc
    if not isinstance(data, dict):
        raise ValueError("Index root must be a JSON object.")
    records = data.get("records")
    if not isinstance(records, list):
        raise ValueError("Index records must be an array")
    if len(records) > MAX_INDEX_RECORDS:
        raise ValueError(f"Index exceeds the configured {MAX_INDEX_RECORDS}-record limit.")
    results, rejected = [], 0
    for record in records:
        if not isinstance(record, dict):
            rejected += 1
            continue
        error = _validate_record(record)
        if error:
            rejected += 1
            continue
        searchable = " ".join(str(record.get(k) or "") for k in (
            "document_title", "title", "number", "text", "source_reference",
            "source_id")).casefold()
        present = [term for term in terms if re.search(
            r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", searchable)]
        if not present or (match == "all" and len(present) != len(terms)):
            continue
        score = sum(len(re.findall(
            r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", searchable))
            for term in present)
        if " ".join(terms) in searchable:
            score += 3
        results.append((score, record))
    results.sort(key=lambda item: (-item[0], item[1]["document_id"],
                                  item[1]["source_reference"], item[1].get("node_id", "")))
    evidence = []
    for score, record in results[:limit]:
        location = {
            "source_reference": record["source_reference"],
            "page_number": record.get("page_number"),
            "paragraph_number": record.get("paragraph_number"),
            "structure_path": record["structure_path"],
        }
        evidence.append({
            "citation_id": _citation_id(record),
            "score": score,
            "document_title": record["document_title"],
            "document_id": record["document_id"],
            "version_id": record["version_id"],
            "source_id": record.get("source_id"),
            "source_url": record.get("source_url"),
            "source_checksum_sha256": record["source_checksum_sha256"],
            "location": location,
            "kind": record.get("kind"),
            "number": record.get("number"),
            "title": record.get("title"),
            "excerpt": record["text"],
            "evidence_status": "traceable_source_reference",
            "limitations": [
                "Retrieval confirms traceability to this indexed source version only.",
                "It does not establish authenticity, commencement, current force, amendment status, or legal effect.",
                "Check the authoritative original before relying on this passage."
            ]
        })
    return {
        "query": query,
        "match": match,
        "result_count": len(evidence),
        "rejected_untraceable_records": rejected,
        "results": evidence,
        "warning": "Research retrieval only. A traceable citation is not proof that the source is authoritative or current law."
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Retrieve legal passages with traceable source evidence.")
    parser.add_argument("query")
    parser.add_argument("--index", default=str(ROOT / "legal-index" / "index.json"))
    parser.add_argument("--match", choices=("all", "any"), default="all")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(retrieve(args.index, args.query, args.match, args.limit),
                         indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print("RETRIEVAL ERROR: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
