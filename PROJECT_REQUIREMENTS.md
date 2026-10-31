# PNG Legal Library — Project Requirements

## 1. Purpose

Build a maintained, searchable, downloadable library of Papua New Guinea legal information and legal-document resources.

The project will support:
- Online legal research and AI-assisted responses.
- Downloadable legal information for offline use.
- Automated discovery and monitoring of legal sources.
- Verification and tracking of legal document changes.
- Future integration with a website and Android application.
- Future legal form search, filling, drafting, editing, and document export.

The repository will maintain three connected collections:

1. Legal knowledge base.
2. Legal forms and templates.
3. Legal reference documents.

These collections must remain logically separate while being linked through shared metadata.

## 2. Core Principles

1. Prefer authoritative PNG legal and government sources.
2. Record the original source of every resource.
3. Distinguish discovery from verification and interpretation.
4. Never assume an online document represents current law.
5. Never assume an online form is the latest or legally appropriate version.
6. Require human review for material legal-status changes and template approval.
7. Prefer free and open-source tools.
8. Never configure paid AI services or automatic paid fallbacks without explicit approval.
9. Respect copyright, licensing, privacy, website terms, and redistribution restrictions.
10. Never publish confidential user case information or completed documents containing personal data.
11. Preserve an auditable history of important legal-content changes.
12. Never fabricate laws, section numbers, court decisions, citations, or official contact details.

## 3. Legal Knowledge Base

The knowledge base will support legal research and AI-assisted explanations.

Potential content includes:

- Constitution of Papua New Guinea.
- Acts of Parliament.
- Regulations and subsidiary legislation.
- Organic laws.
- Official gazettes and legal notices.
- Court judgments and decisions.
- Court rules and practice directions.
- Reviewed legal principles.
- Plain-language legal explanations.
- Legal aid and public legal assistance information.

Suggested organisation:

knowledge-base/
- legislation/
- constitution/
- court-judgments/
- court-rules/
- legal-principles/

The structure is organisational guidance. It does not mean that all categories already contain verified material.

## 4. Legal Forms and Templates

A separate legal-forms collection will support the future creation and editing of legal documents.

Potential categories include:

- Court forms and applications.
- Affidavits.
- Statutory declarations.
- Agreements and contracts.
- Business and commercial documents.
- Land and property documents.
- Employment documents.
- Family, succession, and estate-related documents.
- Government applications and complaints.
