# ⚖️ Berne-Provenance-Toolkit
**An Operational Forensic CLI Tool & Author-Rights Curriculum for Auditing MCP Servers, Scrapers, and Multi-Hop Aggregators**

**Type:** Practical Software Tool (Zero-Dependency Python 3 CLI + JSON Schemas) & Educational Curriculum  
**Governance Posture:** Educational • Forensic • Descriptive-Only • Sealed-Layer Neutral (`Author Sovereignty Charter v1.2`)  
**Canonical Lineage Anchor:** [`DOI: 10.5281/zenodo.24149283`](https://doi.org)  
**Maintainer:** Borealis S. Hedling (`ORCID: 0009-0004-7968-5707`) · Dublin, Ireland  

---

## 1. What This Tool Does
`Berne-Provenance-Toolkit` is a **hands-on forensic utility and educational guide** built for writers, researchers, and open-source developers. Instead of relying on vague policy wishes, it gives creators two concrete instruments:
1. **Zero-Dependency Forensic CLI Tools (`audit-tools/`):** Local Python 3 utilities (`generate_manifest.py` and `mcp_provenance_auditor.py`) that anchor canonical files with `SHA-256` digests and inspect Model Context Protocol (`MCP`) JSON responses or scraped Markdown files for stripped attribution, silent text alteration, and middle-hop provenance laundering.
2. **A Plain-Language Rights Curriculum (`curriculum/`):** Short, practical guides explaining how international copyright law protects human authors automatically—even when code or essays are shared under open licenses like `MIT` or `CC-BY-4.0`.

*Disclaimer: This is a forensic software tool and educational resource. It does not constitute formal legal advice and operates strictly under non-activation boundaries.*

---

## 2. The Berne Convention in Plain English
The **Berne Convention for the Protection of Literary and Artistic Works** (1886, ratified by over 180 countries including Ireland, the EU, the UK, and the US) is the foundational international treaty protecting creative and technical works—including essays, documentation, whitepapers, and software source code.

Three core rules make the Berne Convention directly relevant to AI ingestion and MCP pipelines:
* **Automatic Protection Without Formalities (Article 5(2)):** Copyright attaches automatically the moment a human fixes an original work in writing or code. Authors do not need to register with a government office, pay fees, or hide behind a paywall for their rights to exist.
* **Original Intellectual Creation (Article 2):** Protection covers works reflecting free, deliberate human creative choices. Automated scraping, bulk repository mirroring, and unedited LLM text mutations do not create new independent authorship or erase upstream human origin.
* **Inalienable Moral Rights (Article 6bis · Irish CRRA 2000, Chapter 7):** Separate from economic rights, moral rights protect the human author's personal bond with their work:
  * **Right of Attribution (Paternity):** The right to be identified as the creator of your work.
  * **Right of Integrity:** The right to object to distortion, mutilation, or silent alteration that harms your reputation or misrepresents your meaning.
  * **Protection Against False Attribution:** The right not to have someone else's automated output or altered text falsely credited to you.

---

## 3. Why Author Autonomy Matters Just as Much as Sovereignty
In technical governance, people often focus exclusively on **Sovereignty**—building cryptographic walls and custody records. True creator protection requires **both Sovereignty and Autonomy** working together:

| Dimension | What It Means in Practice | How This Toolkit Supports It |
| :--- | :--- | :--- |
| **Author Sovereignty** *(Boundary & Custody)* | **Controlling your perimeter and proving origin.** Signing your artifacts, maintaining tamper-evident manifests, and preventing unauthorized appropriation. | `SHA-256` custody chains (`generate_manifest.py`), `Ed25519` signatures, and W3C `ODRL` policies (`sovereignty.template.jsonld`). |
| **Author Autonomy** *(Agency & Voice)* | **Retaining active human choice over how your work travels and speaks.** Deciding how your ideas are framed, ensuring automated tools do not flatten or distort your voice, and preserving human agency against opaque extraction. | Plain-language legal literacy (`curriculum/`) plus forensic MCP auditing (`mcp_provenance_auditor.py`) that exposes silent distortion and attribution stripping. |

* **Sovereignty without Autonomy** leaves an author isolated behind locked walls with no safe way to share work openly.
* **Autonomy without Sovereignty** leaves an author's voice defenseless when automated scrapers and MCP tools strip context and rewrite intent.
* **Together**, they let authors publish openly under permissive licenses like `MIT` while keeping verifiable attribution, structural integrity, and human agency intact.

---

## 4. Forensic Defect Taxonomy (What the CLI Tool Detects)

| Audit Code | Statutory / Technical Basis | Forensic Signal Detected in MCP / Aggregators |
| :--- | :--- | :--- |
| **`BERNE-6BIS-PATERNITY`** | Berne Art. 6bis(1) · CRRA 2000 § 107 | Text matches an anchored source fingerprint (`SHA-256` / shingle overlap), but author identity (`ORCID` / name) or canonical URI is missing. |
| **`BERNE-6BIS-INTEGRITY`** | Berne Art. 6bis(1) · CRRA 2000 § 109 | Artifact retains author attribution or DOI (`modified != true`), but `SHA-256` digest fails verification due to silent LLM rewriting or truncation. |
| **`PROVENANCE-HOP-DRIFT`** | Chain-of-Custody Integrity | Aggregator or MCP response cites a downstream scraper or mirror fork instead of the upstream canonical DOI or origin repository. |
| **`MCP-SCHEMA-UNBOUND`** | W3C ODRL · Typed MCP Responses | MCP tool dumps flat, unattributed text strings without `author_name`, `author_orcid`, `source_uri`, `license_spdx`, `sha256`, or `modified` fields. |

---

## 5. Repository Structure

```text
Berne-Provenance-Toolkit/
├── README.md                                              # Tool Overview, Berne Primer, Autonomy & Defect Taxonomy
├── run_self_test.sh                                       # Zero-dependency end-to-end self-test script
├── curriculum/
│   ├── README.md                                          # Curriculum index & learning path
│   ├── 01-berne-convention-and-author-autonomy.md         # Plain-language guide to Berne Art. 2/5/6bis & CRRA 2000
│   ├── 02-open-licenses-vs-moral-rights.md                # Why MIT & CC-BY-4.0 do not waive moral rights
│   └── 03-anatomy-of-mcp-and-aggregator-laundering.md     # How multi-hop pipelines strip lineage
├── audit-tools/
│   ├── generate_manifest.py                               # Zero-dependency SHA-256 manifest generator CLI
│   ├── mcp_provenance_auditor.py                          # Zero-dependency Python 3 forensic CLI auditor
│   └── mcp-provenance.schema.json                         # Drop-in JSON Schema for provenance-safe MCP tools
├── governance/
│   └── sovereignty.template.jsonld                        # Author-agnostic W3C ODRL + Schema.org template
└── manifest/
    └── provenance-chain.example.jsonl                     # Author-agnostic example SHA-256 custody ledger
```

---

## 6. Quick Forensic Workflow (Offline, Zero Dependencies)

```bash
# 1. Generate a canonical SHA-256 manifest for your own documents
python3 audit-tools/generate_manifest.py \
  --root ./docs \
  --author "Your Name" \
  --orcid "0000-0000-0000-0000" \
  --base-uri "https://github.com" \
  --license "MIT" \
  --out manifest/provenance-chain.jsonl

# 2. Audit an MCP JSON response or scraped Markdown file against your manifest
python3 audit-tools/mcp_provenance_auditor.py \
  --manifest manifest/provenance-chain.jsonl \
  --inspect sample_mcp_response.json
```
