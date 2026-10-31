#!/usr/bin/env python3
"""Provider-neutral, evidence-first orchestration for the PNG legal research agent.

No model, network service, or paid API is bundled. Supply a trusted local/free
provider adapter explicitly when one is selected and reviewed.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from retrieve_legal_evidence import retrieve

SYSTEM_INSTRUCTIONS = """You are a legal research assistant for Papua New Guinea materials.
You are not a lawyer and must not present your output as legal advice.
Use ONLY the supplied evidence passages. Do not rely on memory or outside facts.
For every factual legal proposition, attach one or more citation_id values from
the supplied evidence. Never invent a source, citation, section, date, legal
status, amendment, commencement, or court decision.
If the evidence does not answer the question, say so plainly and identify what
additional authoritative material is needed. Distinguish what the passage says
from any inference. Do not claim a law is current or in force unless the evidence
explicitly and reliably establishes that fact.
Return JSON with: answer (string), claims (array of {text, citation_ids}),
limitations (array of strings), and insufficient_evidence (boolean)."""

def build_model_request(question, evidence):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("A research question is required.")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("results"), list):
        raise ValueError("Evidence must be a retrieval result containing a results array.")
    return {
        "system": SYSTEM_INSTRUCTIONS,
        "user": json.dumps({
            "question": question,
            "evidence": evidence["results"],
            "instruction": "Answer using only these passages. Return the required JSON object."
        }, ensure_ascii=False)
    }

def validate_model_answer(answer, evidence):
    if not isinstance(answer, dict):
        raise ValueError("Model response must be a JSON object.")
    if not isinstance(answer.get("answer"), str) or not answer["answer"].strip():
        raise ValueError("Model response must include a non-empty answer.")
    claims = answer.get("claims")
    if not isinstance(claims, list):
        raise ValueError("Model response claims must be an array.")
    allowed = {item.get("citation_id") for item in evidence.get("results", [])
               if isinstance(item, dict) and item.get("citation_id")}
    checked = []
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict) or not isinstance(claim.get("text"), str) or not claim["text"].strip():
            raise ValueError(f"Claim {i + 1} must contain text.")
        ids = claim.get("citation_ids")
        if not isinstance(ids, list) or not ids:
            raise ValueError(f"Claim {i + 1} has no supporting citation.")
        unknown = [cid for cid in ids if cid not in allowed]
        if unknown:
            raise ValueError(f"Claim {i + 1} contains citation IDs not present in retrieved evidence.")
        checked.append({"text": claim["text"], "citation_ids": ids})
    limitations = answer.get("limitations", [])
    if not isinstance(limitations, list) or not all(isinstance(x, str) for x in limitations):
        raise ValueError("Limitations must be an array of strings.")
    insufficient = answer.get("insufficient_evidence", False)
    if not isinstance(insufficient, bool):
        raise ValueError("insufficient_evidence must be a boolean.")
    if not checked and not insufficient:
        raise ValueError("An answer without cited claims must be marked insufficient_evidence.")
    return {
        "answer": answer["answer"],
        "claims": checked,
        "limitations": limitations,
        "insufficient_evidence": insufficient,
        "citations": [item for item in evidence["results"]
                      if item.get("citation_id") in {cid for c in checked for cid in c["citation_ids"]}],
        "warning": "AI-assisted legal research only, not legal advice. Verify every cited passage against the authoritative current original."
    }

def research(question, index_path, model=None, match="all", limit=8):
    evidence = retrieve(index_path, question, match=match, limit=limit)
    if not evidence["results"]:
        return {
            "status": "insufficient_evidence",
            "answer": "I could not find traceable passages in the available index that answer this question.",
            "claims": [],
            "citations": [],
            "missing_evidence": True,
            "rejected_untraceable_records": evidence["rejected_untraceable_records"],
            "warning": evidence["warning"]
        }
    if model is None:
        return {
            "status": "model_not_configured",
            "question": question,
            "evidence": evidence["results"],
            "message": "Relevant passages were found, but no language model is configured. No legal answer has been generated.",
            "warning": evidence["warning"]
        }
    request = build_model_request(question, evidence)
    raw_answer = model(request)
    validated = validate_model_answer(raw_answer, evidence)
    validated["status"] = "answer_generated" if not validated["insufficient_evidence"] else "insufficient_evidence"
    validated["question"] = question
    return validated

def main(argv=None):
    parser = argparse.ArgumentParser(description="Evidence-first PNG legal research agent.")
    parser.add_argument("question")
    parser.add_argument("--index", default=str(ROOT / "legal-index" / "index.json"))
    parser.add_argument("--match", choices=("all", "any"), default="all")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    try:
        result = research(args.question, args.index, match=args.match, limit=args.limit)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print("LEGAL RESEARCH AGENT ERROR: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
