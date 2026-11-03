# A1: Parliament of PNG and Office of the Legislative Counsel (OLC) - Official Source Links

- Assignment ID: PNGLL-M11-CLAUDE-A1
- Prepared by: Claude
- Access date for all endpoints: 2026-11-03
- Scope: only the National Parliament of Papua New Guinea and the Office of the Legislative Counsel (OLC). Online public sources only. No office, Registry or agency was contacted. No document files were copied or downloaded.
- Companion file: `claude-a1-parliament-olc-sources.csv` (one row per endpoint)

## Method and caveat

Endpoints were found by web search and opened with an automated page-fetch tool. That tool returns page text only. Lists that a site loads dynamically (for example document tables) may not appear in fetched text, so "no listing visible" means none appeared in the fetched text, not that none exists. A person should open the pages in a normal browser to confirm. Where a URL was only seen in a search snippet or in another page's links and was not opened, the CSV says `not_tested` or `search_snippet_only`.

## Summary of findings

### Parliament of PNG (official site: parliament.gov.pg)

| Endpoint | Result |
|---|---|
| https://parliament.gov.pg/bills-legislations/ | Opened. Page describes a library of bills, search and filter tools and bill tracking. No bill or Act entries or document links appeared in fetched text. |
| https://parliament.gov.pg/notice-papers/ | Opened. Heading and navigation only; no entries visible. |
| https://parliament.gov.pg/hansards/ | Opened. Heading and navigation only; no entries visible. |
| https://parliament.gov.pg/minutes-of-proceeds/ | Linked in site navigation. Not opened. (Footer quick links use a different path, `/minutes-of-proceedings/`; the difference was not resolved.) |
| https://parliament.gov.pg/constitution-of-png/ | Opened. Offers a Download PDF link (see next row). |
| https://demo.parliament.gov.pg/wp-content/uploads/2026/04/PNG-CONSTITUTION.pdf | Link seen on the Constitution page. PDF not opened or downloaded. Hosted on a `demo.` subdomain. |
| https://parliament.gov.pg/wp/terms-of-use/ | Opened. Records the reuse terms (below). |
| https://www.parliament.gov.pg/bills-and-legislation | Older address, seen only as the access link in a third-party library catalogue. Not tested. |
| https://demo.parliament.gov.pg/ | Host that appears in search results and in page links. Not opened. Whether it is a staging or demo copy is unknown. |

Other Parliament navigation items seen but not investigated (outside the bounded task): Questions for Written Answers, Committees, Recommendation, Press Releases, Performance Reports.

### Office of the Legislative Counsel (OLC)

| Endpoint | Result |
|---|---|
| https://pnglaw.gov.pg/ and https://pnglaw.gov.pg/index.php | Opened. Page titled "Office of the Legislative Counsel :: Papua New Guinea"; describes OLC functions and services. No legislation list, revised-law index or download link appeared in fetched text. The navigation menu was not present in the fetched text. |
| https://www.pmnec.gov.pg/office-of-the-legislative-council/ | Opened. OLC page on the Department of Prime Minister and NEC site; states objectives and KPIs, including edition and printing of laws and OLC digitisation. No legislation links. |
| https://paclii.org/pg/legis/num_act | THIRD PARTY (PacLII). Search snippet only; not opened. See below. |

No OLC-owned page offering Acts, revised laws or bills for viewing or download was confirmed in this batch.

## Official versus third-party

- Official publication (owned by the institution): parliament.gov.pg pages (National Parliament), pnglaw.gov.pg (self-identifies as OLC; `.gov.pg` domain), pmnec.gov.pg OLC page (Department of Prime Minister and NEC).
- Third party, NOT official: PacLII (paclii.org). Search snippets show PacLII PNG pages that carry the attribution "Office of Legislative Counsel, PNG" and describe "selected sessional legislation" and consolidated reprints (one snippet for a regulation says it incorporates amendments made before 25 November 2006). This attribution does not make PacLII an official publisher. No official page that links to PacLII was confirmed. Example PacLII page seen in a snippet: https://paclii.org/pg/legis/consol_act/pr1992173.
- Third-party catalogue (secondary evidence only): Global Legal Information catalogue (gli.inp.pan.pl) record 20220000429 describes the Parliament bills-and-legislation site as providing PNG legal acts from 2012 to the present, with a 2014 publication date on the record. This is a catalogue description, not evidence taken from the Parliament site, and was not verified.

## Reuse and licensing terms seen

Parliament Terms of Use (https://parliament.gov.pg/wp/terms-of-use/): content is protected by copyright unless otherwise stated; it may be reproduced for personal, non-commercial use with proper acknowledgment; the site gives no warranty of completeness or reliability. No open licence was seen. No reuse terms were found for pnglaw.gov.pg or the pmnec.gov.pg OLC page in the text fetched. Note that this repository work records links only and does not copy files.

## Searchable / downloadable / metadata

- Parliament Bills & Legislations page text refers to search and filter tools; this was not confirmed working because no entries appeared. Metadata and full text availability: unknown.
- Constitution: a PDF download link exists on the Parliament page; the file was not opened, so text layer, searchability and metadata are unknown.
- OLC: nothing downloadable or searchable was confirmed.

## Evidence gaps

1. No Act, Bill or Hansard entry was seen on any Parliament list page in fetched text. A browser check is needed to see whether the lists render and what years they cover.
2. Coverage periods are not evidenced for any official endpoint.
3. The `minutes-of-proceeds` and `minutes-of-proceedings` paths were not tested.
4. The pnglaw.gov.pg navigation was not visible, so any inner legislation pages there were not found. No URL was guessed.
5. The status of `demo.parliament.gov.pg` (staging or live) is unknown.
6. The Constitution PDF and the old `www.parliament.gov.pg/bills-and-legislation` address were not opened.

## Legal safeguards

Accessibility of a page or file is not evidence that a law is current, in force, repealed or authoritative. Nothing here states the legal status of any document. No document numbers, dates, coverage periods or URLs were invented.
