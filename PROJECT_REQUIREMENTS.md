# PNG Legal Library — Project Requirements

## 1. Purpose

Build a public, searchable, downloadable knowledge library of Papua New Guinea legal information.

The library will support:
- Online legal research and AI-assisted responses.
- Downloadable legal information for offline use.
- Automated monitoring of approved legal sources.
- Verification and tracking of legal document changes.
- Future integration with a website and Android application.

## 2. Core Principles

1. Prefer official PNG legal and government sources.
2. Record the original source of every document.
3. Track document versions, verification dates and legal status.
4. Never assume that an online document represents current law.
5. Require human review for significant legal-status changes.
6. Keep the library independent of any particular AI provider.
7. Support offline access through downloadable packages.
8. Prefer free and open-source tools.
9. Never configure paid AI services or automatic paid fallbacks without explicit approval.
10. Respect copyright, licensing, privacy and redistribution restrictions.
11. Never publish confidential user case information.
12. Preserve an auditable history of legal-content changes.

## 3. Legal Knowledge Categories

The library may include:

- Constitution of Papua New Guinea.
- Acts of Parliament.
- Regulations and subsidiary legislation.
- Official gazettes and legal notices.
- Court judgments.
- Government procedures and official forms.
- Legal aid and public legal assistance information.
- Plain-language legal guides linked to supporting authorities.

## 4. Document Verification

Every document should record, where available:

- Document ID and title.
- Document type and jurisdiction.
- Issuing authority.
- Original source URL.
- Publication and retrieval dates.
- Commencement, amendment or repeal information.
- Verification status and last verification date.
- Copyright and redistribution assessment.
- Version history and related documents.

Use explicit statuses such as:

- DISCOVERED
- PENDING_REVIEW
- VERIFIED
- SUPERSEDED
- REPEALED
- STATUS_UNKNOWN

Unknown information must remain unknown until verified.

## 5. GitHub Automation

GitHub Actions should eventually:

- Monitor approved sources for changes.
- Identify newly published documents.
- Generate change reports.
- Validate documents and metadata.
- Create review issues or pull requests.
- Rebuild search indexes.
- Generate downloadable offline packages.

Automation must not independently declare a law current or in force merely because a document was discovered or updated.

## 6. AI Integration

The future AI agent should:

1. Identify the user's legal question.
2. Search the legal knowledge library.
3. Retrieve relevant legal provisions.
4. Check document status and verification information.
5. Prepare a plain-language explanation.
6. Cite supporting documents and provisions.
7. Identify uncertainty and recommend appropriate assistance when necessary.

The AI must not invent legislation, section numbers, court decisions or official contact details.

The retrieval system must remain compatible with different AI providers.

## 7. Zero-Cost Requirement

Prefer free tools, public repositories and open-source software.

Document the usage limits of free services. The system must never silently switch to paid services or incur unapproved charges.

The offline legal library should remain useful even when AI services are unavailable.

## 8. Initial Development Stages

1. Establish repository policies and approved legal sources.
2. Create the document metadata schema.
3. Build the document register.
4. Implement source monitoring and validation.
5. Generate searchable legal indexes.
6. Create downloadable offline packages.
7. Develop the AI retrieval interface.
8. Integrate and test a suitable AI model.
9. Test legal accuracy, privacy and security.

## 9. Legal Safety

This repository provides legal information infrastructure, not a guarantee of legal advice.

AI-generated explanations must distinguish verified legal sources from interpretation and uncertainty.

High-risk matters must receive appropriate safeguards and referrals to qualified legal assistance.

## 10. Current Status

This document defines project requirements. It does not claim that the legal documents, verification processes, automation or AI services have already been implemented.
