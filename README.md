# png-legal-library
A maintained, searchable and downloadable knowledge library of Papua New Guinea laws and legal information, with automated source monitoring and AI-assisted legal research.


## Document processing

The library includes version-linked PDF and DOCX text extraction. See [docs/document-processing.md](docs/document-processing.md) for setup, OCR requirements, safety limits, and usage. Extracted text is written locally to the git-ignored extracted/ folder and is not committed to the public repository.

## Legal document segmentation and keyword search

After extracting a registered document, build a local passage index with python scripts/build_legal_index.py and search it with python scripts/search_legal_index.py. See docs/legal-segmentation-and-search.md. The index and extracted text remain local and gitignored.
