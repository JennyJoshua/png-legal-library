# Milestone 8 — Local legal library search portal

A responsive, dependency-free browser portal for searching a locally prepared legal passage index.

## Run locally
From the repository root:

    python scripts/portal_server.py

Open http://127.0.0.1:8765 on the same computer. The server intentionally binds only to loopback and refuses public-network binding. Stop with Ctrl+C.

The index defaults to `legal-index/index.json`. To select another local index:

    python scripts/portal_server.py --index /absolute/path/to/index.json

## Features
- Search all or any query terms, with a bounded result count.
- Show document title and ID, passage excerpt, section/title, version, source page/paragraph, source URL, checksum and citation ID.
- Report whether a local index is available.
- Display a no-results message that does not imply no relevant law exists.

## API
- `GET /api/health`
- `POST /api/search` with JSON `{"query":"...","match":"all","limit":10}`

Request bodies are limited to 16 KB. The server sets no-store, nosniff and restrictive content-security headers. The browser uses text nodes for source text rather than interpreting source text as HTML.

## Limitations and legal safeguards
This is a local development portal, not production hosting. It is keyword search only. It does not generate AI legal answers, authenticate sources, determine current legal status, verify amendments or commencement, or provide legal advice. Keep the index and extracted source text local and gitignored. Verify every result against the authoritative original.
