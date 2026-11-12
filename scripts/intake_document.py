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
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "data" / "documents.json"
HISTORY = ROOT / "data" / "document-versions.json"
TRANSACTION_JOURNAL = ROOT / "data" / ".intake-transaction.json"
INTAKE_LOCK = ROOT / "data" / ".intake.lock"
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


def recover_pending_transaction():
    """Replay a staged two-register update after an interrupted intake."""
    if not TRANSACTION_JOURNAL.exists():
        return False

    journal = load_json(TRANSACTION_JOURNAL)
    if (
        not isinstance(journal, dict)
        or journal.get("transaction_version") != 1
        or not isinstance(journal.get("documents"), dict)
        or not isinstance(journal.get("versions"), dict)
    ):
        raise ValueError("Pending intake transaction journal is invalid; manual recovery is required.")

    # Keep the journal until both snapshots are safely replaced. Replaying
    # both complete snapshots is safe if either write already completed.
    save_json_atomic(HISTORY, journal["versions"])
    save_json_atomic(REGISTER, journal["documents"])
    TRANSACTION_JOURNAL.unlink()
    return True


def commit_registers_transactionally(register, history):
    """Commit both register snapshots with a replayable recovery journal."""
    journal = {
        "transaction_version": 1,
        "documents": register,
        "versions": history,
    }
    save_json_atomic(TRANSACTION_JOURNAL, journal)
    recover_pending_transaction()


def open_regular_file_no_follow(path):
    """Open one regular file without following a final-component symlink."""
    no_follow = getattr(os, "O_NOFOLLOW", None)
    if no_follow is None:
        raise ValueError("This platform does not support O_NOFOLLOW; refusing unsafe file intake.")
    fd = os.open(os.fspath(path), os.O_RDONLY | no_follow)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Input and archive paths must resolve to regular files.")
        return fd, info
    except Exception:
        os.close(fd)
        raise


def _same_file_snapshot(before, after):
    return (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns
    )


def sha256_file(path):
    fd, before = open_regular_file_no_follow(path)
    try:
        digest = hashlib.sha256()
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        if not _same_file_snapshot(before, os.fstat(fd)):
            raise ValueError("File changed while it was being checked; retry intake.")
        return digest.hexdigest()
    finally:
        os.close(fd)


def copy_file_verified(source, destination, expected_checksum, expected_size):
    """Copy from a no-follow descriptor and publish only a verified snapshot."""
    source_fd, before = open_regular_file_no_follow(source)
    temporary = destination.with_name(destination.name + "." + uuid4().hex + ".tmp")
    target_fd = None
    try:
        if before.st_size != expected_size:
            raise ValueError("Source file changed before archive copy; retry intake.")
        target_fd = os.open(str(temporary), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        digest = hashlib.sha256()
        copied = 0
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            copied += len(chunk)
            if copied > expected_size:
                raise ValueError("Source file grew during archive copy; retry intake.")
            digest.update(chunk)
            view = memoryview(chunk)
            while view:
                written = os.write(target_fd, view)
                view = view[written:]
        if not _same_file_snapshot(before, os.fstat(source_fd)) or copied != expected_size:
            raise ValueError("Source file changed during archive copy; retry intake.")
        if digest.hexdigest() != expected_checksum:
            raise ValueError("Archived copy checksum does not match the inspected source file.")
        os.fsync(target_fd)
        os.close(target_fd)
        target_fd = None
        os.replace(temporary, destination)
    finally:
        os.close(source_fd)
        if target_fd is not None:
            os.close(target_fd)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


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
    """Run one intake at a time; fail closed if another process owns the lock."""
    token = uuid4().hex
    try:
        lock_fd = os.open(str(INTAKE_LOCK), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(
            "Another intake is running or a previous intake left a lock. "
            "Confirm no intake process is active before removing data/.intake.lock."
        ) from exc

    try:
        with os.fdopen(lock_fd, "w", encoding="utf-8") as lock_file:
            json.dump({
                "token": token,
                "pid": os.getpid(),
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }, lock_file)
            lock_file.flush()
            os.fsync(lock_file.fileno())
        return _intake_without_lock(args)
    finally:
        # Remove only the lock created by this process. Abrupt termination
        # leaves it in place for deliberate operator recovery.
        try:
            lock_data = load_json(INTAKE_LOCK)
            if isinstance(lock_data, dict) and lock_data.get("token") == token:
                INTAKE_LOCK.unlink()
        except (FileNotFoundError, OSError, ValueError):
            pass


def _intake_without_lock(args):
    # Recover a prior interrupted write before reading either register.
    recover_pending_transaction()

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
    try:
        source_fd, source_info = open_regular_file_no_follow(supplied)
    except (OSError, ValueError) as exc:
        raise ValueError("file must be an existing regular local file and must not be a symlink.") from exc
    try:
        size = source_info.st_size
        if size < 1:
            raise ValueError("Empty files cannot be registered.")
        limit = min(max(args.max_file_mb, 1), 100) * 1024 * 1024
        if size > limit:
            raise ValueError(f"File exceeds the configured maximum ({limit // (1024*1024)} MB).")
        digest = hashlib.sha256()
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        if not _same_file_snapshot(source_info, os.fstat(source_fd)):
            raise ValueError("File changed while it was being checked; retry intake.")
        checksum = digest.hexdigest()
    finally:
        os.close(source_fd)

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

    # Snapshot the assessment currently attached to the document onto its
    # exact previous version before the document record moves to a new file.
    if existing and prior:
        current_version_id = existing.get("current_version_id")
        previous_current = next(
            (item for item in prior if item.get("version_id") == current_version_id),
            None,
        )
        if previous_current is None:
            previous_current = next(
                (item for item in prior
                 if item.get("checksum_sha256") == existing.get("checksum_sha256")),
                None,
            )
        if previous_current is not None:
            previous_current["verification_status"] = existing.get(
                "verification_status", "pending_review"
            )
            previous_current["last_verified_date"] = existing.get("last_verified_date")
            previous_current["legal_status"] = existing.get(
                "legal_status", "status_unknown"
            )
            previous_current["legal_status_evidence"] = existing.get(
                "legal_status_evidence"
            )

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
            # Reopen without following symlinks, copy from that descriptor,
            # and verify file identity stability and the original digest.
            copy_file_verified(supplied, destination, checksum, size)
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
        "verification_status": "pending_review", "verification_evidence": None, "verified_at": None,
        "last_verified_date": None, "legal_status": "status_unknown",
        "legal_status_evidence": None
    }
    history["versions"].append(version)
    commit_registers_transactionally(register, history)
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