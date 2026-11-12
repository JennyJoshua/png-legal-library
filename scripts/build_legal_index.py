#!/usr/bin/env python3
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from segment_legal_text import segment_text

ROOT = Path(__file__).resolve().parent.parent
MAX_INDEX_BYTES = 50 * 1024 * 1024
MAX_INDEX_RECORDS = 100_000

def build(input_dir, output_dir):
    records = []
    for path in sorted(Path(input_dir).glob("*.extraction.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        required = ("document_id", "version_id", "source_checksum_sha256", "segments")
        if any(k not in data for k in required):
            raise ValueError(f"{path.name}: missing extraction provenance")
        if not re.fullmatch(r"[a-f0-9]{64}", data["source_checksum_sha256"]):
            raise ValueError(f"{path.name}: invalid source checksum")
        next_id = 1
        for segment in data["segments"]:
            ref, content = segment.get("reference"), segment.get("text", "")
            if not isinstance(ref, str) or not isinstance(content, str):
                raise ValueError(f"{path.name}: malformed extraction segment")
            nodes = segment_text(content, ref, data["document_id"], data["version_id"], next_id)
            next_id += len(nodes)
            for node in nodes:
                node.update({"document_title": data.get("document_title") or data["document_id"],
                             "source_url": data.get("source_url"), "source_id": data.get("source_id"),
                             "source_checksum_sha256": data["source_checksum_sha256"], "format": data.get("format")})
            if len(records) + len(nodes) > MAX_INDEX_RECORDS:
                raise ValueError(f"Index exceeds the configured {MAX_INDEX_RECORDS}-record limit")
            records.extend(nodes)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    result = {"index_schema_version": "1.0",
              "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
              "record_count": len(records), "records": records,
              "warning": "Local research aid only. Verify every passage and citation against the original authoritative document and confirm its current legal status."}
    target = output / "index.json"
    serialized = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if len(serialized.encode("utf-8")) > MAX_INDEX_BYTES:
        raise ValueError(f"Index exceeds the configured {MAX_INDEX_BYTES}-byte limit")
    target.write_text(serialized, encoding="utf-8")
    return {"indexed_records": len(records), "index_file": str(target)}

def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a local keyword index from extracted legal text.")
    parser.add_argument("--input-dir", default=str(ROOT / "extracted"))
    parser.add_argument("--output-dir", default=str(ROOT / "legal-index"))
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args.input_dir, args.output_dir), indent=2)); return 0
    except Exception as exc:
        print(f"INDEX ERROR: {exc}", file=sys.stderr); return 1

if __name__ == "__main__":
    raise SystemExit(main())
