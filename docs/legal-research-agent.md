# Milestone 6 — AI legal research agent

## Purpose
A provider-neutral, evidence-first orchestration layer for Papua New Guinea legal research. It retrieves passages using the Milestone 5 engine, prepares a strict evidence-only request for an explicitly supplied model adapter, and validates every returned citation ID against the retrieved evidence.

## Current capability
Run locally:

    python scripts/legal_research_agent.py "What does section 5 say about a court?"

When no model adapter is configured, the CLI returns traceable passages and reports `model_not_configured`. It does not generate or pretend to generate a legal answer. If no traceable passages match, it returns `insufficient_evidence`.

A future model adapter is a Python callable receiving a request with `system` and `user` strings and returning a JSON object. No provider, API key, network call, paid service, or model dependency is bundled.

## Response contract
The model must return:
- `answer`: non-empty string
- `claims`: array of objects containing `text` and non-empty `citation_ids`
- `limitations`: array of strings
- `insufficient_evidence`: boolean

Every citation ID must exist in the retrieval result for that question. Invented citation IDs and uncited claims are rejected. The check confirms citation membership, not whether the passage logically supports the claim; human review remains necessary.

## Safeguards and limitations
The agent must use only supplied passages, must not invent legal sources or status, and must state when evidence is insufficient. It does not authenticate source documents, determine whether legislation is in force, verify amendments or commencement, or provide legal advice. Always check authoritative current originals. A real model provider must be assessed separately for cost, PNG availability, privacy, data handling, and free-tier limits before connection.
