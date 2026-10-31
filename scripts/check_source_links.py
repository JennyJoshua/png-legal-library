#!/usr/bin/env python3
"""Check source URLs in the PNG Legal Library document register.

This checks technical link availability only. It does not verify
the authenticity, currency, legal effect, or reuse rights of documents.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "documents.json"
REPORT = ROOT / "reports" / "source-link-check-report.json"
TIMEOUT = 15


def check_url(url):
    checked_at = datetime.now(timezone.utc).isoformat()

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return {
            "url": url,
            "result": "invalid_url",
            "http_status": None,
            "checked_at": checked_at,
        }

    last_error = None

    for method in ("HEAD", "GET"):
        headers = {
            "User-Agent": "PNG-Legal-Library-SourceMonitor/1.0"
        }

        if method == "GET":
            headers["Range"] = "bytes=0-0"

        request = Request(url, headers=headers, method=method)

        try:
            with urlopen(request, timeout=TIMEOUT) as response:
                status = response.getcode()

                return {
                    "url": url,
                    "final_url": response.geturl(),
                    "result": "reachable" if status < 400 else "http_error",
                    "http_status": status,
                    "checked_at": checked_at,
                }

        except HTTPError as exc:
            last_error = {
                "status": exc.code,
                "detail": str(exc.reason),
            }

            # Some websites do not support HEAD requests.
            if method == "HEAD" and exc.code in (400, 403, 405, 501):
                continue

            if exc.code == 404:
                result = "not_found"
            elif exc.code in (401, 403, 429):
                result = "access_restricted"
            elif exc.code >= 500:
                result = "server_error"
            else:
                result = "http_error"

            return {
                "url": url,
                "final_url": exc.geturl(),
                "result": result,
                "http_status": exc.code,
                "detail": str(exc.reason),
                "checked_at": checked_at,
            }

        except (URLError, TimeoutError, OSError) as exc:
            last_error = {
                "status": None,
                "detail": str(exc),
            }

            if method == "HEAD":
                continue

            break

    return {
        "url": url,
        "result": "network_error",
        "http_status": last_error["status"] if last_error else None,
        "detail": last_error["detail"] if last_error else "Unknown error",
        "checked_at": checked_at,
    }


def main():
    if not REGISTER.exists():
        raise SystemExit("ERROR: data/documents.json was not found.")

    try:
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR reading document register: {exc}")

    documents = data.get("documents")

    if not isinstance(documents, list):
        raise SystemExit("ERROR: document register must contain a documents list.")

    results = []
    checked_urls = set()

    for document in documents:
        if not isinstance(document, dict):
            continue

        url = document.get("source_url")
        document_id = document.get("document_id")

        if not isinstance(url, str) or not url.strip():
            results.append({
                "document_id": document_id,
                "title": document.get("title"),
                "url": url,
                "result": "missing_url",
                "http_status": None,
            })
            continue

        if url in checked_urls:
            continue

        checked_urls.add(url)
        result = check_url(url)
        result["document_id"] = document_id
        result["title"] = document.get("title")
        results.append(result)

        print(
            f"{result['result'].upper():18} "
            f"{result.get('http_status')} {url}"
        )

        time.sleep(0.2)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "report_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": (
            "Technical link check only. "
            "This report does not verify legal status."
        ),
        "summary": {
            "total": len(results),
            "reachable": sum(
                item.get("result") == "reachable"
                for item in results
            ),
            "needs_attention": sum(
                item.get("result") != "reachable"
                for item in results
            ),
        },
        "results": results,
    }

    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\nReport saved to: {REPORT.relative_to(ROOT)}")
    print("Link availability does not establish legal validity or currency.")


if __name__ == "__main__":
    main()
