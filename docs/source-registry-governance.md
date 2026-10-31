# Source Registry Governance

The sources/discovery-sources.yml file is the controlled list of websites that discovery may inspect. It records each source's stable ID, public URL, source type, discovery scope, review state, and known redistribution permission.

## What registry inclusion means

A listed source is approved for discovery consideration only. Inclusion does not establish that a particular page or file is authentic, legally authoritative, current, in force, complete, or free to redistribute. Each discovered item remains in the human-review queue until a reviewer assesses it.

## Adding or changing a source

1. Confirm the source identity and that the URL belongs to the claimed organisation or service.
2. Prefer HTTPS and record the canonical public homepage.
3. Describe the material the crawler may discover in discovery_scope; do not broaden scope without a reason.
4. Set review_status to candidate or needs_verification until source identity and role are checked.
5. Keep redistribution permission unknown unless a reliable licence or permission statement supports another value.
6. Run python scripts/validate_documents.py and the unit tests.
7. Review changes before merging.

## Candidate provenance

Every queue candidate with a source_id must reference an ID in this registry. The validator checks that relationship and rejects duplicate source IDs. Discovery metadata is observational; it must never overwrite reviewer decisions, legal-status assessments, or redistribution decisions.

## Non-automatic decisions

The registry schema requires automatic legal-status changes and automatic redistribution approval to remain disabled. Legal status and reuse rights require evidence and human review. A successful technical HTTP response is not legal verification.

## Validation

The repository validation workflow checks the YAML registry against schemas/source-registry.schema.json, verifies source ID uniqueness, and checks candidate-to-source references. Automated validation checks data consistency only; it does not certify any source or legal material.
