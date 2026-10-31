# PDF and Word Document Processing

## What this milestone does

The extraction command accepts a local PDF or DOCX file and creates:
- a structured JSON result with source/version provenance and individual page or paragraph segments
- a plain-text file with explicit page or paragraph markers for search indexing

It does not download legal documents, change the original file, infer legal status, or certify the accuracy of extracted text.

## Prerequisite: register the source version first

Every extraction is tied to a document ID and a version ID in `data/document-versions.json`. The input file's SHA-256 checksum must exactly match that registered version. If the checksum differs, stop and register the new file as a new version with `scripts/intake_document.py` before extraction.

Install the processing dependencies:

```bash
python -m pip install -r requirements-processing.txt
```

## PDF extraction

```bash
python scripts/extract_document.py \
  --file ./downloads/example-act.pdf \
  --document-id example-act-2026 \
  --version-id 0123456789abcdef
```

Each PDF page is extracted separately and receives a stable `PDF page N` reference. The output includes a page count and extraction method for each page.

## Scanned PDF OCR (optional)

OCR requires the Python dependencies above and the Tesseract OCR system executable. On Ubuntu/Debian, an administrator can install it with:

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

Then run:

```bash
python scripts/extract_document.py \
  --file ./downloads/scanned-act.pdf \
  --document-id scanned-act \
  --version-id 0123456789abcdef \
  --ocr \
  --ocr-language eng
```

OCR is attempted only on pages with fewer than 40 embedded-text characters. OCR is limited to 200 pages per run; PDFs are limited to 1,000 pages. Install additional Tesseract language packs separately if needed. OCR can misread names, numbers, section symbols, punctuation and legal wording; compare every relied-upon passage with the original page image.

## Word extraction

```bash
python scripts/extract_document.py \
  --file ./downloads/example-rules.docx \
  --document-id example-rules \
  --version-id 0123456789abcdef
```

DOCX extraction preserves paragraph order, heading style/context, and table rows. DOCX files do not provide dependable printed page positions through this method, so references are paragraph and table-row identifiers, not page numbers. For authoritative page references, use the original Word/PDF layout.

## Output and privacy

By default, output is written to the local `extracted/` directory:
- `<version-id>.extraction.json`
- `<version-id>.extraction.txt`

The directory is git-ignored because extracted text may be copyrighted, confidential, or otherwise restricted. Do not commit extracted text to this public repository. Store and share outputs only where the source licence and applicable rules permit.

## Validation

```bash
python -m unittest discover -s tests -v
python scripts/validate_documents.py
```

The extraction result is checked against `schemas/extraction-result.schema.json` in automated tests.

## Known limitations

- Supported formats in this milestone: PDF and DOCX. Legacy DOC, image-only files, spreadsheets and HTML are not supported as direct inputs.
- OCR supports PDF pages only and requires Tesseract installed on the machine. OCR is bounded to 200 pages per run.
- Tables in DOCX are emitted as row text; complex merged cells and nested tables may need manual review.
- PDF extraction cannot guarantee perfect reading order in multi-column layouts, forms, marginalia, handwriting, or complex tables.
- Page/paragraph references are navigational aids, not a substitute for checking the original source.
- Extraction does not determine whether a document is current, in force, amended, authentic, or legally reusable.