# 📘 Module 02: Open Licenses vs. Moral Rights (Why MIT & CC-BY Do Not Erase Authorship)

**Series:** `Berne-Provenance-Toolkit` Curriculum (Module 02 of 03)  
**Governance Posture:** Educational • Descriptive-Only • Sealed-Layer Neutral (`Author Sovereignty Charter v1.2`)  
**Canonical Lineage Anchor:** [`DOI: 10.5281/zenodo.24149283`](https://doi.org)  
**Maintainer:** Borealis S. Hedling (`ORCID: 0009-0004-7968-5707`) · Dublin, Ireland  

---

## 1. The Most Common Myth in Open-Source & AI Ingestion
A widespread misconception among scraper operators and MCP developers is that *"if a repository uses an MIT or CC-BY license, we can strip the author's name, rewrite the text with an LLM, and serve it as unattributed context."*

**That assumption is legally and technically false.** Open-source licenses govern **economic copyright permissions** (copying, modifying, distributing), while **moral rights** protect the human creator's identity and textual integrity separately.

---

## 2. How Permissive Licenses Actually Work

| License Type | What It Grants Downstream Users | What It Explicitly Requires & Preserves |
| :--- | :--- | :--- |
| **`MIT` License** | Permission to use, copy, modify, merge, publish, and distribute the software or documentation. | **Mandatory Notice Preservation:** *"The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."* Stripping the copyright header violates the license itself. |
| **`Apache-2.0`** | Broad reuse, patent grant, and modification rights. | Requires retaining all copyright, patent, trademark, and attribution notices, plus **prominent notices stating that modified files were changed**. |
| **`CC-BY-4.0`** | Freedom to share and adapt creative or academic material for any purpose. | Requires giving **appropriate credit**, providing a link to the license, and **indicating if changes were made**—without suggesting the licensor endorses the downstream use. |

---

## 3. Why Moral Rights Persist Under Irish & EU Law
Under **Berne Convention Article 6bis** and **Ireland's Copyright and Related Rights Act 2000 (Chapter 7, §§ 107–119)**, moral rights belong personally to the human author and operate independently of economic licensing:

1. **Inalienable Paternity (§ 107):** Even when you release code or whitepapers under `MIT` or `CC-BY-4.0`, your right to be identified as the creator remains intact unless explicitly waived in writing by you.
2. **Protection Against Silent Distortion (§ 109):** Downstream aggregators or AI pipelines may fork or adapt open-licensed works, **but they may not silently alter your text while leaving your name attached** in a way that distorts your meaning or harms your professional integrity.
3. **No False Attribution (§ 113):** Automated tools cannot attribute synthetic LLM hallucinations or mangled summaries to a human author's `ORCID` or name.

---

## 4. Practical Takeaways for Authors & Tool Builders
* **For Authors:** Using `MIT` or `CC-BY-4.0` lets people learn from and build upon your work freely while keeping your legal right to credit (`BERNE-6BIS-PATERNITY`) and accurate representation (`BERNE-6BIS-INTEGRITY`) enforceable.
* **For MCP & Aggregator Developers:** Passing flat, unattributed text chunks strips mandatory `MIT`/`CC-BY` notices. Every tool response should preserve `author_orcid`, `source_uri`, `license_spdx`, and a `sha256` digest so downstream consumers know whether a file is verbatim or modified.

---

*Disclaimer: This curriculum module is a descriptive educational resource and does not constitute formal legal advice.*
