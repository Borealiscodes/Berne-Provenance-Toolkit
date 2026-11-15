#!/usr/bin/env python3
"""
exporters.py — W3C ODRL, C2PA-Compatible Assertion & OpenSSH Ed25519 Exporter
Part of Berne-Provenance-Toolkit (v2.0 · Zero-Dependency Python 3 Core).

Exports `provenance-chain.jsonl` records into machine-readable W3C ODRL policies,
C2PA-style provenance assertions, and detached OpenSSH Ed25519 signatures (`.sig`)
using the system `ssh-keygen` binary without external Python crypto libraries.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def export_odrl_policy(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert manifest records into a W3C ODRL 2.2 JSON-LD attribution & integrity policy."""
    assets = []
    for rec in records:
        assets.append(
            {
                "@type": "Asset",
                "uid": rec.get("canonical_uri") or rec.get("artifact_id"),
                "dc:creator": rec.get("author_name"),
                "orcid": rec.get("author_orcid", ""),
                "spdx:license": rec.get("license_spdx", "MIT"),
                "sha256": rec.get("sha256"),
            }
        )

    return {
        "@context": [
            "http://w3.org",
            {"dc": "http://purl.org", "spdx": "http://spdx.org"},
        ],
        "@type": "Set",
        "uid": "urn:berne-provenance:policy:v2",
        "profile": "https://github.com",
        "permission": [
            {
                "target": assets,
                "action": ["use", "reproduce", "distribute", "derive"],
                "duty": [
                    {
                        "action": "attribute",
                        "constraint": [
                            {
                                "leftOperand": "purpose",
                                "operator": "eq",
                                "rightOperand": "berne-art-6bis-paternity-and-integrity",
                            }
                        ],
                    }
                ],
            }
        ],
        "prohibition": [
            {
                "target": assets,
                "action": "modify",
                "constraint": [
                    {
                        "leftOperand": "event",
                        "operator": "eq",
                        "rightOperand": "silent-mutation-without-modified-flag",
                    }
                ],
            }
        ],
    }


def export_c2pa_assertions(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Export C2PA-aligned provenance assertion blocks for cross-tool ingestion."""
    assertions = []
    for rec in records:
        assertions.append(
            {
                "label": "stds.schema-org.CreativeWork",
                "data": {
                    "@context": "https://schema.org",
                    "@type": "CreativeWork",
                    "name": rec.get("relative_path"),
                    "url": rec.get("canonical_uri"),
                    "identifier": rec.get("canonical_doi") or rec.get("sha256"),
                    "license": rec.get("license_spdx"),
                    "author": [
                        {
                            "@type": "Person",
                            "name": rec.get("author_name"),
                            "identifier": f"https://orcid.org{rec['author_orcid']}"
                            if rec.get("author_orcid")
                            else "",
                        }
                    ],
                },
                "hash_binding": {
                    "alg": "sha256",
                    "text_digest": rec.get("sha256"),
                    "binary_digest": rec.get("binary_sha256", ""),
                },
            }
        )

    return {
        "manifest_generator": "Berne-Provenance-Toolkit/2.0.0",
        "claim_generator_info": [{"name": "Berne-Provenance-Toolkit", "version": "2.0.0"}],
        "assertions": assertions,
    }


def sign_manifest_openssh(manifest_path: Path, private_key_path: Path, namespace: str = "berne-provenance") -> Path:
    """
    Create a detached `.sig` file using OpenSSH `ssh-keygen -Y sign`
    (built into modern Linux, macOS, and Windows — zero Python crypto dependencies).
    """
    if not shutil.which("ssh-keygen"):
        raise RuntimeError("System `ssh-keygen` binary not found in PATH.")
    if not private_key_path.exists():
        raise FileNotFoundError(f"Signing key not found: {private_key_path}")

    subprocess.run(
        [
            "ssh-keygen",
            "-Y",
            "sign",
            "-f",
            str(private_key_path),
            "-n",
            namespace,
            str(manifest_path),
        ],
        check=True,
    )
    return Path(f"{manifest_path}.sig")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Berne-Provenance manifests to ODRL, C2PA, or OpenSSH .sig.")
    parser.add_argument("--manifest", required=True, type=Path, help="Input provenance-chain.jsonl path")
    parser.add_argument("--format", required=True, choices=["odrl", "c2pa", "openssh-sign"], help="Export format")
    parser.add_argument("--out", type=Path, help="Output file path (for odrl/c2pa JSON)")
    parser.add_argument("--key", type=Path, help="Private SSH key path (required for openssh-sign)")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"Manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    records = [
        json.loads(line)
        for line in args.manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if args.format == "openssh-sign":
        if not args.key:
            print("Error: --key is required when --format openssh-sign is selected.", file=sys.stderr)
            return 2
        sig_path = sign_manifest_openssh(args.manifest.resolve(), args.key.resolve())
        print(f"Signed manifest -> {sig_path}")
        return 0

    exported = export_odrl_policy(records) if args.format == "odrl" else export_c2pa_assertions(records)
    rendered = json.dumps(exported, indent=2, ensure_ascii=False)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
        print(f"Exported {args.format.upper()} artifact -> {args.out}")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
