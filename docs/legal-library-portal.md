# Milestone 8 — Local PNG Legal Library portal

## Overview
A static, mobile-friendly browser portal. It reads a locally generated JSON index selected by the user through a file picker. The index is not uploaded to a server.

## Open
Open `web/index.html` in a modern browser. Select the `index.json` created by `scripts/build_legal_index.py`. Enter search words, choose all-word or any-word matching, optionally filter by document, and inspect passage and provenance details.

## Privacy
The page reads the chosen index in browser memory only. It makes no API calls, does not transmit the index, and stores no uploaded file persistently. Source links open in a separate tab with `noopener noreferrer`.

## Scope
This is a local static portal, not a hosted public service. It does not display or host original PDF/DOCX files; it shows indexed passage text and recorded source links. Legal Q&A remains a separate local Python command (`scripts/legal_qa.py`). No AI provider or API is connected.

## Validation
The page must load a valid index, reject unsupported structures, search all/any terms, filter by document, escape indexed text before rendering, show traceability metadata, handle no-match cases, and clear loaded data on request.

## Legal warning
Search results are navigation aids only. The portal does not establish authenticity, current legal status, amendments, commencement or legal effect. Verify the authoritative current original. Not legal advice.
