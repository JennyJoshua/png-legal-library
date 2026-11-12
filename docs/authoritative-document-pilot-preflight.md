# Authoritative document pilot — preflight assessment

**Assessment date:** 2026-11-12  
**Target integration branch:** `phase10/legal-corpus-foundation`  
**Pilot state:** Source candidate identified; byte-level intake and processing not yet completed.

## Decision

Use **Constitutional Amendment No. 41 (Motions of No Confidence) Law 2013** as the first candidate for a bounded, historical-document pipeline test.

Do **not** use the currently registered Constitution PDF as the pilot's consolidated Constitution. The Parliament-hosted Constitution PDF's amendment appendix ends at No. 22, while the Ombudsman Commission PDF is an older 2018 upload and does not establish coverage of later amendments. Constitutional Amendments Nos. 48 and 49 were passed in March 2025. These copies cannot be presented as a current consolidated Constitution.

## Candidate source

- **Title:** Constitutional Amendment No. 41 (Motions of No Confidence) Law 2013
- **Document type:** Act / constitutional amendment
- **Issuing authority:** National Parliament of Papua New Guinea
- **Official-hosted PDF URL:** https://www.parliament.gov.pg/uploads/acts/13C_41.pdf
- **Canonical host for the repository source registry:** `https://parliament.gov.pg/`
- **Expected source ID:** `png_parliament`
- **Proposed document ID:** `constitutional-amendment-41-motions-of-no-confidence-2013`

The PDF text identifies the instrument as a law made by the National Parliament. It contains a Clerk of the National Parliament fair-print certification and a Speaker's certificate under section 14, recording the first and second parliamentary votes. The PDF changes section 145(1)(b) by replacing “one week's” notice with “one month's” notice and “one tenth” of seats with “one fifth”.

The certification text is partly garbled in the text extraction, so the certification date must be read from the original PDF page image before recording it as structured metadata. Do not infer a publication or commencement date from the title or search result.

## Legal-status boundary

This is a discrete 2013 amending instrument, not a consolidated current Constitution. Later amendments changed section 145, and court proceedings have considered Constitutional Amendment No. 48 (2025). The pilot must preserve the exact 2013 instrument and its provenance without claiming that it alone states the current law.

Set all new intake assessments to:

- `verification_status: pending_review`
- `legal_status: status_unknown`
- `redistribution_permission: unknown`

Do not add amendment-effect conclusions, commencement dates, or a current-law label without competent review of the original instrument, subsequent amendments, and relevant court decisions.

## Reuse assessment

Section 5(b) of PNG's Copyright and Neighbouring Rights Act 2000 states that protection under that Act does not extend to an official text of a legislative, administrative or legal nature, or an official translation. WIPO Lex reproduces the Act and identifies its version as 2002, with entry into force recorded as 8 November 2000.

That provision is a relevant legal basis for assessing use of the underlying official legislative text. It is **not** treated here as a completed legal opinion about every element of the scanned PDF, the website's separate terms, or the current state of PNG copyright law. No document-specific reuse licence was located during this preflight.

Therefore keep redistribution permission as `unknown`. The first run should be metadata-only intake; do not archive the PDF in the repository or publish extracted text/index files. A reviewer may later determine whether the official text can be stored and redistributed under section 5(b).

## Intake and end-to-end test plan

Once the exact PDF bytes have been obtained from the official Parliament source:

1. Inspect the original PDF pages, including the Clerk's fair-print certification and the Speaker's section 14 certificate.
2. Compute the file's SHA-256 and record its byte size. Do not use a search-engine text extract as a substitute for the PDF file.
3. Run `scripts/intake_document.py` with source ID `png_parliament`, the exact official PDF URL, and `--redistribution-permission unknown`. This records provenance and checksum without archiving the source file.
4. Run `scripts/extract_document.py` against that same local file and the returned version ID.
5. Build the index with `scripts/build_legal_index.py`.
6. Retrieve a distinctive passage from section 2 (for example, the change from one week's to one month's notice).
7. Confirm every returned result includes the same document ID, version ID, SHA-256, source URL, and PDF page reference.
8. Compare the retrieved excerpt against the original PDF page image. Record extraction accuracy and any layout/OCR issues.
9. Keep all extracted text and indexes local and git-ignored. Do not commit a PDF, extracted text, or generated index to this public repository.

## Current blocker

The PDF's text and certification content are discoverable through the Parliament-hosted PDF reference, but a byte-for-byte downloadable copy has not yet been obtained in the working environment. Consequently no SHA-256, version ID, intake record, extraction, index, or retrieval result is claimed in this report.

The next required input is the actual PDF file from the official Parliament URL. If the official host remains unavailable for direct download, obtain the copy from the Parliament/Office of Legislative Counsel through an authorised channel. Do not substitute a third-party mirror or an unverified consolidated Constitution.

## Evidence links

- [National Parliament — Constitutional Amendment No. 41 PDF](https://www.parliament.gov.pg/uploads/acts/13C_41.pdf)
- [PNG Copyright and Neighbouring Rights Act 2000 — WIPO Lex](https://www.wipo.int/wipolex/en/legislation/details/3427)
- [Parliament — Constitutional Amendment Nos. 48 and 49 passed in March 2025 (PMNEC notice)](https://www.pmnec.gov.pg/national-executive-council-endorses-government-business-for-march-session-of-parliament/)
- [Supreme Court decision concerning Amendment No. 48, reported by NBC PNG, 14 May 2026](https://www.nbc.com.pg/post/35720/supreme-court-sismisses-nomane-challenge)

## Acceptance criteria

The pilot is complete only when the exact official PDF has been checksummed, metadata-intaked, extracted, indexed, retrieved, and manually compared against its original page image. Successful software execution does not verify legal status, commencement, amendment effect, completeness, or redistribution rights.
