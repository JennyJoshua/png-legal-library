# Phase 1 Task 1 — Test Report

Date: 31 October 2026
Branch target: phase1/discovery-reliability
Test environment: isolated Python 3.12 sandbox

## Automated checks

- Python bytecode compilation: PASS for discovery, merge, validation, and test modules.
- Unit tests: PASS — 12 tests.
- Existing legal-register validation: PASS.
- JSON schemas and metadata consistency: PASS.

## Unit-test coverage

- Reject unsupported URL schemes and credential-bearing URLs.
- Remove tracking parameters and URL fragments.
- Reject malformed ports.
- Parse namespaced and malformed sitemap XML safely.
- Classify candidate URLs as suggestions only.
- Convert HTTP 403 to a recorded forbidden result.
- Stop network work after a source budget is exhausted.
- Enforce sitemap recursion depth.
- Preserve existing human review status, notes, and reviewer identity during merge.
- Add new candidates with pending-review, status-unknown, and redistribution-unknown defaults.
- Assert that the GitHub Actions workflow is read-only and does not push to main.

## Bounded live discovery smoke test

A bounded run against the configured public source homepages completed in 52.8 seconds with a 90-second overall budget and 15-second per-source budget.

- Parliament: partial time budget; 0 candidates.
- Judiciary: partial time budget; 5 candidates.
- PacLII: completed; 0 candidates.
- DJAG: completed; 20 candidates.
- Ombudsman Commission: partial time budget; 0 candidates.

The run wrote a report despite partial source outcomes. This is a technical smoke test only. It does not validate source authenticity, the legal status of any document, or copying/redistribution rights.

## Review queue integration

The merge script processed 25 candidates in the isolated workspace. All 25 were added with pending_review, status_unknown, and redistribution_permission unknown. Existing reviewer decisions were preserved in unit tests.

The existing validator passed with 25 queue candidates. The generated queue was not copied into the repository branch because live discovery candidates must be individually reviewed before being retained in the project data.

## Workflow safety

- Workflow permissions reduced to contents: read.
- Checkout credentials are not persisted.
- Workflow uploads the discovery report and proposed queue as a 30-day artifact.
- Workflow no longer commits or pushes to main.
- No pull request is automatically merged.
- No legal candidate is automatically approved.

## Limitations and next checks

- The live smoke test used conservative, shorter-than-production limits to prove bounded execution; scheduled workflow settings are documented in the workflow.
- GitHub Actions must run the workflow after branch review to confirm runner-specific behavior.
- Candidate URLs still require human source and legal verification.
