# A1 (revised A1-R1): Parliament of PNG and Office of the Legislative Counsel (OLC) - Official Source Links

- Assignment IDs: PNGLL-M11-CLAUDE-A1 and PNGLL-M11-CLAUDE-A1-R1
- Prepared by: Claude
- Access date for all endpoints: 2026-11-03 (A1 and A1-R1 were both run on this date)
- Scope: only the National Parliament of Papua New Guinea and the Office of the Legislative Counsel (OLC). Online public sources only. No office, Registry or agency was contacted. No document files were downloaded or copied.
- Companion file: `claude-a1-parliament-olc-sources.csv` (one row per endpoint; it agrees with this report)

## Method and caveat (important for reading A1-R1)

Every check was made with an automated page-fetch tool, NOT a normal browser. The tool returns page text only, can open only URLs that were returned by an earlier search or page fetch, and obeys robots rules. Lists that a site loads dynamically (document tables, bill lists) may not appear in the text, so "no listing visible" means none appeared in the fetched text, not that none exists. The handover asked for a normal-browser check of the bill and notice paper lists; that could not be done here and remains open (see Unresolved items).

Result terms used in the CSV: `fetched_ok` (opened, content seen), `fetched_ok_no_listing_visible` (opened, no records or document links seen), `fetch_error_client` (tool reported a client error; status code not given), `blocked_robots` (site disallows automated access; not bypassed), `not_tested` (not opened; reason given), `search_snippet_only` (seen only in a search result).

## A1-R1 corrections

### 1. Bills & Legislations (and demo counterpart)

- https://parliament.gov.pg/bills-legislations/ was re-opened. It shows an introduction (a library of bills from recently passed to under debate, search and filter tools, tracking of bills through stages) but NO individual bill records and NO document links in the fetched text.
- https://demo.parliament.gov.pg/bills-legislations/ was NOT tested: the fetch tool refused it (the URL had not been returned by any search or page) and a search did not return it.
- https://demo.parliament.gov.pg/?p=6221 (a demo-host page titled Bills & Legislations, returned by search) was opened. Same introduction text only; no records or links.
- The Parliament site map lists the bills page at a different demo path, https://demo.parliament.gov.pg/bills-and-legislations/ . Not tested (demo host disallows automated access, see item 4).
- No example bill could be opened and verified, so none is recorded. Because no records were seen, the report cannot separate Bills under consideration, Bills passed and Acts. Nothing here treats a bill-stage label as proof that an Act is published or in force. The page text itself says only that the library covers bills from those "recently passed into law" to those under debate; that is a description by the site, not a verified list.
- Outcome: UNRESOLVED. Needs a normal-browser check.

### 2. Notice Papers

- https://parliament.gov.pg/notice-papers/ was opened in A1 earlier on 2026-11-03 (heading and navigation only, no entries visible) and was not re-fetched in A1-R1.
- https://www.parliament.gov.pg/notice-papers/2024 was NOT tested: the fetch tool refused it (not returned by any search or page) and a search for Parliament notice papers 2024 did not return it. The handover says a search result shows dated entries for 2024; I could not see that result, so no date or number coverage is recorded and no sample document link was opened.
- Outcome: UNRESOLVED. No coverage evidenced; no linked document tested.

### 3. Constitution PDFs

- https://parliament.gov.pg/constitution-of-png/ (opened in A1) shows a Download PDF link to https://demo.parliament.gov.pg/wp-content/uploads/2026/04/PNG-CONSTITUTION.pdf .
- https://demo.parliament.gov.pg/wp-content/uploads/2026/04/PNG-CONSTITUTION.pdf: NOT tested. The fetch tool refused it (URL not accepted as a prior result). No title, version or date seen.
- https://www.parliament.gov.pg/images/misc/PNG-CONSTITUTION.pdf: NOT tested, same reason. Third-party documents (for example UN Universal Periodic Review submissions at https://upr.info/sites/default/files/documents/2016-04/unesco_upr25_png_e_main.pdf and https://www.upr.info/sites/default/files/documents/2022-03/unesco_upr39_png_e_main.pdf) cite this address as a Parliament-hosted Constitution PDF. That shows the address was cited by others, not that it opens today or that it matches the other file.
- No comparison was made. No claim is made about which file, if either, is identical or authoritative.
- Outcome: UNRESOLVED. Both files untested.

### 4. Minutes of Proceedings: label and path

- Navigation menu label on the homepage and other pages opened: "Minutes of Proceeds", linking to https://parliament.gov.pg/minutes-of-proceeds/ . Footer "Quick Links" label on the same pages: "Minutes of Proceedings", linking to https://parliament.gov.pg/minutes-of-proceedings/ .
- https://parliament.gov.pg/minutes-of-proceeds/ : opened. Page title is "Minutes of Proceeds"; the on-page heading and breadcrumb read "Minutes of proceedings". No entries or document links visible. THIS is the only Minutes URL that opened.
- https://parliament.gov.pg/minutes-of-proceedings/ : the tool returned a client error (status code not reported).
- https://demo.parliament.gov.pg/minutes-of-proceedings/ (the demo path the breadcrumb and site map point to): blocked by robots for automated access; not tested.
- Outcome: PARTLY RESOLVED. Working fetch-tested URL: https://parliament.gov.pg/minutes-of-proceeds/ . Whether the footer path works in a normal browser is unknown. Site map observation: the entry labelled Questions for written answers points to the minutes-of-proceedings demo path (an apparent site mislink; not investigated).

### 5. Research and Publications

- The homepage (https://parliament.gov.pg/ , opened) has a tile labelled "Research and Publications" that links to https://parliament.gov.pg/press-releases/ .
- https://parliament.gov.pg/press-releases/ was opened: heading Press Releases, no entries visible. This is news material, not legal text, so it is recorded for completeness only.
- No separate Research and Publications page was found in the navigation menus or in the opened site map (https://parliament.gov.pg/wp/sitemap/ , canonical https://parliament.gov.pg/sitemap/ ). No legal or parliamentary research publications were identified; no URL was guessed.
- Outcome: nothing relevant confirmed.

## Endpoint summary

### Parliament of PNG (official site: parliament.gov.pg)

| Endpoint | Result |
|---|---|
| https://parliament.gov.pg/ | Opened. Navigation, Research and Publications tile. |
| https://parliament.gov.pg/bills-legislations/ | Opened. No bill records or document links in text. |
| https://demo.parliament.gov.pg/bills-legislations/ | Not tested (fetch tool refused). |
| https://demo.parliament.gov.pg/?p=6221 | Opened. Intro text only. |
| https://parliament.gov.pg/notice-papers/ | Opened in A1. No entries visible. |
| https://www.parliament.gov.pg/notice-papers/2024 | Not tested (fetch tool refused). |
| https://parliament.gov.pg/hansards/ | Opened in A1. No entries visible. |
| https://parliament.gov.pg/minutes-of-proceeds/ | Opened. No entries visible. |
| https://parliament.gov.pg/minutes-of-proceedings/ | Client error from fetch tool. |
| https://demo.parliament.gov.pg/minutes-of-proceedings/ | Blocked by robots; not tested. |
| https://parliament.gov.pg/constitution-of-png/ | Opened in A1. Download PDF link present. |
| https://demo.parliament.gov.pg/wp-content/uploads/2026/04/PNG-CONSTITUTION.pdf | Not tested (fetch tool refused). |
| https://www.parliament.gov.pg/images/misc/PNG-CONSTITUTION.pdf | Not tested (fetch tool refused). Cited by third parties. |
| https://parliament.gov.pg/press-releases/ | Opened. No entries visible. News, not legal. |
| https://parliament.gov.pg/wp/sitemap/ | Opened. Lists demo-host paths. |
| https://parliament.gov.pg/wp/terms-of-use/ | Opened in A1. Reuse terms below. |
| https://www.parliament.gov.pg/bills-and-legislation | Older address seen in a third-party catalogue. Not tested. |
| https://demo.parliament.gov.pg/ | Not opened. Demo host disallows automated access on at least the minutes path. Staging or live status unknown. |

### Office of the Legislative Counsel (OLC) - unchanged from A1

| Endpoint | Result |
|---|---|
| https://pnglaw.gov.pg/ and https://pnglaw.gov.pg/index.php | Opened in A1. OLC background and functions; no legislation list, revised-law index or download link seen in text; navigation menu not visible. |
| https://www.pmnec.gov.pg/office-of-the-legislative-council/ | Opened in A1. OLC objectives and KPIs; no legislation links. |
| https://paclii.org/pg/legis/num_act | THIRD PARTY (PacLII). Search snippet only. |

No OLC-owned page offering Acts, revised laws or bills for viewing or download was confirmed.

## Official versus third-party

- Official (owned by the institution): parliament.gov.pg pages (National Parliament); pnglaw.gov.pg (self-identifies as OLC; `.gov.pg` domain); pmnec.gov.pg OLC page (Department of Prime Minister and NEC). The demo.parliament.gov.pg host is on the Parliament domain but its status (staging or live) is unknown.
- Third party, NOT official: PacLII (paclii.org). Its pages carry the credit "Office of Legislative Counsel, PNG", which does not make PacLII an official publisher. No official page linking to PacLII was confirmed.
- Third-party documents that cite the www Constitution PDF address (UPR submissions above): citations only, not Parliament pages.
- Third-party catalogue (secondary evidence only): Global Legal Information catalogue (gli.inp.pan.pl) record 20220000429 describes the Parliament bills-and-legislation site as holding legal acts from 2012 to the present, record dated 2014. Not verified.

## Reuse and licensing terms seen

Parliament Terms of Use (https://parliament.gov.pg/wp/terms-of-use/): content is protected by copyright unless otherwise stated; it may be reproduced for personal, non-commercial use with proper acknowledgment; no warranty of completeness or reliability. No open licence seen. No reuse terms found for pnglaw.gov.pg or the pmnec.gov.pg OLC page in the text fetched. This work records links only and copies no files.

## Searchable / downloadable / metadata

- Bills and Legislations page text mentions search and filter tools; not confirmed working (no records appeared).
- Constitution: a PDF download link exists on the Parliament page; neither PDF was opened, so text layer, searchability and metadata are unknown.
- OLC: nothing downloadable or searchable confirmed.

## Unresolved items

1. Normal-browser check of the Bills & Legislations list (both hosts) for bill records, document links and bill stages.
2. Notice Papers: 2024 index and a sample linked document untested; no coverage evidenced.
3. Both Constitution PDFs untested; no comparison made.
4. Whether the footer path /minutes-of-proceedings/ works in a browser; the demo-host pages are blocked to automated tools.
5. Coverage periods are not evidenced for any official endpoint.
6. pnglaw.gov.pg inner pages not found (menu absent from fetched text); no URLs guessed.
7. Status of demo.parliament.gov.pg (staging or live) unknown.

## Legal safeguards

Accessibility of a page or file is not evidence that a law is current, in force, repealed or authoritative. Nothing here states the legal status of any document. No document numbers, dates, coverage periods or URLs were invented.
