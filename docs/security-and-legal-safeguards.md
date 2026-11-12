# Milestone 9 — Security, accuracy and legal safeguards

## Scope
This milestone reviews the current local document-intake, extraction, retrieval, research-agent and browser-portal paths. It does not certify the application as secure or establish legal accuracy.

## Changes made on this branch

1. **Registered source URL validation** — intake now parses URLs and requires credential-free HTTPS on the standard port, exact registered hostname, and a path within the registered source path. This closes a hostname-prefix weakness where a deceptive hostname such as `parliament.gov.pg.attacker.example` could pass a simple string-prefix check.
2. **Prompt-injection warning** — the research-agent system instructions now explicitly classify retrieved passage text as untrusted data and instruct a connected model not to follow embedded commands or prompts.
3. **Portal link handling** — external source links are restricted to HTTPS; rendered source text remains HTML-escaped.
4. **Regression tests** — tests cover deceptive hostnames, embedded URL credentials, registered-host boundaries, prompt-injection instruction wording, and HTTPS-only portal links.

## Existing safeguards observed
- Intake accepts a local file and does not download the supplied source URL.
- Symlink inputs are rejected by the intake and extraction scripts.
- File intake and extraction enforce a 100 MB upper bound.
- Redistribution permission defaults to unknown; private archival only occurs when explicitly marked permitted.
- New intake records remain pending review and legal status unknown.
- Version checksums and document/version relationships are checked.
- Retrieval rejects passages missing required provenance and warns that traceability does not prove authority or current force.
- Research-agent output rejects fabricated citation IDs and uncited factual claims.
- Portal uses a local file picker, makes no index upload request, escapes indexed text, and offers a clear-index control.

## Important residual risks / work still required
- **Prompt injection is not solved by prompt wording alone.** Any future model adapter needs adversarial tests and a design that treats retrieved text as data, limits tools/actions, and requires human review.
- **Citation membership is not semantic verification.** A citation ID being present does not prove that a passage supports the associated claim.
- **Source authenticity and legal currency remain manual review tasks.** The system does not determine commencement, amendments, repeal, consolidation, or whether an instrument is currently in force.
- **File intake TOCTOU hardening (Phase 11):** intake opens the supplied file with `O_NOFOLLOW`, checks that the opened descriptor is a regular file, and performs size/hash checks against that descriptor. Archive copies reopen without following symlinks, copy from the descriptor, and verify source identity stability, byte count and checksum before atomic publication. This reduces final-component symlink-swap and path-reopen races; it does not protect against every possible mutation by a privileged process or hostile filesystem.
- **Retrieval-index resource limits (Phase 11):** retrieval rejects indexes larger than 50 MiB or 100,000 records before processing records. Index generation applies the same record and serialized-byte caps. These are conservative local defaults, not a guarantee against all memory or CPU exhaustion.
- **Archive and register writes:** intake now uses a replayable transaction journal and atomic replacement of each register; the journal is retained until both snapshots are written and is replayed on the next intake after interruption. An exclusive local lock prevents concurrent intake writers from overwriting one another. Abrupt termination can leave a stale lock that requires an operator to confirm no process is active before removing it. This is not a distributed lock for shared multi-machine storage.
- **No authentication or hosted deployment:** the portal is local-only. If deployed publicly, access control, transport security, rate limits, logging, privacy review, backups, and security testing are required.
- **No legal professional review:** human legal review and authoritative-source checks remain necessary before publishing or relying on legal content.

## Acceptance status
Code changes and regression tests are committed to this branch. Test execution must be reported separately; a committed test is not evidence that it passed. Do not describe this milestone as a security certification or as completion of legal validation.

## Operating rule
Do not ingest personal case details, client identities, confidential correspondence, or privileged documents into a future hosted or third-party AI service without a separate privacy and legal approval. No paid service or API is authorised by this milestone.


## Intake reliability update — 2026-11-11

The Phase 12-D transaction-safe intake change adds journal-based recovery and checksum-verified temporary archive publication. A follow-up single-writer lock now prevents concurrent intake processes from loading and overwriting the same register snapshots. The lock is local to one working copy; it is not a distributed coordination mechanism. These controls reduce write-corruption risks but do not constitute a security certification.
