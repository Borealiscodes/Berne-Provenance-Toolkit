# Engineering Uplift Roadmap (`v1.0` → `v2.0`)

**Repository:** `Borealiscodes/Berne-Provenance-Toolkit`  
**Governance Posture:** Zero-Dependency Core • Offline-First • Berne Art. 2/6bis & W3C ODRL Aligned  
**Maintainer:** Borealis Serenity Hedling (ORCID: `0009-0004-7968-5707`)

---

## Overview

This roadmap outlines four incremental releases (`v1.1` through `v2.0`) designed to evolve **Berne-Provenance-Toolkit** from a standalone CLI utility into an ecosystem-ready provenance standard—while strictly preserving its **zero-dependency Python 3 core** so creators on any device can audit files offline.

---

## Release 1: Multi-Source Synthesis & Chunk-Level Provenance (`v1.1`)

**Goal:** Eliminate false-positive integrity failures when AI systems or RAG pipelines legitimately synthesize, quote, or blend multiple authored documents.

* **Schema Expansion (`audit-tools/mcp-provenance.schema.json`):**
  * Add a `synthesis_mode` enum (`"verbatim"`, `"excerpt"`, `"synthesis"`).
  * Replace the single-source assumption with a `sources: []` array so multi-document outputs credit every upstream `author_orcid`, `source_uri`, `license_spdx`, and `chunk_hashes` list.
* **Paragraph & Section Shingling (`audit-tools/generate_manifest.py`):**
  * Compute both the full-file `sha256` and a list of normalized **paragraph/section SHA-256 digests** plus **5-gram Jaccard/MinHash fingerprints** using only Python's standard `hashlib` and `re` modules.
* **Nuanced Audit Codes (`audit-tools/mcp_provenance_auditor.py`):**
  * **`SYNTHESIS-ATTRIBUTED` *(Pass)*:** Multiple upstream sources are credited in `sources[]`, `modified: true` is declared honestly, and shingle overlap aligns with cited works.
  * **`BERNE-6BIS-QUOTE-MUTATION` *(Fail)*:** Direct quotation marks or `synthesis_mode: "verbatim"` are used, but paragraph digests fail verification.
  * **`PROVENANCE-LAUNDERING-SYNTHESIS` *(Fail)*:** High n-gram overlap (`>25%`) is detected against two or more anchored manifests with missing upstream ORCIDs or URIs.

---

## Release 2: Zero-Dependency PDF & Binary Document Support (`v1.2`)

**Goal:** Enable creators and auditors to anchor and inspect `.pdf` preprints (such as Zenodo deposits) without requiring heavy third-party PDF libraries.

* **Dual-Hash Manifest Entries:**
  * Store `binary_sha256` (exact byte hash of the `.pdf` container) alongside `extracted_text_sha256` (normalized UTF-8 text hash) and PDF XMP/Info dictionary metadata (`Author`, `Title`, `DOI`).
* **Pure-Stdlib PDF Text Extractor (`audit-tools/extractors/pdf_stdlib.py`):**
  * Use Python’s built-in `zlib` and `re` modules to decompress standard `FlateDecode` PDF content streams and parse `BT ... ET` text operators (`Tj`, `TJ`) offline with zero external dependencies.
* **Graceful External Adapter Fallback:**
  * Add a `--pdf-backend` CLI flag (`auto` | `stdlib` | `pdftotext` | `pypdf`) that automatically delegates to `pdftotext` or `pypdf` if installed in the environment, falling back seamlessly to `pdf_stdlib.py` on restricted or offline systems.

---

## Release 3: Drop-In Developer Middleware & Git Automation (`v1.3`)

**Goal:** Make adoption effortless for MCP server builders and open-source maintainers.

* **1-Line MCP Server Decorator (`integrations/mcp_middleware.py`):**
  * Provide a lightweight `@berne_provenance` Python decorator compatible with `FastMCP` and the official `mcp` SDK that automatically wraps tool outputs into a valid `mcp-provenance.schema.json` JSON envelope at runtime.
* **Git `pre-commit` Hook (`.pre-commit-hooks.yaml`):**
  * Allow any GitHub repository to auto-update and verify `manifest/provenance-chain.jsonl` on every `git commit`, preventing stale hashes as repositories evolve.
* **GitHub Action CI Workflow (`.github/workflows/provenance-audit.yml`):**
  * Provide a copy-pasteable GitHub Action that validates manifest signatures and fails pull requests if attributed files are modified without updating provenance metadata.

---

## Release 4: Ecosystem Interoperability — SPDX, C2PA & Verifiable Credentials (`v2.0`)

**Goal:** Bridge **Berne-Provenance-Toolkit** with existing industry provenance and compliance standards so manifests travel across platforms.

* **SPDX & CFF Importers (`integrations/spdx_bridge.py`):**
  * Parse existing repository `CITATION.cff` files and **SPDX** Software Bills of Materials (SBOMs) to auto-populate author ORCIDs, licenses, and repository URIs without duplicate data entry.
* **C2PA & W3C ODRL Export (`governance/exporters.py`):**
  * Export `provenance-chain.jsonl` records as **W3C ODRL** machine-readable policy assertions or **C2PA (Coalition for Content Provenance and Authenticity)** compatible JSON assertions for cross-tool verification.
* **Detached Ed25519 Signing via OpenSSH:**
  * Support detached cryptographic signatures (`.sig`) via standard `ssh-keygen -Y sign` (built into OpenSSH on Linux, macOS, and Windows—preserving zero Python dependencies) so manifests are tamper-evident without external crypto packages.

---

## Milestone Execution Summary

| Release | Key Deliverable | Primary Files Affected | Dependency Impact |
| :--- | :--- | :--- | :--- |
| **`v1.1`** | Multi-source synthesis & paragraph chunk hashing | `mcp-provenance.schema.json`, `mcp_provenance_auditor.py` | Zero dependencies (`stdlib` only) |
| **`v1.2`** | Dual-hash PDF anchoring & `zlib` stream parser | `generate_manifest.py`, `extractors/pdf_stdlib.py` | Zero core (`pdftotext`/`pypdf` optional) |
| **`v1.3`** | `@berne_provenance` MCP decorator & `pre-commit` | `integrations/mcp_middleware.py`, `.pre-commit-hooks.yaml` | Zero core (`mcp` SDK optional) |
| **`v2.0`** | `CITATION.cff` / SPDX bridge & OpenSSH signing | `integrations/spdx_bridge.py`, `governance/exporters.py` | Zero Python deps (uses system `ssh-keygen`) |
