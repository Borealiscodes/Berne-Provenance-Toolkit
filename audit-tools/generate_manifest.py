#!/usr/bin/env python3
"""
generate_manifest.py — Zero-Dependency Canonical Provenance Manifest Generator
Part of Berne-Provenance-Toolkit (Author-Agnostic · Educational & Forensic Tooling).

Scans a directory of files (e.g. .md, .rs, .py, .lean, .tex) and emits a canonical
JSONL custody ledger (`provenance-chain.jsonl`) with normalized UTF-8 SHA-256 hashes
and excerpt fingerprints compatible with `mcp_provenance_auditor.py`.

Usage:
  python3 audit-tools/generate_manifest.py \
    --root ./docs \
    --author "Jane Doe" \
    --orcid "0000-0002-1825-0097" \
    --base-uri "https://github.com" \
    --license "MIT" \
    --doi "10.5281/zenodo.1234567" \
    --out manifest/provenance-chain.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_EXTENSIONS = {".md", ".txt", ".rst", ".tex", ".py", ".rs", ".lean", ".v", ".jl", ".ts", ".go"}


def canonical_sha256(text: str) -> str:
    """Computes normalized UTF-8 SHA-256 hex digest matching `mcp_provenance_auditor.py`."""
    normalized = text.replace("\(\r\\)n", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_clean_excerpt(text: str, max_chars: int = 280) -> str:
    """Extracts a clean prose/code fingerprint excerpt for k-shingle matching."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith(("#", "---", "```", "<!--"))
    ]
    joined = " ".join(lines)
    collapsed = re.sub(r"\s+", " ", joined).strip()
    return collapsed[:max_chars]


def build_manifest_records(
    root_dir: Path,
    author_name: str,
    author_orcid: str,
    base_uri: str,
    license_spdx: str,
    canonical_doi: str | None,
    extensions: set[str],
) -> list[dict[str, str]]:
    """Walks `root_dir` deterministically and constructs JSONL provenance records."""
    if not root_dir.exists() or not root_dir.is_dir():
        raise FileNotFoundError(f"Root directory not found: {root_dir}")

    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    base_uri_clean = base_uri.rstrip("/")
    records: list[dict[str, str]] = []

    for file_path in sorted(root_dir.rglob("*")):
        if not file_path.is_file():
            continue
        if any(part.startswith(".") for part in file_path.relative_to(root_dir).parts):
            continue
        if file_path.suffix.lower() not in extensions:
            continue

        rel_posix = file_path.relative_to(root_dir).as_posix()
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        digest = canonical_sha256(raw_text)
        excerpt = extract_clean_excerpt(raw_text)

        artifact_slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", rel_posix).strip("-").lower()
        record: dict[str, str] = {
            "artifact_id": artifact_slug,
            "relative_path": rel_posix,
            "author_name": author_name,
            "author_orcid": author_orcid,
            "canonical_uri": f"{base_uri_clean}/{rel_posix}",
            "license_spdx": license_spdx,
            "sha256": digest,
            "anchored_at_utc": timestamp_utc,
            "excerpt": excerpt,
        }
        if canonical_doi:
            record["canonical_doi"] = canonical_doi

        records.append(record)

    return records


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a canonical SHA-256 provenance-chain.jsonl ledger for any repository."
    )
    parser.add_argument("--root", required=True, type=Path, help="Directory of files to anchor")
    parser.add_argument("--author", required=True, type=str, help="Canonical human author name")
    parser.add_argument("--orcid", required=True, type=str, help="Author ORCID (e.g. 0000-0002-1825-0097)")
    parser.add_argument("--base-uri", required=True, type=str, help="Canonical upstream base URL")
    parser.add_argument("--license", default="MIT", type=str, help="SPDX license identifier (default: MIT)")
    parser.add_argument("--doi", default=None, type=str, help="Optional persistent DOI (e.g. 10.5281/zenodo.1234567)")
    parser.add_argument("--out", required=True, type=Path, help="Output JSONL manifest path")
    args = parser.parse_args()

    try:
        records = build_manifest_records(
            root_dir=args.root,
            author_name=args.author,
            author_orcid=args.orcid,
            base_uri=args.base_uri,
            license_spdx=args.license,
            canonical_doi=args.doi,
            extensions=DEFAULT_EXTENSIONS,
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"Error generating manifest: {exc}", file=sys.stderr)
        return 1

    print(f"Anchored {len(records)} artifacts into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
