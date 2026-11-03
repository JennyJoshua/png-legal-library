# PNG Legal Library — B1: National Gazette Online Archive Discovery

**Assignment ID:** PNGLL-M11-GROK-B1  
**Researcher:** Grok  
**Date:** 2026-11-03  
**Scope:** Source discovery only (public online entry points for Papua New Guinea National Gazettes). No full inventory, no PDF redistribution, no offline requests.

## Summary of Findings

No single official PNG Government website hosts a complete, searchable, downloadable digital archive of the National Gazette. The Government Printing Office (Muruk Haus, Kumul Avenue, Waigani; P.O. Box 1280, Port Moresby) remains the primary publisher and physical distributor. Online access is provided almost exclusively through third-party legal-information repositories.

The dominant public online source is **PacLII** (Pacific Islands Legal Information Institute). It maintains year-indexed pages of individual National Gazette issues (G-series general notices and related special/public-service issues) from 1975 onward, with PDFs for many issues. Coverage is extensive but not guaranteed complete for every number; gaps exist in some years.

A secondary third-party source is **PNGi Portal**, which hosts compiled multi-issue PDF bundles for selected ranges (especially 2020–2023 and some earlier post-Independence material). These are downloadable and name-searchable within the portal’s governance-reporting corpus.

National Library of Australia holds catalogue records and a digitised online version link for the National Gazette series (from No. 1, 16 Sep 1975). Access may be subject to bot-protection or institutional restrictions. Older territorial gazettes (pre-1975) appear in NLA and UK National Archives catalogues (physical or limited digitisation).

No evidence was found of a live official .gov.pg full-text archive or index maintained by the Government Printing Office, Department of Justice & Attorney-General, or Office of the Legislative Counsel.

## Sources Documented

See companion CSV for structured fields. Key sources:

1. **PacLII – Papua New Guinea Government Gazettes**  
   - URL: https://www.paclii.org/pg/other/PGGovGaz/  
   - Owner: Pacific Islands Legal Information Institute (University of the South Pacific / AustLII partnership)  
   - Type: Third-party legal repository  
   - Material: National Gazette issues (G-series), special issues, public-services issues  
   - Coverage evidence: Year indexes 1975–2025 listed; individual PDFs linked (e.g., 2025/G34, 2023 issues, earlier years). Recent pages show hundreds of issues per year.  
   - Access: Free public; searchable (database / name / recent). PDF download.  
   - Limitations: Cloudflare protection can block automated / certain IP access; completeness per year not independently verified; some years may have missing numbers.  
   - Sample tests: Year index pages and individual PDF URLs are indexed and return content in search results; direct automated fetch from this environment received 403. Human browser access confirmed in prior public indexing.

2. **PNGi Portal – National Gazette collections**  
   - URL base: https://pngiportal.org/ (directory entries such as /directory/national-gazette-g181-231-2023)  
   - Owner: PNGi (governance / anti-corruption reporting portal)  
   - Type: Third-party  
   - Material: Compiled National Gazette PDF ranges (e.g., G1–65 2023, G181–231 2023, G233–300 2023, selected 1975 and 2020–2022 bundles).  
   - Coverage evidence: Explicit range titles and downloadable PDFs; notes on missing numbers within ranges.  
   - Access: Free, no registration; full-text searchable by person/company name across the portal; direct PDF download.  
   - Limitations: Selective (not a complete chronological archive); focused on governance-relevant content; last major company-data cross-reference noted as June 2022.

3. **National Library of Australia – Papua New Guinea National Gazette**  
   - Catalogue: https://catalogue.nla.gov.au/catalog/733547  
   - Digitised link referenced: https://nla.gov.au/nla.obj-3050301038  
   - Owner: National Library of Australia  
   - Type: Official library / third-party digitisation  
   - Material: Serial run of National Gazette (No. 1, 16 Sep 1975–)  
   - Coverage evidence: Catalogue life dates and “also available online” note.  
   - Access: Catalogue free; digitised object may require challenge or institutional access.  
   - Limitations: Bot-protection observed; copyright status varies by issue.

4. **Archontology – Papua New Guinea Sources**  
   - URL: https://www.archontology.org/nations/papua_new_guinea/01_sources.php  
   - Type: Third-party reference  
   - Points to PacLII (1975–2018+) and NLA for 1971–1975 Government Gazette / National Gazette transition.

5. **NICTA Public Register – Gazettes (selective)**  
   - URL: https://www.nicta.gov.pg/category/public-register/regulatory/gazettes/  
   - Owner: National Information & Communications Technology Authority (official)  
   - Material: Selected National Gazette notices relevant to ICT regulation (determinations, declarations).  
   - Coverage: Sparse, topic-limited; not a general archive.

6. **UK National Archives (physical / catalogue only)**  
   - Series DO 85 / DO 86: pre- and early Independence gazettes.  
   - Not online full-text; open access for on-site consultation.

## Sample Tests Performed

- PacLII year index pages (2025, recent, historical) are publicly listed and return structured issue lists with PDF links in search indexes.  
- Individual PDF URLs (e.g., …/2025/34.pdf, …/2023/…, …/2017/…) appear in web indexes with extractable text confirming National Gazette headers, publication details, and Government Printing Office imprint.  
- Direct automated HTTP requests from this environment to paclii.org returned 403 (Cloudflare). Browser tool also blocked.  
- PNGi Portal directory pages and download links for 2022–2023 compiled ranges load and offer PDF download; content extracts confirm authentic Gazette text and printer imprint.  
- NLA catalogue page loads; digitised object link triggers bot-protection challenge.  
- No official PNG Government Printing Office or central .gov.pg gazette portal was located via targeted searches.

## Evidence Gaps & Limitations

- Exact completeness of PacLII holdings per year cannot be asserted without exhaustive enumeration (outside scope).  
- No official digital “source of truth” archive identified.  
- Pre-1975 territorial gazettes have limited free online full-text.  
- Access reliability depends on third-party uptime and anti-bot measures.

## Recommended Follow-up (for later bounded task)

Priority lead: Systematic inventory of PacLII year indexes for a defined range (e.g., 2015–2025 or Independence-era 1975–1985), recording missing issue numbers and PDF availability, plus cross-check against PNGi Portal compiled bundles. Secondary: locate any OLC or DJAG internal indexes that may later be released.

## Files Produced

- `research/phase11/grok-b1-gazette-source-discovery.md` (this file)  
- `research/phase11/grok-b1-gazette-source-discovery.csv`

## GitHub Status

- Branch: `phase11/grok-gazette-b1` (created from `phase10/legal-corpus-foundation`)
- Files committed to this branch only.
- No shared central files modified.
- PR to be opened targeting `phase10/legal-corpus-foundation`.

**Research deliverables complete.**
