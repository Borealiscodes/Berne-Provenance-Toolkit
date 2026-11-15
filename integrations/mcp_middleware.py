#!/usr/bin/env python3
"""
mcp_middleware.py — Zero-Dependency 1-Line MCP Provenance Decorator
Part of Berne-Provenance-Toolkit (v1.3+ · Author-Agnostic · Berne Art. 6bis & W3C ODRL).

Wraps Python MCP tool functions (compatible with FastMCP, official `mcp` SDK, or
standard JSON-RPC handlers) so every returned text or dict payload automatically carries
a schema-valid `v1.1.0` provenance envelope with SHA-256 digests and upstream attribution.
"""

from __future__ import annotations

import functools
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


def _normalize_utf8_sha256(text: str) -> str:
    normalized = text.replace("\r\n", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_manifest_index(manifest_path: str | Path) -> Dict[str, Dict[str, Any]]:
    """Index manifest records by `relative_path` and `artifact_id` for fast runtime lookup."""
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Provenance manifest not found: {path}")

    index: Dict[str, Dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rec = json.loads(stripped)
        if "relative_path" in rec:
            index[rec["relative_path"]] = rec
        if "artifact_id" in rec:
            index[rec["artifact_id"]] = rec
    return index


def build_mcp_envelope(
    content: str,
    sources: List[Dict[str, Any]],
    synthesis_mode: str = "verbatim",
    modified: Optional[bool] = None,
    odrl_policy_uri: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct a schema v1.1.0 compliant MCP provenance response dictionary."""
    mode = synthesis_mode.lower()
    if mode not in ("verbatim", "excerpt", "synthesis"):
        raise ValueError(f"Invalid synthesis_mode '{synthesis_mode}'. Must be verbatim, excerpt, or synthesis.")

    is_modified = (mode == "synthesis") if modified is None else bool(modified)
    if mode == "verbatim" and is_modified:
        raise ValueError("Invariant violation: synthesis_mode='verbatim' requires modified=False.")

    normalized_sources: List[Dict[str, Any]] = []
    for src in sources:
        entry: Dict[str, Any] = {
            "author_name": src["author_name"],
            "source_uri": src.get("canonical_uri") or src["source_uri"],
            "license_spdx": src.get("license_spdx", "MIT"),
            "sha256": src["sha256"],
        }
        if src.get("author_orcid"):
            entry["author_orcid"] = src["author_orcid"]
        if src.get("relative_path") or src.get("file_path"):
            entry["file_path"] = src.get("relative_path") or src.get("file_path")
        if src.get("binary_sha256"):
            entry["binary_sha256"] = src["binary_sha256"]
        normalized_sources.append(entry)

    governance: Dict[str, Any] = {
        "berne_moral_rights": "Berne Convention Art. 6bis (Attribution & Integrity Retained)"
    }
    if odrl_policy_uri:
        governance["odrl_policy_uri"] = odrl_policy_uri

    return {
        "schema_version": "1.1.0",
        "content": content,
        "synthesis_mode": mode,
        "modified": is_modified,
        "content_sha256": _normalize_utf8_sha256(content),
        "sources": normalized_sources,
        "governance": governance,
    }


def berne_provenance(
    manifest_path: str | Path,
    artifact_keys: List[str],
    synthesis_mode: str = "verbatim",
    modified: Optional[bool] = None,
    odrl_policy_uri: Optional[str] = None,
    as_json_string: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    1-line decorator for Python MCP tools.

    Example:
        @mcp.tool()
        @berne_provenance("manifest/provenance-chain.jsonl", ["01-berne-convention.md"])
        def get_berne_guide() -> str:
            return Path("curriculum/01-berne-convention.md").read_text()
    """
    manifest_index = load_manifest_index(manifest_path)
    resolved_sources: List[Dict[str, Any]] = []
    for key in artifact_keys:
        if key not in manifest_index:
            raise KeyError(f"Artifact '{key}' not found in manifest '{manifest_path}'.")
        resolved_sources.append(manifest_index[key])

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            raw_result = func(*args, **kwargs)
            text_payload = (
                raw_result
                if isinstance(raw_result, str)
                else json.dumps(raw_result, ensure_ascii=False)
            )
            envelope = build_mcp_envelope(
                content=text_payload,
                sources=resolved_sources,
                synthesis_mode=synthesis_mode,
                modified=modified,
                odrl_policy_uri=odrl_policy_uri,
            )
            return json.dumps(envelope, indent=2, ensure_ascii=False) if as_json_string else envelope

        return wrapper

    return decorator
