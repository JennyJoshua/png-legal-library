# PNG Legal Library — Document Verification Checklist

## Purpose

This checklist establishes the minimum checks required before a
legal document is approved for use by the PNG Legal Assistance AI.

A document being available online does not establish that it is
authentic, current, legally effective, or free to redistribute.

## 1. Document Identification

- [ ] Record the exact document title.
- [ ] Identify the document type.
- [ ] Identify the issuing authority.
- [ ] Record the original source URL.
- [ ] Record the date the document was retrieved.
- [ ] Record the document's publication date, if available.
- [ ] Assign a unique document ID.

## 2. Source Authenticity

- [ ] Confirm that the source belongs to the claimed organisation.
- [ ] Confirm that the document is hosted by an official source
      or independently corroborated by reliable evidence.
- [ ] Check that the document is complete and readable.
- [ ] Record any uncertainty about authenticity.

## 3. Legal Version and Status

- [ ] Check whether a newer version exists.
- [ ] Investigate known amendments.
- [ ] Check commencement information where applicable.
- [ ] Investigate repeal or replacement information.
- [ ] Record relevant related legislation.
- [ ] Record the evidence supporting the legal-status assessment.
- [ ] Record unresolved questions explicitly.

Do not infer that a law is currently in force simply because
a copy is available online.

Do not treat a Bill as an enacted Act without evidence of enactment.

Do not assume that a consolidated document includes every amendment.

## 4. Court Judgments

For court judgments, where applicable:

- [ ] Verify the court and case title.
- [ ] Record the decision date.
- [ ] Record the case citation, if available.
- [ ] Check the judgment's completeness.
- [ ] Identify any available appeal or subsequent decision.
- [ ] Do not invent missing case details.

## 5. Copyright and Redistribution

- [ ] Review the source's terms and copyright information.
- [ ] Determine whether copying and redistribution are permitted.
- [ ] Record any applicable conditions or restrictions.
- [ ] If permission is unclear, retain metadata and a source link
      rather than publishing a document copy.

## 6. Technical Validation

- [ ] Validate the document metadata against the JSON schema.
- [ ] Check that the source URL is recorded correctly.
- [ ] Record a SHA-256 checksum if a file is stored.
- [ ] Record the repository path if a copy is stored.
- [ ] Check that the document is not an accidental duplicate.

## 7. Review Decision

Choose one outcome:

- DISCOVERED
- PENDING_REVIEW
- VERIFIED
- VERIFICATION_FAILED

A VERIFIED document must have sufficient evidence supporting
its authenticity and the specific claims made about its status.

If legal status remains uncertain, record STATUS_UNKNOWN in the
legal-status field even if the document itself has been verified.

A document may be verified as an authentic historical text
without being verified as current law.

## 8. Required Review Record

Record the following information where available:

- Document ID
- Reviewer or responsible team
- Review date
- Sources consulted
- Verification evidence
- Known amendments or related documents
- Copyright and redistribution assessment
- Outstanding uncertainties
- Decision and reasons

## 9. AI Usage Rules

The AI must:

- Prefer relevant, verified sources.
- Identify the source supporting each important legal claim.
- Cite the document and provision when available.
- Distinguish quoted law from plain-language explanation.
- Disclose material uncertainty.
- Never invent sections, cases, citations, or legal requirements.
- Recommend qualified legal assistance when appropriate.

## 10. Automation Rules

GitHub Actions may validate metadata, detect source changes,
calculate checksums, and prepare review reports.

Automation must not independently declare a law current or in force
merely because a webpage or file has changed.

Material legal-status changes require evidence and human review.

## Important

This checklist defines the intended review process. Creating this
file does not mean that any document has passed the checks.
