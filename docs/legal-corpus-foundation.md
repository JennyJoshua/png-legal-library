# Milestone 11 — Legal Corpus Foundation

**Branch:** phase10/legal-corpus-foundation  
**Prepared:** 2026-10-31  
**State:** Foundation and review controls added; legal corpus not yet verified.

## Goal
Create a controlled, auditable foundation for building a reliable Papua New Guinea legal corpus. This milestone does not claim that the Constitution or any other instrument has been fully verified or that the repository contains a complete statement of PNG law.

## Work included
1. Expanded the source registry with the Office of Legislative Counsel, CLRC and a clearly labelled third-party Gazette discovery archive.
2. Added a source review register distinguishing official institutions, judicial sources, law reform sources and secondary discovery services.
3. Added a constitutional amendment register with explicit evidence requirements for Amendments Nos. 48 and 49.
4. Seeded the human review queue with source/document leads, all kept at needs_more_evidence.
5. Preserved the rule that legal status, verification and redistribution permissions cannot be assigned automatically.

## Legal corpus workflow
1. Discover a source or candidate instrument.
2. Record original URL, access date, source ID and technical access result.
3. Identify exact instrument title, number, issuing authority and jurisdiction.
4. Obtain primary publication or a copy whose provenance is established.
5. Verify certification, Gazette publication, commencement and amendment/repeal history as applicable.
6. Record checksum and version metadata.
7. Obtain a separate copyright and redistribution decision.
8. Have a competent reviewer approve the record.
9. Only then transfer the approved record into the legal document/resource catalogue.

## Status vocabulary
- discovered: a lead exists; no substantive verification.
- pending_review: waiting for a human reviewer.
- verified: identity and source provenance checked against recorded evidence.
- verification_failed: evidence shows the candidate is not authentic or cannot be sufficiently verified.
- Legal status is separate. Verification does not imply in force.

## Release restrictions
- No automated declaration that a law is current.
- No automatic approval of copying or redistribution.
- AI-generated legal summaries do not replace the underlying instrument.
- No completed client files, personal case information or privileged material in the public corpus.
- No public deployment approval is granted by this milestone.

## Remaining work
- Obtain and compare an authoritative consolidated Constitution and every constitutional alteration.
- Establish exact enacted identity and legal effect of Amendment Nos. 48 and 49.
- Contact OLC or obtain an authoritative publication pathway for current and historical legislation.
- Establish a traceable National Gazette collection, including issue number, date and page.
- Build a national Acts, Organic Laws and subsidiary legislation inventory with amendment and commencement history.
- Establish a court judgment collection with court, case number, date, citation and source.
- Add provincial and local-level instruments, starting with Gulf Province where available.
- Complete professional legal review before describing any corpus collection as verified or current.

## Acceptance criteria
- Source registry validates against its schema.
- Review queue validates against its schema.
- Constitution remains pending_review / status_unknown until authoritative evidence is recorded.
- Amendment Nos. 48 and 49 have separate evidence records; neither is presumed valid, commenced or current.
- Review decisions identify reviewer, date and evidence.
- No changes are made to main as part of this milestone.
