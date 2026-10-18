#!/usr/bin/env python3
"""Discover and classify candidate PNG legal resources.

Discovery does not establish authenticity, current legal status,
legal effect, or permission to redistribute a resource.
"""

import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import (
    quote,
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
    urldefrag,
    parse_qsl,
)
from urllib.request import Request, urlopen

try:
    import yaml
except ImportError:
    raise SystemExit(
        "Missing dependency PyYAML. Install it with: pip install PyYAML"
    )


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "sources" / "discovery-sources.yml"
REPORT = ROOT / "reports" / "discovered-source-candidates.json"

TIMEOUT = 15
MAX_BYTES = 2_000_000
MAX_URLS_PER_SOURCE = 300
MAX_METADATA_CHECKS_PER_SOURCE = 100
USER_AGENT = "PNG-Legal-Library-Discovery/2.1"

TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}

LEGAL_TERMS = re.compile(
    r"constitution|legislation|legislative|statute|"
    r"\bact\b|\bbill\b|\blaw\b|regulation|ordinance|"
    r"judgment|judgement|court|legal|gazette|"
    r"organic[-_ ]law|case[-_ ]law|justice|amendment|"
    r"practice[-_ ]direction|public[-_ ]notice|"
    r"parliament|policy|policies|report|reports|"
    r"village[-_ ]court|juvenile[-_ ]justice|"
    r"legal[-_ ]aid|law[-_ ]reform|court[-_ ]rule|"
    r"forms|decisions|rulings|commission",
    re.IGNORECASE,
)

DOCUMENT_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".rtf", ".odt",
    ".html", ".htm", ".txt",
)


class PageParser(HTMLParser):
    """Extract basic page metadata without executing scripts."""

    def __init__(self):
        super().__init__()
        self.title_parts = []
        self.h1_parts = []
        self.current_title = False
        self.current_h1 = False
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        tag = tag.lower()

        if tag == "title":
            self.current_title = True
        elif tag == "h1":
            self.current_h1 = True
        elif tag == "meta":
            key = (
                attrs.get("property")
                or attrs.get("name")
                or attrs.get("itemprop")
                or ""
            ).strip().lower()

            value = (
                attrs.get("content")
                or attrs.get("datetime")
                or ""
            ).strip()

            if key and value:
                self.meta[key] = value

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == "title":
            self.current_title = False
        elif tag == "h1":
            self.current_h1 = False

    def handle_data(self, data):
        value = data.strip()

        if not value:
            return

        if self.current_title:
            self.title_parts.append(value)

        if self.current_h1:
            self.h1_parts.append(value)


class LinkParser(PageParser):
    """Also collect links from the page."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag.lower() == "a":
            href = attrs_dict.get("href")
            if href:
                self.links.append(href.strip())

        super().handle_starttag(tag, attrs)


def safe_urljoin(base, candidate):
    """Resolve a link safely, returning None for malformed URLs."""

    if not isinstance(candidate, str):
        return None

    candidate = candidate.strip()

    if not candidate:
        return None

    try:
        # Quote spaces and unsafe URL characters while preserving
        # existing URL separators and already encoded characters.
        candidate = quote(
            candidate,
            safe=":/?#[]@!$&'()*+,;=%",
        )

        joined = urljoin(base, candidate)
        joined, _ = urldefrag(joined)
        parsed = urlparse(joined)

        if parsed.scheme.lower() not in ("http", "https"):
            return None

        if not parsed.hostname:
            return None

        if parsed.username or parsed.password:
            return None

        # Accessing .port can raise ValueError for malformed ports.
        _ = parsed.port

        return joined

    except (ValueError, TypeError, UnicodeError):
        return None


def normalize_url(base, candidate):
    """Normalize URLs and remove common tracking parameters."""

    candidate = safe_urljoin(base, candidate)

    if not candidate:
        return None

    try:
        parsed = urlparse(candidate)
        hostname = parsed.hostname.lower()

        if parsed.port:
            netloc = f"{hostname}:{parsed.port}"
        else:
            netloc = hostname

        query_items = []

        for key, value in parse_qsl(
            parsed.query,
            keep_blank_values=True,
        ):
            lowered = key.lower()

            if lowered.startswith("utm_"):
                continue

            if lowered in TRACKING_PARAMETERS:
                continue

            query_items.append((key, value))

        query_items.sort()

        path = parsed.path or "/"

        if path != "/":
            path = path.rstrip("/")

        return urlunparse((
            parsed.scheme.lower(),
            netloc,
            path,
            "",
            urlencode(query_items),
            "",
        ))

    except (ValueError, TypeError, UnicodeError):
        return None


def same_host(url, host):
    try:
        return urlparse(url).hostname == host
    except (ValueError, TypeError):
        return False


def is_document_url(url):
    try:
        return urlparse(url).path.lower().endswith(
            DOCUMENT_EXTENSIONS
        )
    except (ValueError, TypeError):
        return False


def classify_candidate(url, title=""):
    """Suggest a category from the URL and available title."""

    try:
        path = urlparse(url).path
    except (ValueError, TypeError):
        path = url

    text = (
        path + " " + (title or "")
    ).replace("_", " ").replace("-", " ").lower()

    categories = [
        ("constitution", r"\bconstitution\b"),
        ("legislation", r"\blegislation\b|\bstatute\b|\bacts?\b"),
        ("bills", r"\bbills?\b"),
        ("organic_laws", r"\borganic laws?\b"),
        ("regulations", r"\bregulations?\b"),
        ("court_judgments", r"\bjudg(?:ment|ement)s?\b|\brulings?\b"),
        ("court_rules", r"\bcourt rules?\b|\bpractice directions?\b"),
        ("legal_forms", r"\bforms?\b"),
        ("official_notices", r"\bgazette\b|\blegal notices?\b|\bpublic notices?\b"),
        ("court_information", r"\bcourt\b|\bcourts\b|\bcourt diary\b"),
        ("legal_policy", r"\bpolic(?:y|ies)\b"),
        ("official_reports", r"\breports?\b"),
        ("legal_research", r"\bresearch\b|\blaw journal\b|\bcase law\b"),
        ("legal_services", r"\blegal aid\b|\blegal services\b"),
        ("justice_programmes", r"\bjustice\b|\bvillage courts?\b|\bjuvenile justice\b"),
        ("parliamentary_records", r"\bparliament\b|\bparliamentary\b"),
    ]

    for category, pattern in categories:
        if re.search(pattern, text):
            return category

    if is_document_url(url):
        return "document_unclassified"

    return "legal_related_page_unclassified"


def fetch(url):
    """Fetch a public resource without bypassing access controls."""

    try:
        parsed = urlparse(url)

        if (
            parsed.scheme.lower() not in ("http", "https")
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            return {
                "ok": False,
                "status": None,
                "error": "Invalid or unsupported URL",
            }

        request = Request(
            url,
            headers={"User-Agent": USER_AGENT},
        )

        with urlopen(request, timeout=TIMEOUT) as response:
            body = response.read(MAX_BYTES + 1)

            if len(body) > MAX_BYTES:
                body = body[:MAX_BYTES]

            return {
                "ok": True,
                "status": response.getcode(),
                "final_url": response.geturl(),
                "content_type": response.headers.get(
                    "Content-Type", ""
                ),
                "body": body,
            }

    except HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": str(exc.reason),
        }

    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return {
            "ok": False,
            "status": None,
            "error": str(exc)[:500],
        }


def extract_date(parser):
    """Return an available publication or modification date."""

    preferred_keys = (
        "article:published_time",
        "datepublished",
        "date",
        "dc.date",
        "dcterms.date",
        "article:modified_time",
        "datemodified",
        "last-modified",
    )

    for key in preferred_keys:
        value = parser.meta.get(key)

        if value:
            return value[:100]

    return None


def inspect_page(url):
    """Check accessibility and extract basic page metadata."""

    result = fetch(url)

    metadata = {
        "http_status": result.get("status"),
        "access_result": "unreachable",
        "title": None,
        "available_date": None,
        "final_url": None,
        "error": result.get("error"),
    }

    if not result["ok"]:
        status = result.get("status")

        if status == 403:
            metadata["access_result"] = "forbidden"
        elif status == 404:
            metadata["access_result"] = "not_found"
        elif status == 429:
            metadata["access_result"] = "rate_limited"
        elif status is not None:
            metadata["access_result"] = "http_error"
        else:
            metadata["access_result"] = "network_error"

        return metadata

    metadata["final_url"] = result.get("final_url")
    metadata["error"] = None

    content_type = result.get("content_type", "").lower()

    if "html" not in content_type:
        metadata["access_result"] = "accessible_non_html"
        return metadata

    parser = PageParser()

    try:
        parser.feed(
            result["body"].decode("utf-8", errors="replace")
        )

        title = " ".join(parser.title_parts).strip()

        if not title:
            title = " ".join(parser.h1_parts).strip()

        metadata["title"] = title[:300] if title else None
        metadata["available_date"] = extract_date(parser)
        metadata["access_result"] = "accessible_html"

    except Exception as exc:
        # A malformed HTML page should not stop discovery.
        metadata["access_result"] = "accessible_html_parse_error"
        metadata["error"] = str(exc)[:500]

    return metadata


def parse_sitemap(data):
    urls = []

    try:
        root = ET.fromstring(data)
    except (ET.ParseError, ValueError):
        return urls

    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1].lower() == "loc":
            if element.text and element.text.strip():
                urls.append(element.text.strip())

    return urls


def get_sitemap_urls(base_url, host):
    """Find sitemap locations without crawling external hosts."""

    root = base_url.rstrip("/") + "/"

    robots_url = safe_urljoin(root, "robots.txt")
    common_sitemaps = [
        safe_urljoin(root, "sitemap.xml"),
        safe_urljoin(root, "sitemap_index.xml"),
    ]

    sitemap_urls = [
        url for url in common_sitemaps if url
    ]

    if robots_url:
        robots = fetch(robots_url)

        if robots["ok"]:
            text = robots["body"].decode(
                "utf-8", errors="replace"
            )

            for line in text.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemap = line.split(":", 1)[1].strip()
                    normalized = normalize_url(root, sitemap)

                    if normalized and same_host(normalized, host):
                        sitemap_urls.append(normalized)

    return list(dict.fromkeys(sitemap_urls))


def inspect_sitemap(
    sitemap_url, host, found, visited_sitemaps
):
    if sitemap_url in visited_sitemaps:
        return

    visited_sitemaps.add(sitemap_url)

    result = fetch(sitemap_url)

    if not result["ok"]:
        return

    for item in parse_sitemap(result["body"]):
        normalized = normalize_url(sitemap_url, item)

        if not normalized or not same_host(normalized, host):
            continue

        if normalized.lower().endswith(".xml"):
            if len(visited_sitemaps) < 20:
                inspect_sitemap(
                    normalized,
                    host,
                    found,
                    visited_sitemaps,
                )
            continue

        if (
            LEGAL_TERMS.search(normalized)
            or is_document_url(normalized)
        ):
            found.setdefault(normalized, "sitemap")

        if len(found) >= MAX_URLS_PER_SOURCE:
            return


def inspect_homepage_links(base_url, host, found):
    result = fetch(base_url)

    if not result["ok"]:
        status = result.get("status")

        if status == 403:
            result_name = "forbidden"
        elif status == 404:
            result_name = "not_found"
        elif status == 429:
            result_name = "rate_limited"
        else:
            result_name = "unreachable"

        return {
            "result": result_name,
            "http_status": status,
            "error": result.get("error"),
        }

    content_type = result.get("content_type", "").lower()

    if "html" not in content_type:
        return {
            "result": "not_html",
            "http_status": result.get("status"),
        }

    parser = LinkParser()

    try:
        parser.feed(
            result["body"].decode("utf-8", errors="replace")
        )
    except Exception as exc:
        return {
            "result": "html_parse_error",
            "http_status": result.get("status"),
            "error": str(exc)[:500],
        }

    malformed_links_skipped = 0

    for href in parser.links:
        normalized = normalize_url(
            result.get("final_url", base_url), href
        )

        if not normalized:
            malformed_links_skipped += 1
            continue

        if not same_host(normalized, host):
            continue

        if (
            LEGAL_TERMS.search(normalized)
            or is_document_url(normalized)
        ):
            found.setdefault(normalized, "homepage_link")

        if len(found) >= MAX_URLS_PER_SOURCE:
            break

    return {
        "result": "checked",
        "http_status": result.get("status"),
        "links_examined": len(parser.links),
        "malformed_links_skipped": malformed_links_skipped,
    }


def discover_source(source):
    base_url = source.get("url", "")

    try:
        parsed = urlparse(base_url)
        host = parsed.hostname
    except (ValueError, TypeError):
        host = None

    output = {
        "source_id": source.get("source_id"),
        "source_name": source.get("name"),
        "source_url": base_url,
        "source_type": source.get("source_type"),
        "source_review_status": source.get("review_status"),
        "discovery_status": "started",
        "homepage_check": None,
        "sitemaps_checked": 0,
        "duplicate_urls_removed": 0,
        "metadata_checks_performed": 0,
        "metadata_checks_skipped": 0,
        "candidate_errors": 0,
        "candidates": [],
        "notes": [
            "Candidate discovery only; legal status is not verified.",
            "Category labels are automated suggestions, not legal conclusions.",
            "Redistribution permission requires human review.",
            "A reachable page is not proof that its content is current.",
            "Malformed URLs and individual fetch failures are recorded or skipped without stopping the source run.",
        ],
    }

    if (
        not host
        or parsed.scheme.lower() not in ("http", "https")
        or parsed.username
        or parsed.password
    ):
        output["discovery_status"] = "invalid_source_url"
        output["error"] = "Invalid or unsupported source URL"
        return output

    found = {}

    output["homepage_check"] = inspect_homepage_links(
        base_url, host, found
    )

    sitemap_urls = get_sitemap_urls(base_url, host)
    visited_sitemaps = set()

    for sitemap_url in sitemap_urls:
        try:
            inspect_sitemap(
                sitemap_url,
                host,
                found,
                visited_sitemaps,
            )
        except Exception as exc:
            # Keep processing even if an individual sitemap is malformed.
            output["candidate_errors"] += 1
            output.setdefault("warnings", []).append(
                f"Sitemap processing failed: {str(exc)[:200]}"
            )

        time.sleep(0.2)

    output["sitemaps_checked"] = len(visited_sitemaps)

    unique_candidates = sorted(found.items())[
        :MAX_URLS_PER_SOURCE
    ]

    output["duplicate_urls_removed"] = (
        len(found) - len(unique_candidates)
    )

    for index, (url, discovery_method) in enumerate(
        unique_candidates
    ):
        metadata = {
            "http_status": None,
            "access_result": "not_checked",
            "title": None,
            "available_date": None,
            "final_url": None,
            "error": None,
        }

        if index < MAX_METADATA_CHECKS_PER_SOURCE:
            try:
                metadata = inspect_page(url)
            except Exception as exc:
                # One bad candidate must never abort the entire workflow.
                metadata["access_result"] = "inspection_error"
                metadata["error"] = str(exc)[:500]
                output["candidate_errors"] += 1

            output["metadata_checks_performed"] += 1
            time.sleep(0.2)
        else:
            output["metadata_checks_skipped"] += 1

        if metadata.get("error"):
            output["candidate_errors"] += 1

        title = metadata.get("title")

        candidate = {
            "candidate_id": hashlib.sha256(
                url.encode("utf-8")
            ).hexdigest()[:16],
            "url": url,
            "final_url": metadata.get("final_url"),
            "title": title,
            "available_date": metadata.get("available_date"),
            "discovery_method": discovery_method,
            "candidate_type": classify_candidate(
                url, title or ""
            ),
            "technical_access": metadata.get("access_result"),
            "http_status": metadata.get("http_status"),
            "access_error": metadata.get("error"),
            "review_status": "pending_review",
            "legal_status": "status_unknown",
            "legal_status_evidence": None,
            "redistribution_permission": "unknown",
        }

        output["candidates"].append(candidate)

    output["discovery_status"] = "completed"
    output["candidate_count"] = len(output["candidates"])

    return output


def main():
    if not REGISTRY.exists():
        raise SystemExit(
            "ERROR: sources/discovery-sources.yml was not found."
        )

    try:
        registry = yaml.safe_load(
            REGISTRY.read_text(encoding="utf-8")
        )
    except (OSError, yaml.YAMLError) as exc:
        raise SystemExit(
            f"ERROR reading source registry: {exc}"
        )

    if not isinstance(registry, dict):
        raise SystemExit(
            "ERROR: source registry must be a YAML mapping."
        )

    sources = registry.get("sources", [])

    if not isinstance(sources, list):
        raise SystemExit(
            "ERROR: registry 'sources' must be a list."
        )

    results = []

    for source in sources:
        if not isinstance(source, dict):
            continue

        try:
            result = discover_source(source)
        except Exception as exc:
            # Unexpected source-level errors are recorded so later sources
            # can still be processed. No source is silently marked verified.
            result = {
                "source_id": source.get("source_id"),
                "source_name": source.get("name"),
                "source_url": source.get("url"),
                "discovery_status": "source_processing_error",
                "error": str(exc)[:1000],
                "candidate_count": 0,
                "candidates": [],
                "notes": [
                    "This source failed during discovery.",
                    "No legal status or redistribution rights are established.",
                ],
            }

        results.append(result)

        print(
            f"{result['discovery_status'].upper():24} "
            f"{result.get('source_id')} — "
            f"{len(result.get('candidates', []))} candidate(s)"
        )

        time.sleep(0.5)

    all_urls = [
        candidate["url"]
        for result in results
        for candidate in result.get("candidates", [])
    ]

    report = {
        "report_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Candidate discovery and metadata extraction only. "
            "No legal status or redistribution rights are established."
        ),
        "summary": {
            "sources_processed": len(results),
            "sources_with_errors": sum(
                1 for result in results
                if result.get("discovery_status") != "completed"
                or result.get("candidate_errors", 0) > 0
            ),
            "candidates_found": len(all_urls),
            "unique_urls_across_sources": len(set(all_urls)),
            "duplicate_urls_across_sources": (
                len(all_urls) - len(set(all_urls))
            ),
            "human_review_required": True,
            "automatic_legal_status_changes": False,
            "automatic_redistribution_approval": False,
        },
        "sources": results,
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\nReport saved to: {REPORT.relative_to(ROOT)}")
    print(
        "Review all candidate records before adding materials to the library."
    )


if __name__ == "__main__":
    main()
