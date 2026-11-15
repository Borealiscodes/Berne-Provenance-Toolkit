#!/usr/bin/env python3
"""
spdx_bridge.py — Zero-Dependency CITATION.cff & SPDX SBOM Importer
Part of Berne-Provenance-Toolkit (v2.0 · Author-Agnostic · Berne Art. 6bis & W3C ODRL).

Parses standard repository `CITATION.cff` files and SPDX JSON SBOMs using strictly
Python 3 standard library modules (`re`, `json`) to auto-populate author names,
ORCIDs, persistent DOIs, and SPDX license identifiers for `generate_manifest.py`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict


def parse_citation_cff(cff_path: str | Path) -> Dict[str, str]:
    """
    Extract author_name, author_orcid, canonical_doi, canonical_uri, and license_spdx
    from a standard CITATION.cff file without external YAML dependencies.
    """
    path = Path(cff_path)
    if not path.exists():
        raise FileNotFoundError(f"CITATION.cff not found: {path}")

    raw = path.read_text(encoding="utf-8", errors="replace")
    meta: Dict[str, str] = {}

    family_match = re.search(r"family-names:\s*[\"']?([^\"'\n]+)[\"']?", raw)
    given_match = re.search(r"given-names:\s*[\"']?([^\"'\n]+)[\"']?", raw)
    if given_match and family_match:
        meta["author_name"] = f"{given_match.group(1).strip()} {family_match.group(1).strip()}"
    elif family_match:
        meta["author_name"] = family_match.group(1).strip()

    orcid_match = re.search(r"([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])", raw)
    if orcid_match:
        meta["author_orcid"] = orcid_match.group(1)

    doi_match = re.search(r"doi:\s*[\"']?(10\.\d{4,9}/[^\s\"'\n]+)[\"']?", raw)
    if doi_match:
        meta["canonical_doi"] = doi_match.group(1).strip()

    repo_match = re.search(r"repository-code:\s*[\"']?(https?://[^\s\"'\n]+)[\"']?", raw)
    if repo_match:
        meta["canonical_uri"] = repo_match.group(1).strip().rstrip("/")

    lic_match = re.search(r"license:\s*[\"']?([A-Za-z0-9.+-]+)[\"']?", raw)
    if lic_match:
        meta["license_spdx"] = lic_match.group(1).strip()

    return meta


def parse_spdx_sbom(spdx_json_path: str | Path) -> Dict[str, Any]:
    """Extract package license and creator metadata from an SPDX 2.3+ JSON document."""
    path = Path(spdx_json_path)
    if not path.exists():
        raise FileNotFoundError(f"SPDX JSON file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    result: Dict[str, Any] = {
        "spdx_version": data.get("spdxVersion", ""),
        "document_name": data.get("name", ""),
        "license_spdx": data.get("dataLicense", "CC0-1.0"),
        "creators": data.get("creationInfo", {}).get("creators", []),
        "packages": [],
    }

    for pkg in data.get("packages", []):
        result["packages"].append(
            {
                "name": pkg.get("name", ""),
                "license_spdx": pkg.get("licenseDeclared") or pkg.get("licenseConcluded", "NOASSERTION"),
                "download_location": pkg.get("downloadLocation", ""),
            }
        )

    return result
