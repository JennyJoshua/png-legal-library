#!/usr/bin/env python3
"""Citation-forward question-and-answer presentation for PNG legal research."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from legal_research_agent import research


def format_citation(item, number):
    location = item.get("location") or {}
    parts = [item.get("document_title") or item.get("document_id") or "Untitled source"]
    if item.get("number"):
        parts.append("section " + str(item["number"]))
    elif item.get("title"):
        parts.append(str(item["title"]))
    ref = location.get("source_reference")
    if ref:
        parts.append(str(ref))
    parts.append("version " + str(item.get("version_id", "unknown")))
    return {"number": number, "label": "[" + str(number) + "]", "text": ", ".join(parts),
            "citation_id": item.get("citation_id"), "document_id": item.get("document_id"),
            "version_id": item.get("version_id"), "source_checksum_sha256": item.get("source_checksum_sha256"),
            "source_url": item.get("source_url"), "location": location}


def build_qa_response(question, index_path, model=None, match="all", limit=8):
    result = research(question, index_path, model=model, match=match, limit=limit)
    status = result.get("status")
    if status == "insufficient_evidence":
        return {"status": status, "question": question,
                "answer": "I could not find sufficient traceable evidence in the available PNG legal library to answer this question.",
                "claims": [], "citations": [], "follow_up_needed": True,
                "warning": "Do not treat the absence of a search result as proof that no relevant law exists."}
    if status == "model_not_configured":
        citations = [format_citation(item, i + 1) for i, item in enumerate(result.get("evidence", []))]
        return {"status": status, "question": question,
                "answer": "Relevant passages were found, but an AI model is not connected. No legal answer has been generated.",
                "claims": [], "citations": citations, "follow_up_needed": True,
                "warning": result.get("warning")}
    raw_citations = result.get("citations", [])
    citation_map = {item.get("citation_id"): item for item in raw_citations}
    used_ids = []
    for claim in result.get("claims", []):
        for cid in claim.get("citation_ids", []):
            if cid not in used_ids:
                used_ids.append(cid)
    citations = [format_citation(citation_map[cid], i + 1)
                 for i, cid in enumerate(used_ids) if cid in citation_map]
    labels = {item["citation_id"]: item["label"] for item in citations}
    claims = []
    for claim in result.get("claims", []):
        claims.append({"text": claim["text"],
                       "citation_labels": [labels[cid] for cid in claim["citation_ids"] if cid in labels]})
    if result.get("insufficient_evidence"):
        status = "insufficient_evidence"
    return {"status": status, "question": question, "answer": result.get("answer", ""),
            "claims": claims, "citations": citations,
            "limitations": result.get("limitations", []),
            "follow_up_needed": bool(result.get("insufficient_evidence")),
            "warning": result.get("warning")}


def render_text(response):
    lines = ["Question: " + response["question"], "", response["answer"]]
    if response.get("claims"):
        lines.extend(["", "Evidence-linked claims:"])
        for claim in response["claims"]:
            lines.append("- " + claim["text"] + " " + " ".join(claim["citation_labels"]))
    if response.get("citations"):
        lines.extend(["", "Sources:"])
        for citation in response["citations"]:
            lines.append(citation["label"] + " " + citation["text"])
            if citation.get("source_url"):
                lines.append("  " + citation["source_url"])
    if response.get("limitations"):
        lines.extend(["", "Limitations:"])
        lines.extend("- " + item for item in response["limitations"])
    if response.get("warning"):
        lines.extend(["", "Important: " + response["warning"]])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="PNG legal Q&A with source-linked citations.")
    parser.add_argument("question")
    parser.add_argument("--index", default=str(ROOT / "legal-index" / "index.json"))
    parser.add_argument("--match", choices=("all", "any"), default="all")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args(argv)
    try:
        response = build_qa_response(args.question, args.index, match=args.match, limit=args.limit)
        print(json.dumps(response, indent=2, ensure_ascii=False) if args.format == "json" else render_text(response))
        return 0
    except Exception as exc:
        print("LEGAL Q&A ERROR: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
