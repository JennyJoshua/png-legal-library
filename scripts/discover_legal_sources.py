#!/usr/bin/env python3
"""Discover candidate PNG legal materials from registered source websites.

This script identifies candidate URLs only. It does not establish
authenticity, legal status, currency, or redistribution permission.
"""

import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urldefrag
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
USER_AGENT = "PNG-Legal-Library-Discovery/1.0"

LEGAL_TERMS = re.compile(
    r"constitution|act\b|legislation|law\b|bill\b|regulation|"
    r"statute|judgment|judgement|court|legal|gazette|"
    r"organic[- ]law|rules of court|case law|"
    r"justice|ordinance|amendment|legal notice|"
    r"practice direction|public notice|"
    r"legislative|parliamentary",
    re.IGNORECASE,
)

DOCUMENT_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".rtf", ".html", ".htm"
)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return

        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value.strip())


def fetch(url):
    """Fetch a small public text response; never execute page scripts."""
    request = Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )

    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read(MAX_BYTES + 1)

            if len(body) > MAX_BYTES:
                body = body[:MAX_BYTES]

            return {
                "ok": True,
                "status": response.getcode(),
                "final_url": response.geturl(),
                "content_type": content_type,
                "body": body,
            }

    except HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": str(exc.reason),
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "ok": False,
            "status": None,
            "error": str(exc),
        }


def normalize_url(base, candidate):
    candidate = urljoin(base, candidate)
    candidate, _fragment = urldefrag(candidate)
    parsed = urlparse(candidate)

    if parsed.scheme not in ("http", "https"):
        return None

    if not parsed.netloc:
        return None

    if parsed.username or parsed.password:
        return None

    return candidate


def same_host(url, host):
    return urlparse(url).hostname == host


def looks_relevant(url):
    parsed = urlparse(url)
    text = f"{parsed.path} {parsed.query}".replace("_", " ").replace("-", " ")
    return bool(LEGAL_TERMS.search(text))


def is_document_url(url):
    path = urlparse(url).path.lower()
    return path.endswith(DOCUMENT_EXTENSIONS)


def parse_sitemap(data):
    urls = []

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return urls

    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1].lower() == "loc":
            if element.text and element.text.strip():
                urls.append(element.text.strip())

    return urls


def get_sitemap_urls(base_url, host):
    """Read sitemap locations advertised by robots.txt, then common paths."""
    candidates = [
        urljoin(base_url.rstrip("/") + "/", "robots.txt"),
        urljoin(base_url.rstrip("/") + "/", "sitemap.xml"),
        urljoin(base_url.rstrip("/") + "/", "sitemap_index.xml"),
    ]

    sitemap_urls = []

    robots = fetch(candidates[0])
    if robots["ok"]:
        text = robots["body"].decode("utf-8", errors="replace")

        for line in text.splitlines():
            if line.lower().startswith("sitemap:"):
                sitemap_urls.append(line.split(":", 1)[1].strip())

    sitemap_urls.extend(candidates[1:])

    # Keep only sitemap URLs on the registered host.
    return list(dict.fromkeys(
        url for url in sitemap_urls
        if urlparse(url).hostname == host
    ))


def inspect_sitemap(sitemap_url, host, found, visited_sitemaps):
    if sitemap_url in visited_sitemaps:
        return

    visited_sitemaps.add(sitemap_url)

    result = fetch(sitemap_url)
    if not result["ok"]:
        return

    if "xml" not in result.get("content_type", "").lower():
        # Some servers omit the XML content type; parse the response anyway.
        pass

    for url in parse_sitemap(result["body"]):
        normalized = normalize_url(sitemap_url, url)

        if not normalized or not same_host(normalized, host):
            continue

        if normalized.lower().endswith(".xml"):
            inspect_sitemap(
                normalized, host, found, visited_sitemaps
            )
            continue

        if looks_relevant(normalized) or is_document_url(normalized):
            found.setdefault(normalized, "sitemap")


def inspect_homepage_links(base_url, host, found):
    result = fetch(base_url)

    if not result["ok"]:
        return {
            "result": "unreachable",
            "http_status": result.get("status"),
            "error": result.get("error"),
        }

    content_type = result.get("content_type", "").lower()

    if "html" not in content_type:
        return {
            "result": "not_html",
            "http_status": result.get("status"),
        }

    parser = LinkParser()
    parser.feed(result["body"].decode("utf-8", errors="replace"))

    for href in parser.links:
        normalized = normalize_url(result["final_url"], href)

        if not normalized or not same_host(normalized, host):
            continue

        if looks_relevant(normalized) or is_document_url(normalized):
            found.setdefault(normalized, "homepage_link")

    return {
        "result": "checked",
        "http_status": result.get("status"),
    }


def discover_source(source):
    base_url = source.get("url", "")
    parsed = urlparse(base_url)
    host = parsed.hostname

    output = {
        "source_id": source.get("source_id"),
        "source_name": source.get("name"),
        "source_url": base_url,
        "source_type": source.get("source_type"),
        "source_review_status": source.get("review_status"),
        "discovery_status": "started",
        "homepage_check": None,
        "sitemaps_checked": 0,
        "candidates": [],
        "notes": [
            "Candidate discovery only; legal status has not been verified.",
            "Source terms and redistribution permissions require human review.",
        ],
    }

    if not host or parsed.scheme not in ("http", "https"):
        output["discovery_status"] = "invalid_source_url"
        return output

    found = {}
    output["homepage_check"] = inspect_homepage_links(
        base_url, host, found
    )

    sitemap_urls = get_sitemap_urls(base_url, host)
    visited_sitemaps = set()

    for sitemap_url in sitemap_urls:
        inspect_sitemap(
            sitemap_url, host, found, visited_sitemaps
        )
        time.sleep(0.2)

    output["sitemaps_checked"] = len(visited_sitemaps)

    candidates = sorted(found.items())[:MAX_URLS_PER_SOURCE]

    for url, discovery_method in candidates:
        output["candidates"].append({
            "url": url,
            "title": None,
            "discovery_method": discovery_method,
            "candidate_type": (
                "document_link" if is_document_url(url)
                else "webpage"
            ),
            "review_status": "pending_review",
            "legal_status": "status_unknown",
            "redistribution_permission": "unknown",
        })

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
        raise SystemExit(f"ERROR reading source registry: {exc}")

    if not isinstance(registry, dict):
        raise SystemExit("ERROR: source registry must be a YAML mapping.")

    sources = registry.get("sources", [])

    if not isinstance(sources, list):
        raise SystemExit("ERROR: registry 'sources' must be a list.")

    results = []

    for source in sources:
        if not isinstance(source, dict):
            continue

        result = discover_source(source)
        results.append(result)

        print(
            f"{result['discovery_status'].upper():20} "
            f"{result.get('source_id')} — "
            f"{len(result.get('candidates', []))} candidate(s)"
        )

        time.sleep(0.5)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "report_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Candidate discovery only. "
            "No legal status or redistribution rights are established."
        ),
        "summary": {
            "sources_processed": len(results),
            "candidates_found": sum(
                len(item.get("candidates", []))
                for item in results
            ),
            "human_review_required": True,
        },
        "sources": results,
    }

    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\nReport saved to: {REPORT.relative_to(ROOT)}")
    print("Review candidate URLs before adding any document to the library.")


if __name__ == "__main__":
    main()
