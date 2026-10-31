"""Small, dependency-free API helpers for the local PNG legal library portal."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from retrieve_legal_evidence import retrieve


def search_request(payload, index_path):
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    query = payload.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Enter a search term or legal question.")
    match = payload.get("match", "all")
    if match not in ("all", "any"):
        raise ValueError("Match must be 'all' or 'any'.")
    limit = payload.get("limit", 10)
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 50:
        raise ValueError("Result limit must be a whole number between 1 and 50.")
    return retrieve(index_path, query.strip(), match=match, limit=limit)


def health_response(index_path):
    path = Path(index_path)
    return {"status": "ready" if path.is_file() else "index_missing",
            "index_available": path.is_file(),
            "message": "Local legal index is available." if path.is_file()
                       else "No local index found. Build the index from reviewed source documents first."}
