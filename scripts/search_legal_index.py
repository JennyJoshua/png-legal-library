#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def terms(value):
    return re.findall(r"[a-z0-9]+", value.casefold())

def search(index_path, query, match="all", limit=10):
    data = json.loads(Path(index_path).read_text(encoding="utf-8"))
    query_terms = list(dict.fromkeys(terms(query)))
    if not query_terms:
        raise ValueError("Enter at least one searchable word or number.")
    results = []
    for record in data.get("records", []):
        haystack = " ".join(str(record.get(k) or "") for k in
                            ("document_title", "title", "number", "text", "source_reference", "source_id")).casefold()
        present = [term for term in query_terms if re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", haystack)]
        if (match == "all" and len(present) != len(query_terms)) or not present:
            continue
        score = sum(len(re.findall(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", haystack)) for term in present)
        if " ".join(query_terms) in haystack: score += 3
        results.append((score, record))
    results.sort(key=lambda x: (-x[0], x[1].get("document_id", ""), x[1].get("node_id", "")))
    keys = ("document_title", "document_id", "version_id", "kind", "number", "title",
            "source_reference", "structure_path", "source_url", "text", "source_checksum_sha256")
    return [{"score": score, **{k: record.get(k) for k in keys}} for score, record in results[:limit]]

def main(argv=None):
    parser = argparse.ArgumentParser(description="Search the local legal passage index.")
    parser.add_argument("query")
    parser.add_argument("--index", default=str(ROOT / "legal-index" / "index.json"))
    parser.add_argument("--match", choices=("all", "any"), default="all")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 100: parser.error("--limit must be between 1 and 100")
    try:
        print(json.dumps({"query": args.query, "results": search(args.index, args.query, args.match, args.limit)}, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"SEARCH ERROR: {exc}", file=sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
