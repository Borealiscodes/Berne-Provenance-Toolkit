# ⚖️ Berne-Provenance-Toolkit
**An Operational Forensic CLI Tool, Middleware & Author-Rights Curriculum for Auditing MCP Servers, Scrapers, and Multi-Hop Aggregators**

**Type:** Practical Software Prototype (Zero-Dependency Python 3 CLI + JSON Schemas + Middleware) & Educational Curriculum  
**Version:** `v2.0.0` *(Prototype — Pre-Production)*  
**Governance Posture:** Educational • Forensic • Descriptive-Only • Sealed-Layer Neutral (`Author Sovereignty Charter v1.2`)  
**Canonical Lineage Anchor:** [`DOI: 10.5281/zenodo.24149283`](https://doi.org) · [`DOI: 10.5281/zenodo.24240994`](https://doi.org)  
**Maintainer:** Borealis S. Hedling (`ORCID: 0009-0004-7968-5707`) · Dublin, Ireland  

---

## ⚠️ Prototype Status & Epistemic Humility Notice

> **No Provenance System Is Infallible — Unverified Prototype Code:**  
> `Berne-Provenance-Toolkit` is an early-stage research prototype that has not undergone independent security auditing or large-scale production testing. It aims to surface structural anomalies via cryptographic hashes and shingle-overlap heuristics rather than provide adversarial immunity.
>
> For production-grade security and content credentials, users should pair this toolkit with established frameworks:
> * **[C2PA](https://github.com):** Industry-standard cryptographic manifests for digital media.
> * **[Sigstore (`cosign` / `rekor`)](https://github.com):** Keyless code signing and transparency logs.
> * **[in-toto](https://github.com) & [SLSA](https://github.com):** Software supply-chain integrity and verifiable builds.
> * **[SPDX](https://github.com) & [CITATION.cff](https://github.com):** Standardized SBOM licensing and academic citation formats.

*Disclaimer: This repository is a forensic software prototype and educational resource and does not constitute formal legal advice.*

---

## 1. Scope & Governance Distinction: Good-Faith Ecosystems vs. Malicious Extraction

`Berne-Provenance-Toolkit` (`v2.0`) distinguishes between collaborative knowledge work and exploitative extraction:
1. **Good-Faith Constellation Ecosystems & Reversible Corrections:** In open research networks and digital gardens, ideas evolve and synthesize legitimately. When participants maintain transparent lineage (`synthesis_mode: "synthesis"` or `modified: true`) and enable reversible corrections for dropped metadata, minor drift is normal organization rather than misconduct.
2. **Malicious Scraping, Attribution Stripping & Opaque Aggregators:** Conversely, scrapers and MCP wrappers become harmful when they strip author identities, present mutated LLM outputs as verbatim (`modified: false`), or launder downstream mirrors to sever creators from their work.

---

## 2. What This Tool Does

The toolkit provides four core zero-dependency components:
1. **Zero-Dependency Forensic CLI Tools (`audit-tools/`):** Includes `generate_manifest.py` for SHA-256 JSONL custody ledgers and paragraph chunk hashes, `extractors/pdf_stdlib.py` for offline PDF stream/metadata extraction using standard Python libraries, and `mcp_provenance_auditor.py` for auditing MCP JSON-RPC responses and scraped text.
2. **MCP Server Middleware & Git Automation (`integrations/`, `.github/`):** Features the `@berne_provenance` decorator (`integrations/mcp_middleware.py`) and pre-commit/CI workflows.
3. **Ecosystem Bridges & Exporters (`integrations/spdx_bridge.py`, `governance/exporters.py`):** Importers for `CITATION.cff` and SPDX JSON SBOMs, plus exporters for W3C ODRL 2.2 JSON-LD, C2PA-aligned assertions, and OpenSSH Ed25519 signatures.
4. **Plain-Language Rights Curriculum (`curriculum/`):** Practical guides on how international copyright law automatically protects human authors despite open licenses like `MIT` or `CC-BY-4.0`.

---

## 3. The Berne Convention in Plain English

The **Berne Convention for the Protection of Literary and Artistic Works** (1886) governs international protection for creative and technical works:
* **Automatic Protection Without Formalities (Article 5(2)):** Copyright attaches automatically upon fixation without government registration.
* **Original Intellectual Creation (Article 2):** Covers works reflecting deliberate human creative choices, distinct from automated scraping or unedited LLM mutations.
* **Inalienable Moral Rights (Article 6bis · Irish CRRA 2000, Chapter 7):** Encompasses the **Right of Attribution (Paternity)**, **Right of Integrity** (objection to harmful distortion or alteration), and protection against false attribution.

---

## 4. Author Sovereignty & Author Autonomy

| Dimension | What It Means in Practice | How This Toolkit Supports It |
| :--- | :--- | :--- |
| **Author Sovereignty** *(Boundary & Custody)* | Controlling perimeters and proving origin via tamper-evident manifests and signed artifacts. | Dual-hash SHA-256 ledgers (`generate_manifest.py`), OpenSSH Ed25519 signatures (`exporters.py`), and W3C ODRL policies. |
| **Author Autonomy** *(Agency & Voice)* | Retaining human agency over how work travels, supporting good-faith synthesis while preventing distortion. | Multi-source synthesis attribution (`sources[]`), legal literacy curriculum, and forensic MCP auditing. |

---

## 5. Forensic Defect Taxonomy

* **`BERNE-6BIS-PATERNITY`** (Berne Art. 6bis(1) · CRRA 2000 § 107): Fingerprint matches source, but author identity or canonical URI is missing.
* **`BERNE-6BIS-INTEGRITY`** (Berne Art. 6bis(1) · CRRA 2000 § 109): Payload claims verbatim status (`modified != true`), but SHA-256 or chunk digest fails verification.
* **`PROVENANCE-HOP-DRIFT`**: Response cites a downstream mirror or scraper instead of the upstream canonical DOI/repository.
* **`MCP-SCHEMA-UNBOUND`** (W3C ODRL): MCP tool outputs flat, unattributed text or omits required metadata fields.
* **`PROVENANCE-LAUNDERING-SYNTHESIS`**: Significant 5-gram shingle overlap detected across multiple anchored sources without declaring upstream references in `sources[]`.

---

## 6. Repository Structure

```text
Berne-Provenance-Toolkit/
├── README.md                                              # Overview, Epistemic Humility Notice, Berne Primer & CLI Guide
├── ROADMAP.md                                             # Engineering Uplift Roadmap (v1.0 -> v2.0)
├── run_self_test.sh                                       # Zero-dependency 8-stage end-to-end self-test harness
├── .pre-commit-hooks.yaml                                 # Pre-commit hook definition for automated verification
├── .github/workflows/provenance-audit.yml                 # GitHub Actions CI workflow
├── curriculum/                                            # Plain-language rights guides (Articles 2, 5, 6bis, open licenses)
├── audit-tools/                                           # CLI tools (generate_manifest.py, auditor, PDF extractor, schemas)
├── integrations/                                          # MCP middleware (@berne_provenance) & SPDX/CITATION bridges
├── governance/                                            # W3C ODRL templates & C2PA/OpenSSH exporters
└── manifest/provenance-chain.example.jsonl                # Example custody ledger
```

---

## 7. Quick Forensic Workflow (Offline, Zero Dependencies)

```bash
# 1. Generate a canonical v1.2.0 SHA-256 & chunk manifest
python3 audit-tools/generate_manifest.py \
  --root ./docs \
  --author "Your Name" \
  --orcid "0000-0000-0000-0000" \
  --base-uri "https://github.com" \
  --license "MIT" \
  --doi "10.5281/zenodo.0000000" \
  --out manifest/provenance-chain.jsonl

# 2. Audit an MCP JSON-RPC response or scraped file
python3 audit-tools/mcp_provenance_auditor.py \
  --manifest manifest/provenance-chain.jsonl \
  --inspect sample_mcp_response.json

# 3. Export manifest to W3C ODRL 2.2 or C2PA-compatible JSON assertions
python3 governance/exporters.py \
  --manifest manifest/provenance-chain.jsonl \
  --format odrl \
  --out governance/policy.odrl.jsonld

# 4. Run the offline 8-stage self-test suite
bash run_self_test.sh
```
