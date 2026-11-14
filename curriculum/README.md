# 📚 Author-Rights & Provenance Literacy Curriculum (`curriculum/`)

**Part of:** [`Berne-Provenance-Toolkit`](../README.md)  
**Governance Posture:** Educational • Descriptive-Only • Sealed-Layer Neutral (`Author Sovereignty Charter v1.2`)  
**Canonical Lineage Anchor:** [`DOI: 10.5281/zenodo.24149283`](https://doi.org)  
**Maintainer:** Borealis S. Hedling (`ORCID: 0009-0004-7968-5707`) · Dublin, Ireland  

---

## 1. Purpose of This Curriculum
Technical verification tools (`SHA-256` manifests, `Ed25519` signatures, and JSON Schemas) only protect creators when authors understand **what legal rights attach to their work automatically** and **how automated pipelines attempt to strip them**.

These three short, plain-language modules bridge the gap between international copyright law (**Berne Convention** & **Irish CRRA 2000**) and practical software engineering—empowering writers, researchers, and developers to protect both their **Sovereignty** (cryptographic custody) and their **Autonomy** (creative voice and agency).

---

## 2. Curriculum Modules

| Module | File | Core Focus & Key Takeaways |
| :--- | :--- | :--- |
| **Module 01** | [`01-berne-convention-and-author-autonomy.md`](./01-berne-convention-and-author-autonomy.md) | **The Berne Convention & Author Autonomy:** Explains automatic copyright without registration (**Art. 5(2)**), human intellectual creation (**Art. 2**), inalienable moral rights (**Art. 6bis** / **Irish CRRA 2000 Ch. 7**), and why **Autonomy** is just as essential as **Sovereignty**. |
| **Module 02** | [`02-open-licenses-vs-moral-rights.md`](./02-open-licenses-vs-moral-rights.md) | **Open Licenses vs. Moral Rights:** Debunks the myth that `MIT`, `Apache-2.0`, or `CC-BY-4.0` allow attribution stripping or silent LLM rewriting; shows how paternity and integrity rights persist alongside open reuse. |
| **Module 03** | [`03-anatomy-of-mcp-and-aggregator-laundering.md`](./03-anatomy-of-mcp-and-aggregator-laundering.md) | **MCP & Aggregator Provenance Laundering:** Maps how multi-hop scrapers and flat-text MCP servers strip headers, mutate text, and launder citations—plus the 3 architectural rules to fix them. |

---

## 3. From Reading to Forensic Auditing
Once you have reviewed the modules above:
1. Record your canonical file digests in [`../manifest/provenance-chain.jsonl`](../manifest/provenance-chain.jsonl).
2. Run the zero-dependency forensic CLI in [`../audit-tools/mcp_provenance_auditor.py`](../audit-tools/mcp_provenance_auditor.py) against any MCP server response or scraped Markdown file to verify compliance with **Berne Article 6bis** and your open-source license headers.

---

*Disclaimer: All curriculum modules in this directory are descriptive educational resources and do not constitute formal legal advice.*
