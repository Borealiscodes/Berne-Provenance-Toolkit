#!/usr/bin/env python3
"""
mcp_provenance_auditor.py — Zero-Dependency Forensic MCP & Aggregator Auditor
Part of Berne-Provenance-Toolkit (v1.2+ · Berne Art. 2/6bis, CRRA 2000, W3C ODRL).

Inspects MCP JSON-RPC responses or scraped text files against a canonical
SHA-256 provenance manifest (`provenance-chain.jsonl`) and detects:
  1. BERNE-6BIS-PATERNITY            : Content matches anchored source, but author/ORCID is stripped.
  2. BERNE-6BIS-INTEGRITY            : Claimed verbatim/excerpt (`modified != True`), but digest fails.
  3. PROVENANCE-HOP-DRIFT            : Response cites a middle-hop scraper instead of canonical URI/DOI.
  4. MCP-SCHEMA-UNBOUND              : MCP JSON payload omits required structured provenance metadata.
  5. PROVENANCE-LAUNDERING-SYNTHESIS : Multi-source blend omits upstream attributions in `sources[]`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from extractors.pdf_stdlib import normalize_text  # noqa: E402
from generate_manifest import compute_5gram_shingles, compute_paragraph_chunks  # noqa: E402

REQUIRED_SOURCE_FIELDS = (
    "author_name",
    "author_orcid",
    "source_uri",
    "license_spdx",
    "sha256",
)


def canonical_sha256(text: str) -> str:
    """Compute normalized UTF-8 SHA-256 hex digest."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_shingles(text: str, k: int = 5) -> Set[str]:
    """Build lowercase word k-shingles for overlap detection."""
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def load_manifest(manifest_path: Path) -> List[Dict[str, Any]]:
    """Load canonical artifact entries from a JSONL provenance manifest."""
    entries: List[Dict[str, Any]] = []
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    for line_no, raw_line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on manifest line {line_no}: {exc}") from exc
        entries.append(record)
    return entries


def extract_payload_fields(target_path: Path) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]], bool]:
    """
    Extract text body, envelope metadata, and normalized `sources[]` list from an
    MCP JSON-RPC response, v1.1+ envelope, or raw text/Markdown file.
    """
    raw = target_path.read_text(encoding="utf-8", errors="replace")
    stripped = raw.strip()
    is_json = target_path.suffix.lower() == ".json" or (
        stripped.startswith("{") and stripped.endswith("}")
    )

    if not is_json:
        return raw, {}, [], False

    data = json.loads(raw)
    container = data.get("result", data) if isinstance(data, dict) else {}
    if not isinstance(container, dict):
        container = {}

    raw_content = container.get("content")
    if isinstance(raw_content, list):
        text_body = "\n".join(
            block.get("text", "") for block in raw_content if isinstance(block, dict)
        )
    else:
        text_body = container.get("text") or raw_content or ""

    meta = container.get("provenance", container)
    if not isinstance(meta, dict):
        meta = {}

    # Normalize v1.1+ `sources[]` array or legacy v1.0 flat provenance fields
    sources: List[Dict[str, Any]] = []
    if isinstance(meta.get("sources"), list):
        sources = [s for s in meta["sources"] if isinstance(s, dict)]
    elif any(k in meta for k in ("author_name", "author_orcid", "source_uri", "sha256")):
        sources = [meta]

    return str(text_body), meta, sources, True


def audit_target(
    manifest: List[Dict[str, Any]],
    target_path: Path,
    overlap_threshold: float = 0.25,
) -> Dict[str, Any]:
    """Run forensic checks against all canonical records in the manifest."""
    text_body, meta, declared_sources, is_json = extract_payload_fields(target_path)
    observed_sha = canonical_sha256(text_body)
    observed_chunks = set(compute_paragraph_chunks(text_body))
    observed_shingles = extract_shingles(text_body)

    synthesis_mode = str(meta.get("synthesis_mode", "verbatim")).lower() if is_json else "unstructured"
    is_declared_modified = meta.get("modified") is True or synthesis_mode == "synthesis"

    findings: List[Dict[str, str]] = []

    # 1. Schema completeness check on JSON envelopes
    if is_json:
        if not declared_sources:
            findings.append(
                {
                    "code": "MCP-SCHEMA-UNBOUND",
                    "severity": "HIGH",
                    "detail": "MCP JSON payload omits structured provenance metadata or `sources[]` array.",
                }
            )
        else:
            for idx, src in enumerate(declared_sources):
                missing = [
                    f for f in REQUIRED_SOURCE_FIELDS if f not in src or src.get(f) in (None, "")
                ]
                if "modified" not in meta and "modified" not in src:
                    missing.append("modified")
                if missing:
                    findings.append(
                        {
                            "code": "MCP-SCHEMA-UNBOUND",
                            "severity": "HIGH",
                            "detail": f"MCP source[{idx}] omits required provenance fields: {', '.join(missing)}",
                        }
                    )

    # 2. Match observed content against all manifest records (exact, chunk, URI/DOI, or shingle)
    matched_entries: List[Tuple[Dict[str, Any], float, Set[str]]] = []
    best_overlap = 0.0

    for entry in manifest:
        entry_sha = str(entry.get("sha256", "")).lower()
        entry_doi = str(entry.get("canonical_doi", ""))
        entry_uri = str(entry.get("canonical_uri") or entry.get("source_uri", ""))
        entry_chunks = set(entry.get("chunk_hashes", []))
        entry_shingles = set(entry.get("shingle_5grams", []))
        if not entry_shingles and entry.get("excerpt"):
            entry_shingles = extract_shingles(str(entry["excerpt"]))

        exact_doc = bool(entry_sha and observed_sha == entry_sha)
        chunk_hits = observed_chunks & entry_chunks

        overlap = 0.0
        if exact_doc:
            overlap = 1.0
        elif entry_shingles and observed_shingles:
            denom = min(len(entry_shingles), len(observed_shingles))
            overlap = len(entry_shingles & observed_shingles) / denom if denom > 0 else 0.0

        if overlap > best_overlap:
            best_overlap = overlap

        uri_or_doi_cited = bool(
            (entry_doi and entry_doi in text_body) or (entry_uri and entry_uri in text_body)
        )

        if exact_doc or chunk_hits or uri_or_doi_cited or overlap >= overlap_threshold:
            matched_entries.append((entry, overlap, chunk_hits))

    # 3. Verify paternity, integrity, and hop-drift for each matched manifest artifact
    unattributed_matches: List[Dict[str, Any]] = []

    for entry, overlap, chunk_hits in matched_entries:
        art_id = str(entry.get("artifact_id") or entry.get("relative_path", "unknown"))
        expected_sha = str(entry.get("sha256", "")).lower()
        expected_orcid = str(entry.get("author_orcid", ""))
        expected_author = str(entry.get("author_name", ""))
        expected_uri = str(entry.get("canonical_uri") or entry.get("source_uri", "")).rstrip("/")
        expected_doi = str(entry.get("canonical_doi", "")).strip()

        # Find matching source declaration in `declared_sources`
        matched_src: Dict[str, Any] | None = None
        for src in declared_sources:
            s_sha = str(src.get("sha256", "")).lower()
            s_uri = str(src.get("source_uri", "")).rstrip("/")
            if (expected_sha and s_sha == expected_sha) or (
                expected_uri and s_uri == expected_uri
            ) or (expected_doi and expected_doi in s_uri):
                matched_src = src
                break

        # Paternity check (Berne Art. 6bis) — supports structured JSON or inline text attribution
        has_inline_author = bool(
            (expected_orcid and expected_orcid in text_body)
            or (expected_author and expected_author.lower() in text_body.lower())
        )
        has_struct_author = bool(
            matched_src
            and (
                (expected_orcid and matched_src.get("author_orcid") == expected_orcid)
                or (
                    expected_author
                    and str(matched_src.get("author_name", "")).lower() == expected_author.lower()
                )
            )
        )

        if not (has_struct_author or (not is_json and has_inline_author)):
            unattributed_matches.append(entry)
            findings.append(
                {
                    "code": "BERNE-6BIS-PATERNITY",
                    "severity": "CRITICAL",
                    "detail": f"Matched canonical artifact '{art_id}' (overlap={overlap:.0%}), but author identity/ORCID ({expected_orcid}) was stripped.",
                }
            )

        # Integrity check (Berne Art. 6bis) — fires if not explicitly flagged modified=True
        if not is_declared_modified:
            if synthesis_mode == "excerpt":
                if not chunk_hits and expected_sha and observed_sha != expected_sha:
                    findings.append(
                        {
"code": "BERNE-6BIS-INTEGRITY",
"severity": "HIGH",
"detail": f"Excerpt chunk digest mismatch for '{art_id}' (modified=false): silent quote mutation or truncation.",
}
)
elif expected_sha and observed_sha != expected_sha:
findings.append(
{
"code": "BERNE-6BIS-INTEGRITY",
"severity": "HIGH",
"detail": f"SHA-256 mismatch for '{art_id}' (modified=false): expected {expected_sha[:16]}..., observed {observed_sha[:16]}... (silent mutation or undeclared truncation).",
}
)
# Middle-hop provenance laundering check
if matched_src:
observed_uri = str(matched_src.get("source_uri", "")).rstrip("/")
if (
observed_uri
and expected_uri
and observed_uri != expected_uri
and (not expected_doi or expected_doi not in observed_uri)
):
findings.append(
{
"code": "PROVENANCE-HOP-DRIFT",
"severity": "MEDIUM",
"detail": f"Middle-hop source_uri '{observed_uri}' does not match canonical upstream '{expected_uri}' or DOI '{expected_doi}'.",
}
)
# 4. Multi-source synthesis laundering check
if len(unattributed_matches) >= 2:
names = ", ".join(
str(e.get("artifact_id") or e.get("relative_path", "unknown"))
for e in unattributed_matches
)
findings.append(
{
"code": "PROVENANCE-LAUNDERING-SYNTHESIS",
"severity": "CRITICAL",
"detail": f"Multi-source synthesis overlap detected across {len(unattributed_matches)} uncredited artifacts: [{names}].",
}
)
matched_ids = [
str(e.get("artifact_id") or e.get("relative_path")) for e, _, _ in matched_entries
]
return {
"target": str(target_path),
"synthesis_mode": synthesis_mode,
"observed_sha256": observed_sha,
"matched_artifact": matched_ids if matched_ids else None,
"matched_artifacts": matched_ids,
"shingle_overlap": round(best_overlap, 3),
"status": "PASS" if not findings else "DEFECTS_DETECTED",
"findings": findings,
}
def main() -> int:
parser = argparse.ArgumentParser(
description="Forensic MCP & Aggregator Provenance Auditor (Berne-Provenance-Toolkit)"
)
parser.add_argument("--manifest", required=True, type=Path, help="Path to provenance-chain.jsonl")
parser.add_argument("--inspect", required=True, type=Path, help="Path to MCP JSON or scraped text file")
parser.add_argument(
"--threshold",
type=float,
default=0.25,
help="5-gram shingle overlap threshold (default: 0.25)",
)
args = parser.parse_args()
try:
manifest = load_manifest(args.manifest)
if not args.inspect.exists():
raise FileNotFoundError(f"Inspection target not found: {args.inspect}")
report = audit_target(manifest, args.inspect, overlap_threshold=args.threshold)
except Exception as exc:
print(f"Audit error: {exc}", file=sys.stderr)
return 2
print(json.dumps(report, indent=2, ensure_ascii=False))
return 0 if report["status"] == "PASS" else 1
if name == "main":
raise SystemExit(main())

