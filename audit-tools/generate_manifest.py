#!/usr/bin/env python3
"""
generate_manifest.py — Zero-Dependency Canonical Provenance Manifest Generator
Part of Berne-Provenance-Toolkit (v1.2+ · Author-Agnostic · Educational & Forensic Tooling).

Scans a directory or file (.md, .rs, .py, .lean, .tex, .pdf, etc.) and emits a canonical
JSONL custody ledger (`provenance-chain.jsonl`) with normalized UTF-8 SHA-256 digests,
dual-hash PDF records, paragraph-level chunk hashes, and 5-gram synthesis shingles.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from extractors.pdf_stdlib import extract_pdf_provenance, normalize_text  # noqa: E402

DEFAULT_EXTENSIONS: Set[str] = {
    ".md",
    ".txt",
    ".rst",
    ".tex",
    ".py",
    ".rs",
    ".lean",
    ".v",
    ".jl",
    ".ts",
    ".go",
    ".json",
    ".jsonld",
    ".pdf",
}

SKIP_DIRS: Set[str] = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
}


def extract_clean_excerpt(text: str, max_chars: int = 280) -> str:
    """Extract a clean prose/code fingerprint excerpt for human inspection & k-shingle matching."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith(("#", "---", "```", "<!--"))
    ]
    joined = " ".join(lines)
    collapsed = re.sub(r"\s+", " ", joined).strip()
    return collapsed[:max_chars]


def compute_paragraph_chunks(text: str, min_chars: int = 40) -> List[str]:
    """Split normalized text into substantive paragraphs and return SHA-256 chunk digests."""
    blocks = re.split(r"\n\s*\n", normalize_text(text))
    chunk_hashes: List[str] = []
    for block in blocks:
        cleaned = " ".join(block.split()).strip()
        if len(cleaned) >= min_chars:
            digest = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()
            chunk_hashes.append(digest)
    return chunk_hashes


def compute_5gram_shingles(text: str, max_shingles: int = 250) -> List[str]:
    """Generate deterministic lowercase alphanumeric 5-gram word shingles for synthesis auditing."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    if len(tokens) < 5:
        return [" ".join(tokens)] if tokens else []

    seen: Set[str] = set()
    shingles: List[str] = []
    for i in range(len(tokens) - 4):
        gram = " ".join(tokens[i : i + 5])
        if gram not in seen:
            seen.add(gram)
            shingles.append(gram)
            if len(shingles) >= max_shingles:
                break
    return shingles


def build_artifact_record(
    file_path: Path,
    root_dir: Path,
    author_name: str,
    author_orcid: str,
    base_uri: str,
    license_spdx: str,
    canonical_doi: str | None = None,
    pdf_backend: str = "auto",
) -> Dict[str, Any]:
    """Build a schema v1.2+ provenance manifest entry preserving legacy & v1.1 fields."""
    rel_posix = file_path.relative_to(root_dir).as_posix() if file_path != root_dir else file_path.name
    clean_base = base_uri.rstrip("/")
    canonical_uri = f"{clean_base}/{rel_posix}" if clean_base else rel_posix
    timestamp_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    artifact_slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", rel_posix).strip("-").lower()

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        pdf_data = extract_pdf_provenance(file_path, backend=pdf_backend)
        norm_text = pdf_data["extracted_text"]
        text_sha256 = pdf_data["extracted_text_sha256"]
        artifact_type = "pdf"
    else:
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        norm_text = normalize_text(raw_text)
        text_sha256 = hashlib.sha256(norm_text.encode("utf-8")).hexdigest()
        artifact_type = "markdown" if suffix == ".md" else "code_or_text"

    record: Dict[str, Any] = {
        "schema_version": "1.2.0",
        "artifact_id": artifact_slug,
        "artifact_type": artifact_type,
        "relative_path": rel_posix,
        "author_name": author_name,
        "canonical_uri": canonical_uri,
        "license_spdx": license_spdx,
        "sha256": text_sha256,
        "excerpt": extract_clean_excerpt(norm_text),
        "chunk_hashes": compute_paragraph_chunks(norm_text),
        "shingle_5grams": compute_5gram_shingles(norm_text),
        "anchored_at_utc": timestamp_utc,
    }

    if author_orcid:
        record["author_orcid"] = author_orcid
    if canonical_doi:
        record["canonical_doi"] = canonical_doi

    if suffix == ".pdf":
        record["binary_sha256"] = pdf_data["binary_sha256"]
        record["pdf_backend"] = pdf_data["backend_used"]
        record["pdf_metadata"] = pdf_data["pdf_metadata"]

    return record


def build_manifest_records(
    root: Path,
    author_name: str,
    author_orcid: str,
    base_uri: str,
    license_spdx: str,
    canonical_doi: str | None = None,
    pdf_backend: str = "auto",
    extensions: Set[str] = DEFAULT_EXTENSIONS,
) -> List[Dict[str, Any]]:
    """Walk `root` deterministically and construct JSONL provenance records."""
    if not root.exists():
        raise FileNotFoundError(f"Target path not found: {root}")

    if root.is_file():
        files = [root]
        base_root = root.parent
    else:
        base_root = root
        files = sorted(
            p
            for p in root.rglob("*")
            if p.is_file()
            and p.suffix.lower() in extensions
            and not any(part.startswith(".") or part in SKIP_DIRS for part in p.relative_to(root).parts)
        )

    return [
        build_artifact_record(
            file_path=fp,
            root_dir=base_root,
            author_name=author_name,
            author_orcid=author_orcid,
            base_uri=base_uri,
            license_spdx=license_spdx,
            canonical_doi=canonical_doi,
            pdf_backend=pdf_backend,
        )
        for fp in files
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a canonical SHA-256 & chunk provenance-chain.jsonl ledger."
    )
    parser.add_argument("--root", required=True, type=Path, help="File or directory of files to anchor")
    parser.add_argument("--author", required=True, type=str, help="Canonical human author name")
    parser.add_argument("--orcid", default="", type=str, help="Author ORCID (e.g. 0000-0002-1825-0097)")
    parser.add_argument("--base-uri", required=True, type=str, help="Canonical upstream base URL")
    parser.add_argument("--license", default="MIT", type=str, help="SPDX license identifier (default: MIT)")
    parser.add_argument("--doi", default=None, type=str, help="Optional persistent DOI (e.g. 10.5281/zenodo.1234567)")
    parser.add_argument(
        "--pdf-backend",
        choices=["auto", "stdlib", "pdftotext", "pypdf"],
        default="auto",
        help="PDF extraction backend (default: auto)",
    )
    parser.add_argument("--out", required=True, type=Path, help="Output JSONL manifest path")
    args = parser.parse_args()

    try:
        records = build_manifest_records(
            root=args.root.resolve(),
            author_name=args.author,
            author_orcid=args.orcid,
            base_uri=args.base_uri,
            license_spdx=args.license,
            canonical_doi=args.doi,
            pdf_backend=args.pdf_backend,
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
