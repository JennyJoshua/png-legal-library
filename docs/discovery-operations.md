# Legal source discovery operations

## What discovery does

The workflow identifies candidate URLs from the configured source registry and records basic technical access and page metadata. It does **not** establish authenticity, whether a law is in force, legal effect, completeness, or permission to copy or redistribute a resource.

Every candidate remains subject to human review.

## Runtime limits

The scheduled workflow uses conservative limits:

- 6-second network timeout per request
- 40 candidate URLs per source
- 12 candidate metadata checks per source
- 5 sitemap files per source
- sitemap recursion depth of 2
- 500 sitemap entries considered per sitemap
- 75-second budget per source
- 480-second overall discovery budget

Limits can be changed through the PNG_DISCOVERY_* environment variables in the workflow. The script clamps values to safe maximums.

If a source exceeds its budget, remaining checks for that source are skipped and recorded. If the overall budget is exhausted, remaining sources are explicitly marked as skipped. A source failure must not silently mark any source or legal resource as verified.

## Reviewing results

1. Open the latest Discover PNG legal sources workflow run.
2. Download the discovered-legal-source-review-package artifact.
3. Inspect discovered-source-candidates.json for discovery results and warnings.
4. Inspect legal-resource-review-queue.json for proposed queue additions.
5. Verify the identity and authority of each source independently.
6. Verify the exact document, version, commencement, amendments, and legal status using reliable evidence.
7. Confirm redistribution permission before storing or republishing document files.
8. Only a human reviewer may change review, legal-status, or permission fields.

The workflow intentionally does not commit the review queue to main. The artifact is a proposal for review, not an approved update. A reviewer may later prepare a separate pull request containing approved changes.

## Failure handling

HTTP 403 responses are recorded as access restrictions; the workflow must not attempt to bypass them. HTTP 404, 429, timeout, and network errors are recorded as technical outcomes. A technical failure does not establish that a source or document is invalid.

A partial report is useful: it must identify completed, failed, and skipped sources and retain the reason for each failure.
