# Milestone 10 — Integration and release-readiness report

## Scope reviewed
Repository branch: `phase10/legal-corpus-foundation`
Comparison branch: `main`
Review date: 2026-11-11

The reviewed integration branch contains the document intake/versioning, extraction, segmentation, keyword index, evidence retrieval, research agent, cited Q&A, local browser portal, Milestone 9 safeguards, Phase 12 provenance/version/discovery compliance, and transaction-safe intake work. GitHub comparison reports `phase10/legal-corpus-foundation` is 100 commits ahead of `main` (and `main` is 0 commits ahead of this branch) at the time of this review. This is a substantial integration gap, not approval to merge. No merge to `main` or deployment was performed.

## Integration architecture
1. Register and review an authoritative source in the source registry.
2. Intake a permitted local source file with its source ID, URL, document ID and version metadata.
3. Extract text locally; OCR requires Tesseract when the source is scanned.
4. Segment extracted text and build the local keyword index.
5. Search passages and retrieve evidence with provenance.
6. Use the research-agent / legal-Q&A modules to produce evidence-bound draft research responses.
7. Open `web/index.html` and load the locally generated index for browser-based search.

Refer to the milestone-specific documents for exact commands and schemas. Extracted text and the generated index are intended to remain local and gitignored.

## Release gate results

| Gate | Status | Notes |
|---|---|---|
| Milestone branches and files present | Reviewed | Current Phase 10 integration branch contains the milestone modules and Phase 12 changes reviewed in this report. |
| Portal and usage documentation | Present | Static local browser portal; no hosted deployment. |
| Security changes | Partially verified | Phase 12 transaction journal and single-writer lock are implemented and covered by CI; TOCTOU and retrieval-index resource limits remain open. See `docs/security-and-legal-safeguards.md`. |
| Full automated test suite | CI passed for current integration commit | GitHub Actions run #64 completed successfully on merge commit `0ee257abdc84211df1b174232c4116b9924897df`; inspect the workflow job logs for the executed test steps. |
| GitHub Actions | Passed | [Run #64](https://github.com/JennyJoshua/png-legal-library/actions/runs/42967376713) completed with conclusion `success` on 2026-11-11. |
| Actual PNG legal corpus | Not ready | No verified, complete corpus of authoritative PNG Acts, amendments, subsidiary legislation or case law has been ingested and reviewed. |
| Legal currency / amendment validation | Not ready | No automatic legal status determination; human legal review remains essential. |
| Public hosting / production | Not performed | Local portal only. No hosting provider, API, paid service or production deployment was authorised. |

## Required verification before any release
Run from the repository root in a clean Python 3.12 environment:

```bash
python -m pip install -r requirements-processing.txt
python -m unittest discover -s tests -v
python -m compileall -q scripts
python scripts/validate_documents.py
```

If OCR is required, install Tesseract separately and verify its version and language data. Run an end-to-end test with a small, lawfully obtained, authoritative PNG legal document whose source metadata and expected page/section references have been manually checked. Confirm that extracted text, index passages, search results and Q&A citations all trace back to that exact source version.

Record the actual test output and GitHub Actions result before changing this report's statuses.

## Release decision
**Not ready for public production deployment.** The software workflow is assembled as a prototype, but release is blocked by unverified full integration tests, absence of a validated PNG legal corpus, unresolved legal-currentness review, and the lack of a reviewed production hosting/security design.

## User approvals required for later release
- Approval to merge the milestone branch into `main`.
- Approval of a specific hosting/deployment target, after confirming its free-tier terms and data handling.
- Legal review of authoritative sources, licensing/redistribution permissions, completeness, amendment and commencement status.
- Explicit approval before any paid service, API, or third-party hosting is introduced.

## Intended product boundary
This system is a legal research and document-navigation aid. It is not a law firm, legal practitioner, court database, or source of legal advice. It must not present generated text as authoritative law or claim that an instrument is current unless a competent reviewer has verified the relevant authoritative records.


## Verification update — 2026-11-11

PR #16, “P12-D: transaction-safe intake and single-writer hardening”, was merged into `phase10/legal-corpus-foundation` as commit `0ee257abdc84211df1b174232c4116b9924897df`. The post-merge GitHub Actions workflow [run #64](https://github.com/JennyJoshua/png-legal-library/actions/runs/42967376713) completed successfully (run ID `42967376713`). It is the current branch's latest recorded validation evidence.

The run verifies the automated software checks configured in the repository at that commit. It does not establish legal authenticity, currentness, commencement, completeness, legal effect, or redistribution permission for any legal instrument.

## Integration review — 2026-11-11

### Branch and integration position

- Current integration branch: `phase10/legal-corpus-foundation`.
- Current reviewed commit: `0ee257abdc84211df1b174232c4116b9924897df`.
- GitHub comparison: the integration branch is 100 commits ahead of `main`; `main` is not ahead of the integration branch.
- This review did not modify `main`, merge the integration branch into `main`, or deploy the application.
- The age and size of the branch difference require a deliberate integration review; commit count alone is not a quality or release-readiness measure.

### Legal corpus and review queue

At this review, the repository's legal-resource review queue contains 39 candidates, all marked `needs_more_evidence`. The document register contains one document record; the document-version register and legal-resources catalogue contain no entries. The registered Constitution record has not been established as a verified, versioned source document in the corpus.

The repository therefore has a software and research foundation, not yet a populated, verified PNG legal corpus. No claim of complete national legislation, current law, or authoritative case-law coverage is justified.

### Outstanding technical risks

1. File time-of-check/time-of-use (TOCTOU) race conditions remain to be reviewed and tested.
2. Retrieval-index size, record-count, and resource-consumption limits need explicit bounds and tests.
3. Hosted access still lacks an approved authentication, privacy, backup, and operational security design.
4. A clean end-to-end test using a lawfully obtained authoritative document, exact source version, page/section references, extraction, indexing, retrieval, and citations remains outstanding.

### Research PR reconciliation

- PR #2 (Parliament and OLC source discovery) contains two research-only deliverables. It records unresolved normal-browser checks, no verified document samples for key Parliament listings, and restrictive Parliament website reuse terms. These links are discovery leads, not proof of authoritative law or permission to redistribute source documents.
- PR #3 (National Gazette source discovery) contains two research-only deliverables. It identifies PacLII and PNGi Portal as third-party discovery sources and NICTA as a narrow official register. It does not establish completeness or redistribution permission. The 1985 PacLII sample reference has an unresolved identifier discrepancy: the referenced `1985/68.pdf` is described as showing Gazette No. G69. This must be checked against the source issue index and original PDF before relying on the identifier.
- Both research assignments were accessed on 2026-11-03. They require fresh human/browser verification before any source registry promotion or document ingestion.

### Current release decision

**Not ready for merge to `main` or public production.** Continue on the integration branch and feature branches. First reconcile the research-only deliverables and close the technical hardening gaps; then complete a bounded legal-document pilot with competent human review and explicit reuse-permission checks.

A successful CI run verifies configured software checks only. It is not legal validation, and it does not replace source-by-source human review.


## Verification update — 2026-11-12

### Phase 11 technical hardening

PR #20, "Security: harden local intake and bound retrieval index resources", was merged into `phase10/legal-corpus-foundation` as commit `a6ef65a12c731d126c396770a8a8630c70879aee`. Its pull-request validation run #68 passed on head commit `84f0d8c8abea4d3082b7a2f64292343709a7702c`.

The merged changes address the specific intake TOCTOU and retrieval-index resource-limit risks described earlier in this report. They add no legal corpus content. The run verifies configured software checks only; it does not establish legal authenticity, currentness, commencement, completeness, legal effect, or reuse rights.

### Authoritative-document pilot preflight

The first candidate is **Constitutional Amendment No. 41 (Motions of No Confidence) Law 2013**, hosted as a PDF on the National Parliament website. The PDF text identifies the instrument as made by Parliament and contains Clerk fair-print and Speaker section 14 certification material.

The previously registered consolidated Constitution PDF is not suitable as the first current-law pilot: the Parliament-hosted copy's amendment appendix ends at No. 22, and the Ombudsman-hosted copy is an older 2018 upload. Amendments Nos. 48 and 49 were passed in March 2025, so those copies cannot be treated as a current consolidated Constitution.

The No. 41 instrument is a discrete historical amendment. Its current legal effect must not be inferred from the 2013 instrument alone. Its record must remain pending human review with legal status unknown. PNG Copyright and Neighbouring Rights Act 2000, section 5(b), is relevant to the reuse assessment for official legislative text, but the repository has not made a final permission determination; redistribution permission remains unknown.

**The end-to-end pilot has not yet run.** A byte-for-byte downloadable PDF has not been obtained in the working environment, so there is no checksum, version record, extraction output, index, or retrieval result. The exact official PDF must be obtained before claiming pilot completion. The preflight plan is recorded in `docs/authoritative-document-pilot-preflight.md`.

### Current decision

The software foundation has progressed, but the PNG legal corpus and legal release gates remain **not ready**. Do not merge the Phase 10 integration branch into `main`, deploy publicly, or present any unverified document as current law.
