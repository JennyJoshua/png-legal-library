#!/usr/bin/env python3
"""Record a locally supplied legal document and append an immutable version entry.

This tool never downloads a URL. It hashes a file supplied by the operator.
A copy is archived only when redistribution_permission is explicitly permitted.
All new records remain pending human review.
"""
import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "data" / "documents.json"
HISTORY = ROOT / "data" / "document-versions.json"
SOURCE_REGISTRY = ROOT / "sources" / "discovery-sources.yml"
MAX_FILE_BYTES = 100 * 1024 * 1024
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Existing local file; no URL downloads are performed")
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--document-type", required=True, choices=[
        "constitution", "act", "regulation", "gazette_notice", "court_judgment",
        "court_rule", "official_form", "government_guidance", "legal_aid_information", "other"])
    parser.add_argument("--source-url", required=True, help="Canonical HTTPS page where this file was obtained")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--issuing-authority")
    parser.add_argument("--publication-date")
    parser.add_argument("--commencement-date")
    parser.add_argument("--redistribution-permission", default="unknown",
                        choices=["permitted", "restricted", "prohibited", "unknown"])
    parser.add_argument("--max-file-mb", type=int, default=100)
    return parser.parse_args(argv)


def intake(args):
    if not ID_PATTERN.fullmatch(args.document_id):
        raise ValueError("document-id must use lowercase letters, digits, dots, underscores or hyphens.")
    supplied_url = urlsplit(args.source_url)
    if (supplied_url.scheme != "https" or not supplied_url.hostname
            or supplied_url.username or supplied_url.password
            or supplied_url.fragment or supplied_url.port not in (None, 443)):
        raise ValueError("source-url must be a credential-free HTTPS URL on the standard port, without a fragment.")
    source_data = __import__("yaml").safe_load(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    sources = {item["source_id"]: item for item in source_data["sources"]}
    if args.source_id not in sources:
        raise ValueError(f"Unknown source-id: {args.source_id}")
    source = sources[args.source_id]
    registered_url = urlsplit(source["url"])
    registered_path = registered_url.path.rstrip("/")
    candidate_path = supplied_url.path.rstrip("/")
    path_matches = (candidate_path == registered_path or
                    candidate_path.startswith(registered_path + "/"))
    if (supplied_url.scheme != "https"
            or supplied_url.hostname.casefold() != (registered_url.hostname or "").casefold()
            or registered_url.port not in (None, 443)
            or not path_matches):
        raise ValueError("source-url must use the exact registered HTTPS host and remain within its registered path.")

    supplied = Path(args.file).expanduser()
    if not supplied.is_file() or supplied.is_symlink():
        raise ValueError("file must be an existing regular local file, not a symlink.")
    supplied = supplied.resolve()
    size = supplied.stat().st_size
    if size < 1:
        raise ValueError("Empty files cannot be registered.")
    limit = min(max(args.max_file_mb, 1), 100) * 1024 * 1024
    if size > limit:
        raise ValueError(f"File exceeds the configured maximum ({limit // (1024*1024)} MB).")
    checksum = sha256_file(supplied)

    register = load_json(REGISTER)
    history = load_json(HISTORY)
    existing = next((d for d in register["documents"] if d["document_id"] == args.document_id), None)
    if existing and existing.get("source_url") != args.source_url:
        raise ValueError("Existing document ID has a different source URL; do not silently change its provenance.")
    for item in history["versions"]:
        if item["checksum_sha256"] == checksum:
            if item["document_id"] == args.document_id:
                return {"result": "already_recorded", "version_id": item["version_id"], "checksum_sha256": checksum}
            raise ValueError("This exact file hash is already associated with another document ID; human review is required.")

    prior = [v for v in history["versions"] if v["document_id"] == args.document_id]
    prior.sort(key=lambda v: v["version_number"])
    version_number = len(prior) + 1
    previous_id = prior[-1]["version_id"] if prior else None
    version_id = uuid4().hex[:16]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    media_type = mimetypes.guess_type(supplied.name)[0] or "application/octet-stream"

    archived_path = None
    if args.redistribution_permission == "permitted":
        relative = Path(".private") / "legal-documents" / args.document_id / f"{checksum}{supplied.suffix.lower()}"
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and sha256_file(destination) != checksum:
            raise ValueError("Archive destination already exists with a different checksum.")
        if not destination.exists():
            shutil.copyfile(supplied, destination)
        archived_path = relative.as_posix()

    if existing is None:
        record = {
            "document_id": args.document_id, "title": args.title, "document_type": args.document_type,
            "jurisdiction": "Papua New Guinea", "issuing_authority": args.issuing_authority,
            "source_id": args.source_id, "source_url": args.source_url,
            "publication_date": args.publication_date, "commencement_date": args.commencement_date,
            "date_added": now[:10], "last_verified_date": None, "verification_status": "pending_review",
            "legal_status": "status_unknown", "legal_status_evidence": None, "amendments": [],
            "related_document_ids": [], "language": "en", "file_path": archived_path,
            "checksum_sha256": checksum, "current_version_id": version_id,
            "redistribution_permission": args.redistribution_permission,
            "reviewer_notes": None
        }
        register["documents"].append(record)
    else:
        # Verification and legal-status assessments belong to the exact file
        # version reviewed. A newly observed file must not inherit approval
        # from an earlier checksum. Preserve notes, but require fresh review.
        existing["checksum_sha256"] = checksum
        existing["current_version_id"] = version_id
        existing["file_path"] = archived_path
        existing["verification_status"] = "pending_review"
        existing["last_verified_date"] = None
        existing["legal_status"] = "status_unknown"
        existing["legal_status_evidence"] = None
        existing["redistribution_permission"] = args.redistribution_permission

    version = {
        "version_id": version_id, "document_id": args.document_id, "version_number": version_number,
        "checksum_sha256": checksum, "file_name": supplied.name, "file_size_bytes": size,
        "media_type": media_type, "source_url": args.source_url, "source_id": args.source_id,
        "observed_at": now, "previous_version_id": previous_id, "review_status": "pending_review",
        "redistribution_permission": args.redistribution_permission, "archived_path": archived_path,
        "verification_status": "pending_review", "verification_evidence": None, "verified_at": None
    }
    history["versions"].append(version)
    save_json_atomic(HISTORY, history)
    save_json_atomic(REGISTER, register)
    return {"result": "recorded", "version_id": version_id, "version_number": version_number,
            "checksum_sha256": checksum, "archived": archived_path is not None,
            "review_status": "pending_review", "legal_status": "status_unknown"}


def main(argv=None):
    try:
        args = parse_args(argv)
        result = intake(args)
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"INTAKE ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())