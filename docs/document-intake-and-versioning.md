# Legal Document Intake and Version Tracking

## Purpose

The intake tool records a locally supplied file's SHA-256 checksum, source provenance, observed metadata, and append-only version history. It does not fetch URLs, decide legal status, verify authenticity, or approve reuse.

## Safe operating rules

- Obtain a file manually from a registered source using a lawful method. The tool does not bypass access controls or download from a URL.
- The source URL must be HTTPS and on the registered source host.
- Supply an explicit document ID, title, type, source ID, and permission assessment.
- Permission defaults to `unknown`. When permission is `unknown`, `restricted`, or `prohibited`, only metadata and checksum are recorded; the source file is not copied into the archive.
- A copy is archived in `.private/legal-documents/` only when the operator explicitly sets `--redistribution-permission permitted`. `.private/` is git-ignored and must never be committed to this public repository.
- Each new checksum creates a new version record. Existing version records are not overwritten. Repeated submission of the same file for the same document is idempotent.
- All new versions remain `pending_review`. New document records begin with `verification_status: pending_review` and `legal_status: status_unknown`.
- The tool does not change reviewer notes, legal-status evidence, amendments, or a verified/rejected decision on an existing record.
- Maximum file size is 100 MB by default and cannot be raised above 100 MB.

## Example

Metadata-only intake (recommended unless redistribution permission is documented):

```bash
python scripts/intake_document.py \\
  --file ./downloads/example-act.pdf \\
  --document-id example-act-2026 \\
  --title "Example Act 2026" \\
  --document-type act \\
  --source-id png_parliament \\
  --source-url https://parliament.gov.pg/legislation/example-act-2026 \\
  --redistribution-permission unknown
```

Only after permission to store a copy is established, use `--redistribution-permission permitted`.

## Data files

- `data/documents.json`: one record per legal document, with its current observed checksum.
- `data/document-versions.json`: append-only records of every observed file version, including checksum, source, timestamp, and previous-version link.
- `schemas/document-versions.schema.json`: version history schema.
- `.private/legal-documents/`: optional local copies when redistribution is explicitly permitted; excluded from Git.

## Change detection

A new file with the same document ID and a different checksum is recorded as the next version, linked to the prior version. It does not overwrite the old history entry. The change must be reviewed to determine whether it is a corrected scan, reprint, amendment, replacement, or unrelated file. A checksum proves byte-level identity only; it does not prove legal effect or document authenticity.

## Validation and limitations

Run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_documents.py
```

Validation checks schema shape, unique version IDs and checksums, document references, sequential numbering, and previous-version links. Human review is still required for authenticity, completeness, legal status, amendment coverage, and redistribution rights.