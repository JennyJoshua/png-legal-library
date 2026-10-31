# Milestone 7 — Legal Q&A with citations

## Purpose
Present evidence-first research as a consistent question-and-answer response. Each model claim is connected to numbered source labels, and the source list preserves document identity, version, checksum, URL and page/paragraph reference.

## Run
After building the local index:

    python scripts/legal_qa.py "What does section 5 say about a court?"
    python scripts/legal_qa.py "What does section 5 say about a court?" --format json

The command uses the Milestone 6 agent. Until a model adapter is configured, it lists matching source passages but clearly says no AI answer has been generated. No-match queries return an insufficient-evidence response.

## Citation format
Numbered labels such as [1] appear beside claims. The source list identifies the document, section/title, original source reference, exact indexed version, checksum and source URL where available. These are traceability references, not a determination of current law.

## Acceptance criteria
- Every factual claim returned by the model has at least one citation ID already present in retrieved evidence.
- The Q&A layer maps citation IDs to numbered source labels and displays matching source metadata.
- No-match queries return insufficient evidence, not an invented answer.
- No configured model produces no generated answer.
- Missing or fabricated citations are rejected by the Milestone 6 validation layer.
- The output warns users to verify against authoritative current originals.

## Limitations
The tests use synthetic fixture records and a fake model adapter. This milestone does not connect a real model, authenticate source documents, check amendments or commencement, or establish current legal status. Citation membership does not prove semantic support; human review remains required. This tool is legal research assistance, not legal advice.
