#!/usr/bin/env python3
"""
mcp_provenance_auditor.py — Zero-Dependency Forensic MCP & Aggregator Auditor
Part of Berne-Provenance-Toolkit (Educational & Forensic Tooling Only).

Inspects MCP JSON-RPC responses or scraped text files against a canonical
SHA-256 provenance manifest (`provenance-chain.jsonl`) and detects:
  1. BERNE-6BIS-PATERNITY  : Content matches anchored source, but author/ORCID is stripped.
  2. BERNE-6BIS-INTEGRITY : Author/DOI is cited, but SHA-256 digest fails (silent mutation).
  3. PROVENANCE-HOP-DRIFT : Response cites a middle-hop scraper instead of canonical URI/DOI.
  4. MCP-SCHEMA-UNBOUND   : MCP payload omits structured provenance metadata fields.

Usage:
  python3 audit-tools/mcp_provenance_auditor.py --manifest manifest/provenance-chain.jsonl --inspect payload.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_PROVENANCE_FIELDS = ("author_orcid", "source_uri", "license_spdx", "sha256")


def canonical_sha256(text: str) -> str:
    """Computes normalized UTF-8 SHA-256 hex digest."""
    normalized = text.replace("\r\n", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_shingles(text: str, k: int = 5) -> set[tuple[str, ...]]:
    """Builds lowercase word k-shingles for overlap detection even when text is truncated."""
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    if len(tokens) < k:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def load_manifest(manifest_path: Path) -> list[dict[str, Any]]:
    """Loads canonical artifact entries from a JSONL provenance manifest."""
    entries: list[dict[str, Any]] = []
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    for line_no, raw_line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on manifest line {line_no}: {exc}") from exc
        entries.append(record)
    return entries


def extract_payload_fields(target_path: Path) -> tuple[str, dict[str, Any], bool]:
    """Extracts text body and provenance metadata from an MCP JSON or raw text/Markdown file."""
    raw = target_path.read_text(encoding="utf-8")
    if target_path.suffix.lower() == ".json":
        data = json.loads(raw)
        # Support top-level dict or MCP result wrapper (`{"result": {...}}`)
        container = data.get("result", data) if isinstance(data, dict) else {}
        if not isinstance(container, dict):
            container = {}
        text_body = (
            container.get("text")
            or container.get("content")
            or (
                "\n".join(
                    block.get("text", "")
                    for block in container.get("content", [])
                    if isinstance(block, dict)
                )
                if isinstance(container.get("content"), list)
                else ""
            )
            or json.dumps(container)
        )
        meta = container.get("provenance", container)
        if not isinstance(meta, dict):
            meta = {}
        return str(text_body), meta, True

    return raw, {}, False


def audit_target(manifest: list[dict[str, Any]], target_path: Path) -> dict[str, Any]:
    """Runs forensic checks against all canonical records in the manifest."""
    text_body, meta, is_json = extract_payload_fields(target_path)
    observed_sha = canonical_sha256(text_body)
    observed_shingles = extract_shingles(text_body)

    findings: list[dict[str, str]] = []

    if is_json:
        missing_fields = [f for f in REQUIRED_PROVENANCE_FIELDS if not meta.get(f)]
        if missing_fields:
            findings.append(
                {
                    "code": "MCP-SCHEMA-UNBOUND",
                    "severity": "HIGH",
                    "detail": f"MCP JSON payload omits structured provenance fields: {', '.join(missing_fields)}",
                }
            )

    matched_entry: dict[str, Any] | None = None
    best_overlap = 0.0

    for entry in manifest:
        entry_sha = str(entry.get("sha256", "")).lower()
        entry_doi = str(entry.get("canonical_doi", ""))
        entry_uri = str(entry.get("canonical_uri", ""))
        entry_orcid = str(entry.get("author_orcid", ""))
        entry_excerpt = str(entry.get("excerpt", ""))

        # Check exact hash match or metadata reference match
        if entry_sha and observed_sha == entry_sha:
            matched_entry = entry
            best_overlap = 1.0
            break

        if (entry_doi and entry_doi in text_body) or (entry_uri and entry_uri in text_body):
            matched_entry = entry

        if entry_excerpt:
            ref_shingles = extract_shingles(entry_excerpt)
            if ref_shingles and observed_shingles:
                overlap = len(ref_shingles & observed_shingles) / len(ref_shingles)
                if overlap > best_overlap:
                    best_overlap = overlap
                    if overlap >= 0.40:
                        matched_entry = entry

    if matched_entry is not None:
        expected_sha = str(matched_entry.get("sha256", "")).lower()
        expected_orcid = str(matched_entry.get("author_orcid", ""))
        expected_author = str(matched_entry.get("author_name", ""))
        expected_uri = str(matched_entry.get("canonical_uri", ""))
        expected_doi = str(matched_entry.get("canonical_doi", ""))

        # 1. Paternity check (Berne Art. 6bis)
        has_author = bool(
            (expected_orcid and (expected_orcid in text_body or meta.get("author_orcid") == expected_orcid))
            or (expected_author and expected_author.lower() in text_body.lower())
        )
        if not has_author:
            findings.append(
                {
                    "code": "BERNE-6BIS-PATERNITY",
                    "severity": "CRITICAL",
                    "detail": f"Matched canonical artifact '{matched_entry.get('artifact_id', 'unknown')}' (overlap={best_overlap:.0%}), but author identity/ORCID ({expected_orcid}) was stripped.",
                }
            )

        # 2. Integrity check (Berne Art. 6bis)
        if expected_sha and observed_sha != expected_sha:
            findings.append(
                {
                    "code": "BERNE-6BIS-INTEGRITY",
                    "severity": "HIGH",
                    "detail": f"SHA-256 mismatch for '{matched_entry.get('artifact_id', 'unknown')}': expected {expected_sha[:16]}..., observed {observed_sha[:16]}... (possible silent mutation or truncation).",
                }
            )

        # 3. Middle-hop provenance laundering check
        observed_uri = str(meta.get("source_uri", ""))
        if observed_uri and expected_uri and observed_uri != expected_uri and expected_doi not in observed_uri:
            findings.append(
                {
                    "code": "PROVENANCE-HOP-DRIFT",
                    "severity": "MEDIUM",
                    "detail": f"Middle-hop source_uri '{observed_uri}' does not match canonical upstream '{expected_uri}' or DOI '{expected_doi}'.",
                }
            )

    return {
        "target": str(target_path),
        "observed_sha256": observed_sha,
        "matched_artifact": matched_entry.get("artifact_id") if matched_entry else None,
        "shingle_overlap": round(best_overlap, 3),
        "status": "PASS" if not findings else "DEFECTS_DETECTED",
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Forensic MCP & Aggregator Provenance Auditor (Berne-Provenance-Toolkit)"
    )
    parser.add_argument("--manifest", required=True, type=Path, help="Path to provenance-chain.jsonl")
    parser.add_argument("--inspect", required=True, type=Path, help="Path to MCP JSON or scraped Markdown file")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
        report = audit_target(manifest, args.inspect)
    except Exception as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
