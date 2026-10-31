# Legal document segmentation and keyword search

Milestone 4 builds a local, transparent keyword index from version-linked extraction files created in Milestone 3. It does not download source material, publish extracted text, decide legal status, or generate legal advice.

## Pipeline

1. Register a source document and its version using the intake workflow.
2. Extract its PDF or DOCX text with scripts/extract_document.py.
3. Build a local index using scripts/build_legal_index.py.
4. Search passages using scripts/search_legal_index.py.

Commands:

    python scripts/build_legal_index.py
    python scripts/search_legal_index.py "court competent jurisdiction"
    python scripts/search_legal_index.py "section 5" --match any --limit 20

Use --input-dir and --output-dir on the index builder to choose local directories. Use --index to search a specific index. The default index is legal-index/index.json.

## Segmentation and references

The initial structural parser recognises common Part, Chapter, Division, Subdivision, Subpart, section, subsection, paragraph and subparagraph forms. It retains text that does not match a known heading as unstructured rather than discarding it. A record carries document ID, version ID, source checksum, source URL/ID, structural path and original extraction reference.

PDF records retain the page reference from extraction. DOCX records retain paragraph references where available; a Word paragraph number is not a printed legal page number. Unusual formatting, headings split across lines, or multi-column PDFs may be classified as unstructured or split imperfectly. Treat segmentation as a navigation aid, not a legal interpretation. Always check the original.

## Search behaviour

Search is local keyword search, not semantic/AI search. By default all query terms must occur in a record (match all); match any returns records containing at least one term. Matching is case-insensitive and token-boundary based. Results are ranked by term frequency with a small exact-phrase bonus. Limit accepts 1 to 100.

## Privacy and legal safeguards

extracted/, legal-index/ and search-index/ are gitignored. Do not commit or publish working text or index data unless copyright and redistribution are confirmed by an authorised reviewer. Index records carry provenance so results can be checked against the exact source version.

The system does not establish authenticity, commencement, amendment status, current force, interpretation or legal effect. It does not alter legal status, reviewer notes or decisions. Search results are not legal advice and must not be relied on without checking the authoritative original and current law.
