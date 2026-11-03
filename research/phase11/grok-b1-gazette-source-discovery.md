# PNG Legal Library — B1: National Gazette Online Archive Discovery

**Assignment ID:** PNGLL-M11-GROK-B1 / B1-R1  
**Researcher:** Grok  
**Date:** 2026-11-03 (original); revised 2026-11-03 (B1-R1)  
**Scope:** Source discovery only (public online entry points for Papua New Guinea National Gazettes). No full inventory, no PDF redistribution, no offline requests.

## Summary of Findings

No complete official online archive of the Papua New Guinea National Gazette was identified in this research. The Government Printing Office remains the primary publisher and physical distributor. Online access is provided almost exclusively through third-party legal-information repositories.

The dominant public online source is **PacLII** (Pacific Islands Legal Information Institute). It maintains year-indexed pages of individual National Gazette issues (G-series) from 1975 onward, with linked HTML issue pages and associated PDFs for many issues. Coverage is extensive but completeness per year has not been exhaustively verified.

A secondary third-party source is **PNGi Portal**, which hosts compiled multi-issue PDF bundles for selected ranges (especially 2019–2023). These are selective, not a complete chronological archive.

National Library of Australia holds a catalogue record for the National Gazette series (from No. 1, 16 Sep 1975). The digitised-object access could not be fully tested due to bot-protection challenges.

## Sources Documented

See companion CSV for structured fields. Key sources with sample-access evidence:

### 1. PacLII – Papua New Guinea Government Gazettes

- **Main index:** https://www.paclii.org/pg/other/PGGovGaz/  
  - Result: Index page opened successfully (2026-11-03). Lists year links 1975–2025.

- **Recent year index (2025):** https://www.paclii.org/pg/other/PGGovGaz/2025/  
  - Result: Index page opened successfully. Lists individual issue links (e.g., G1–G74 for January, continuing through later months). Issue links are present as HTML pages (e.g., ../2025/34.html).

- **Historical year index (1985):** https://www.paclii.org/pg/other/PGGovGaz/1985/  
  - Result: Index page opened successfully. Lists individual issue links for 1985 (G1–G72).

- **Sample individual issue PDF (recent):** https://www.paclii.org/pg/other/PGGovGaz/2025/34.pdf  
  - Result: PDF content was retrievable via search-index extraction and returned National Gazette header text, publication details (No. G34, 16 January 2025), and Government Printing Office imprint. Direct automated fetch from some environments returns 403/Cloudflare; content is publicly indexed.

- **Sample individual issue PDF (historical):** https://www.paclii.org/pg/other/PGGovGaz/1985/68.pdf  
  - Result: PDF content was retrievable via search-index extraction and returned National Gazette header text (No. G69 / related 1985 issue), confirming historical coverage.

**Evidence states (PacLII):**
| Test item | Outcome |
|-----------|---------|
| Main year-list index opened | Yes |
| 2025 year index opened | Yes |
| 1985 year index opened | Yes |
| Issue links listed on year indexes | Yes |
| Sample PDF content retrieved (via index/search) | Yes (text extractable) |
| Direct PDF download in all environments | Variable (Cloudflare 403 observed in some automated contexts) |

Do not treat search-engine snippets alone as successful page/PDF access. Completeness of any single year is not asserted.

### 2. PNGi Portal – National Gazette collections

- **Directory page 1:** https://pngiportal.org/directory/national-gazette-g181-231-2023  
  - Result: Directory page content is publicly available and describes compiled range G181–231 (2023) with note of missing numbers. Download link displayed.

- **Directory page 2:** https://pngiportal.org/directory/national-gazette-g233-300-2023  
  - Result: Directory page content is publicly available and describes compiled range G233–300 (2023) with note of missing numbers. Download link displayed.

- **Directory page 3:** https://pngiportal.org/directory/national-gazette-g1-30-2022  
  - Result: Directory page content is publicly available and describes compiled range G1–30 (2022) with note of missing numbers. Download link displayed.

**Evidence states (PNGi):**
| Test item | Outcome |
|-----------|---------|
| Directory pages opened / content retrieved | Yes (three samples) |
| Download links displayed | Yes |
| PDF content itself opened/downloaded in this environment | Partial (page text and Gazette extracts visible in search results; full binary PDF download not independently confirmed in all test contexts) |

PNGi Portal remains selective (compiled ranges only) and is not a complete chronological archive.

### 3. National Library of Australia – Papua New Guinea National Gazette

- **Catalogue record:** https://catalogue.nla.gov.au/catalog/733547  
  - Stated series coverage: National Gazette from No. 1 (16 Sep 1975)–  
  - Result: Catalogue page is protected by Anubis bot-challenge (Proof-of-Work). Full catalogue metadata could not be freely retrieved in this automated environment. Prior public indexing confirms the record exists and notes online availability.

- **Digitised object (referenced):** https://nla.gov.au/nla.obj-3050301038  
  - Result: Digitised-object access triggers bot-protection / challenge. Free unrestricted access to the complete digital run was not confirmed.

**Evidence states (NLA):**
| Test item | Outcome |
|-----------|---------|
| Catalogue record reachable without challenge | No (Anubis challenge presented) |
| Digitised object freely accessible | Not confirmed (challenge encountered) |
| Series coverage statement | Catalogue life dates begin 16 Sep 1975 (from prior public records) |

Do not imply that the complete digital run is freely accessible.

### 4. Other sources (contextual)

- **Archontology:** https://www.archontology.org/nations/papua_new_guinea/01_sources.php — secondary pointer to PacLII and NLA.
- **NICTA Public Register (selective ICT gazettes):** https://www.nicta.gov.pg/category/public-register/regulatory/gazettes/ — official but topic-limited.
- **Government Printing Office:** Primary official publisher (physical). No public digital portal URL identified. Postal address and single-copy sale details appear on Gazette imprints; this is contextual information only and is not treated as an online endpoint.

## Sample Tests Performed (B1-R1)

All tests conducted 2026-11-03.

- PacLII main index, 2025 year index, and 1985 year index opened successfully.
- Individual issue links listed on both year indexes.
- Sample PDF URLs (2025/34.pdf and 1985 historical) returned extractable Gazette text via public indexes; Cloudflare 403 observed on some direct automated requests.
- Three PNGi directory pages returned content describing compiled ranges and displaying download links.
- NLA catalogue and digitised-object links encountered bot-protection challenges; free access not confirmed.

## Evidence Gaps & Limitations

- Exact completeness of PacLII holdings per year cannot be asserted without exhaustive enumeration (outside scope).
- Direct PDF binary download success varies by client/environment due to Cloudflare.
- NLA digitised run access restricted by challenge; full free accessibility not verified.
- PNGi coverage is selective by design.
- No complete official PNG Government Printing Office digital archive was identified in this research.

## Recommended Follow-up (for later bounded task)

Systematic inventory of selected PacLII year indexes (e.g., 2015–2025) recording missing issue numbers and PDF availability, plus cross-check against PNGi compiled bundles.

## Files Produced / Updated

- `research/phase11/grok-b1-gazette-source-discovery.md` (this file)
- `research/phase11/grok-b1-gazette-source-discovery.csv`

## GitHub Status

- Branch: `phase11/grok-gazette-b1` (existing, from `phase10/legal-corpus-foundation`)
- PR: https://github.com/JennyJoshua/png-legal-library/pull/3
- Only the two B1 deliverable files are modified.
- No shared central files changed.
- No merge performed.

**B1-R1 revision complete.**
