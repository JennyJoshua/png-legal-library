# Milestone 5 — Legal research retrieval and evidence linking

## Purpose
Retrieve relevant indexed passages and return a stable citation identifier with the exact indexed document version, SHA-256 source checksum, source URL/ID, structural path, and original page or paragraph reference.

## Usage
Build the local index as described in [legal-segmentation-and-search.md](legal-segmentation-and-search.md), then run:

    python scripts/retrieve_legal_evidence.py "court competent jurisdiction"
    python scripts/retrieve_legal_evidence.py "section 5" --match any --limit 20

Use `--index` to select a local index. Results are JSON and remain local; do not commit extracted legal text or indexes.

## Evidence contract
A result is emitted only when its document ID, version ID, title, text, source reference, structural path, and valid SHA-256 checksum are present. Records failing these checks are excluded and counted in `rejected_untraceable_records`. Citation IDs are deterministic fingerprints of the indexed passage and its provenance. They are identifiers, not official legal citations.

## Important limitations
This stage uses deterministic keyword retrieval. It does not generate legal answers, authenticate source documents, verify amendments, determine whether a law is in force, or establish legal effect. A page/paragraph reference and checksum make a result traceable to an indexed copy; they do not prove that copy is authoritative or current. Always check the authoritative original and current law.
