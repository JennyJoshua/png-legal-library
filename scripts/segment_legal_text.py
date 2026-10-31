#!/usr/bin/env python3
import re

PART_RE = re.compile(r"^\s*(?:PART|CHAPTER)\s+([IVXLCDM]+|\d+|[A-Z])\s*[.\-—:]?\s*(.*)$", re.I)
DIVISION_RE = re.compile(r"^\s*(?:DIVISION|SUBDIVISION)\s+([IVXLCDM]+|\d+|[A-Z])\s*[.\-—:]?\s*(.*)$", re.I)
SUBPART_RE = re.compile(r"^\s*SUBPART\s+([IVXLCDM]+|\d+|[A-Z])\s*[.\-—:]?\s*(.*)$", re.I)
SECTION_RE = re.compile(r"^\s*(?:(?:SECTION|SEC\.?|S)\s+)?(\d+[A-Z]?)\s*[.)]\s*(.*)$", re.I)
SUBSECTION_RE = re.compile(r"^\s*\((\d+[A-Z]?)\)\s*(.*)$", re.I)
PARAGRAPH_RE = re.compile(r"^\s*\(([a-z])\)\s*(.*)$", re.I)
SUBPARAGRAPH_RE = re.compile(r"^\s*\(([ivxlcdm]+)\)\s*(.*)$", re.I)


def _heading(kind, number, title):
    return {"kind": kind, "number": number, "title": title.strip(), "label": f"{kind.title()} {number}"}


def segment_text(text, source_reference, document_id, version_id, start_id=1):
    nodes = []
    context = {"part": None, "division": None, "subpart": None, "section": None}
    current = None
    next_id = start_id

    def flush():
        nonlocal current
        if current and current["text"].strip():
            current["text"] = current["text"].strip()
            current["character_count"] = len(current["text"])
            current["structure_path"] = [x for x in (context["part"], context["division"], context["subpart"], context["section"]) if x]
            nodes.append(current)
        current = None

    def begin(kind, number, content):
        nonlocal current, next_id
        flush()
        current = {"node_id": f"{version_id}-{next_id:06d}", "document_id": document_id,
                   "version_id": version_id, "kind": kind, "number": number, "title": "",
                   "text": content.strip(), "source_reference": source_reference,
                   "page_number": None, "paragraph_number": None, "structure_path": []}
        page = re.search(r"PDF page (\d+)", source_reference)
        para = re.search(r"DOCX paragraph (\d+)", source_reference)
        if page: current["page_number"] = int(page.group(1))
        if para: current["paragraph_number"] = int(para.group(1))
        next_id += 1

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if current: current["text"] += "\n"
            continue
        m = PART_RE.match(line)
        if m:
            flush()
            context = {"part": _heading("part", m.group(1), m.group(2)), "division": None, "subpart": None, "section": None}
            continue
        m = DIVISION_RE.match(line)
        if m:
            flush()
            context["division"] = _heading("division", m.group(1), m.group(2))
            context["subpart"] = None
            context["section"] = None
            continue
        m = SUBPART_RE.match(line)
        if m:
            flush()
            context["subpart"] = _heading("subpart", m.group(1), m.group(2))
            context["section"] = None
            continue
        m = SECTION_RE.match(line)
        if m:
            number, rest = m.groups()
            context["section"] = _heading("section", number, rest)
            begin("section", number, rest)
            current["title"] = rest.strip()
            continue
        m = SUBSECTION_RE.match(line)
        if m and context["section"]:
            number, rest = m.groups()
            begin("subsection", f"({number})", rest)
            continue
        m = SUBPARAGRAPH_RE.match(line)
        if m and context["section"]:
            number, rest = m.groups()
            begin("subparagraph", f"({number})", rest)
            continue
        m = PARAGRAPH_RE.match(line)
        if m and context["section"]:
            number, rest = m.groups()
            begin("paragraph", f"({number})", rest)
            continue
        if current:
            current["text"] += ("\n" if current["text"] else "") + line
        else:
            begin("unstructured", None, line)
    flush()
    return nodes
