#!/usr/bin/env python3
"""Extract searchable text from a version-registered PDF or DOCX file.

The source file is never modified. Extracted text is derivative working data,
not an authoritative legal record. OCR is optional and requires Tesseract.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "data" / "documents.json"
HISTORY = ROOT / "data" / "document-versions.json"
MAX_FILE_BYTES = 100 * 1024 * 1024
MAX_PDF_PAGES = 1000
MAX_OCR_PAGES = 200
OCR_MIN_CHARS = 40


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_provenance(document_id, version_id, checksum):
    if not re.fullmatch(r"[a-f0-9]{16}", version_id):
        raise ValueError("version-id must be a 16-character lowercase hexadecimal ID.")
    register = load_json(REGISTER)
    history = load_json(HISTORY)
    document = next((d for d in register.get("documents", []) if d.get("document_id") == document_id), None)
    if document is None:
        raise ValueError(f"Unknown document ID: {document_id}")
    version = next((v for v in history.get("versions", []) if v.get("version_id") == version_id), None)
    if version is None:
        raise ValueError(f"Unknown version ID: {version_id}")
    if version.get("document_id") != document_id:
        raise ValueError("The supplied version ID belongs to a different document ID.")
    if version.get("checksum_sha256") != checksum:
        raise ValueError("The file checksum does not match the registered version. Re-intake the file as a new version first.")
    return document, version


def clean_text(value):
    value = value.replace("\x00", "")
    return re.sub(r"[ \t]+", " ", value).strip()


def extract_pdf(path, use_ocr=False, ocr_language="eng", min_chars=OCR_MIN_CHARS):
    import fitz
    pages = []
    ocr_used = False
    with fitz.open(path) as pdf:
        if pdf.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported; provide an authorised, readable copy.")
        if len(pdf) > MAX_PDF_PAGES:
            raise ValueError(f"PDF exceeds the maximum of {MAX_PDF_PAGES} pages.")
        if use_ocr and len(pdf) > MAX_OCR_PAGES:
            raise ValueError(f"OCR is limited to {MAX_OCR_PAGES} pages per run.")
        for index, page in enumerate(pdf):
            text = clean_text(page.get_text("text", sort=True))
            method = "embedded_text"
            if use_ocr and len(text) < min_chars:
                try:
                    import pytesseract
                    from PIL import Image
                    if not shutil.which("tesseract"):
                        raise ValueError("Tesseract OCR executable is not installed.")
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text = clean_text(pytesseract.image_to_string(image, lang=ocr_language))
                    method = "ocr"
                    ocr_used = True
                except ImportError as exc:
                    raise ValueError("OCR dependencies are missing. Install pytesseract and Pillow.") from exc
            pages.append({
                "reference": f"PDF page {index + 1}",
                "page_number": index + 1,
                "text": text,
                "extraction_method": method,
                "character_count": len(text)
            })
    return pages, {"page_count": len(pages), "ocr_used": ocr_used}


def extract_docx(path):
    from docx import Document
    document = Document(path)
    segments = []
    heading = None
    paragraph_number = 0
    for paragraph in document.paragraphs:
        paragraph_number += 1
        text = clean_text(paragraph.text)
        if not text:
            continue
        style = paragraph.style.name if paragraph.style else "Normal"
        if style.lower().startswith("heading") or style.lower() == "title":
            heading = text
        segments.append({
            "reference": f"DOCX paragraph {paragraph_number}",
            "paragraph_number": paragraph_number,
            "heading_context": heading,
            "style": style,
            "text": text,
            "character_count": len(text)
        })
    for table_index, table in enumerate(document.tables, start=1):
        for row_index, row in enumerate(table.rows, start=1):
            cells = [clean_text(cell.text) for cell in row.cells]
            line = " | ".join(cell for cell in cells if cell)
            if line:
                segments.append({
                    "reference": f"DOCX table {table_index}, row {row_index}",
                    "table_number": table_index,
                    "row_number": row_index,
                    "heading_context": heading,
                    "text": line,
                    "character_count": len(line)
                })
    return segments, {"paragraph_count": paragraph_number, "table_count": len(document.tables), "ocr_used": False}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Local PDF or DOCX file")
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--version-id", required=True, help="Version ID from data/document-versions.json")
    parser.add_argument("--output-dir", default=str(ROOT / "extracted"))
    parser.add_argument("--ocr", action="store_true", help="OCR PDF pages with little/no embedded text")
    parser.add_argument("--ocr-language", default="eng", help="Installed Tesseract language code, default eng")
    return parser.parse_args(argv)


def run(args):
    path = Path(args.file).expanduser()
    if path.is_symlink() or not path.is_file():
        raise ValueError("Input must be an existing regular local file, not a symlink.")
    path = path.resolve()
    if path.stat().st_size < 1 or path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("File must be between 1 byte and 100 MB.")
    checksum = sha256_file(path)
    document, version = validate_provenance(args.document_id, args.version_id, checksum)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        segments, details = extract_pdf(path, args.ocr, args.ocr_language)
        format_name = "pdf"
    elif suffix == ".docx":
        if args.ocr:
            raise ValueError("OCR is currently supported for PDF pages only.")
        segments, details = extract_docx(path)
        format_name = "docx"
    else:
        raise ValueError("Unsupported file type. Supported formats: PDF and DOCX.")
    extracted_text = "\n\n".join(f"[{item['reference']}]\n{item['text']}" for item in segments)
    output = {
        "extraction_schema_version": "1.0",
        "document_id": args.document_id,
        "version_id": args.version_id,
        "document_title": document.get("title"),
        "source_url": version.get("source_url"),
        "source_id": version.get("source_id"),
        "source_checksum_sha256": checksum,
        "source_file_name": path.name,
        "source_media_type": version.get("media_type"),
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "format": format_name,
        "extraction_tool": "PyMuPDF" if format_name == "pdf" else "python-docx",
        "extraction_details": details,
        "segments": segments,
        "total_character_count": sum(item["character_count"] for item in segments),
        "warning": "Extracted text is a working derivative. Check the original document and page/paragraph reference before relying on any passage. OCR may contain errors."
    }
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{args.version_id}.extraction.json"
    text_path = output_dir / f"{args.version_id}.extraction.txt"
    json_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    text_path.write_text(extracted_text + "\n", encoding="utf-8")
    return {"result": "extracted", "segments": len(segments), "characters": output["total_character_count"],
            "json_output": str(json_path), "text_output": str(text_path), "ocr_used": details.get("ocr_used", False)}


def main(argv=None):
    try:
        print(json.dumps(run(parse_args(argv)), indent=2))
        return 0
    except Exception as exc:
        print(f"EXTRACTION ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())