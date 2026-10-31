# Milestone 6 — AI legal research agent

## Purpose
Provide a provider-neutral orchestration layer that retrieves traceable passages, prepares a strict evidence-only model request, validates model citations against retrieved citation IDs, and refuses to generate an answer when no traceable evidence exists.

## Current capability
`scripts/legal_research_agent.py` is a local Python module and CLI. It uses the Milestone 5 retrieval engine. Without a model adapter it returns relevant evidence and explicitly reports `model_not_configured`; it never fabricates an answer. A future adapter is an explicitly injected Python callable receiving a request with `system` and `user` strings and returning the required JSON object.

## Model response contract
The adapter must return:
- `answer`: non-empty string
- `claims`: array of objects containing `text` and non-empty `citation_ids`
- `limitations`: array of strings
- `insufficient_evidence`: boolean

Every citation ID must exist in the retrieval result for that question. Invalid or invented citation IDs and uncited claims are rejected. This validates citation membership, not whether the cited text truly entails the claim; human review remains necessary.

## Run without a model
Build the local index, then run:

    python scripts/legal_research_agent.py "What does section 5 say about a court?"

The output will contain traceable evidence and `model_not_configured` until a provider adapter is explicitly installed/configured.

## Safety and limitations
This is legal research assistance, not legal advice or representation. It does not determine whether legislation is in force, authenticate source copies, check amendments, or establish legal effect. The model adapter is not bundled; no paid API or network connection is called. Do not connect a provider until its cost, privacy, data handling, availability in PNG, and free-tier limits have been checked. A citation-membership check is not a semantic entailment check; review answers against authoritative originals.
