# 📘 Module 01: The Berne Convention & Author Autonomy (A Creator's Plain-Language Guide)

**Series:** `Berne-Provenance-Toolkit` Curriculum (Module 01 of 03)  
**Governance Posture:** Educational • Descriptive-Only • Sealed-Layer Neutral (`Author Sovereignty Charter v1.2`)  
**Canonical Lineage Anchor:** [`DOI: 10.5281/zenodo.24149283`](https://doi.org)  
**Maintainer:** Borealis S. Hedling (`ORCID: 0009-0004-7968-5707`) · Dublin, Ireland  

---

## 1. Why Every Writer, Researcher, and Developer Needs This Guide
When you publish an essay, whitepaper, documentation guide, or software repository on the open web, automated scrapers, repository aggregators, and Model Context Protocol (`MCP`) servers can ingest your work within seconds. Often, downstream pipelines strip your name, replace your canonical repository link with an intermediate scraper URL, or pass AI-altered text as if you wrote it.

Knowing how international copyright law actually works gives you **clarity, confidence, and verifiable leverage**—without needing a law degree or expensive registration portals.

---

## 2. Three Pillars of the Berne Convention (1886)
The **Berne Convention for the Protection of Literary and Artistic Works** is the core international treaty governing authorship across more than 180 countries (including Ireland, the European Union, the United Kingdom, and the United States). It protects **literary, scientific, and artistic works**—which explicitly includes technical essays, mathematical documentation, and computer source code.

### Pillar A: Automatic Protection Without Formalities (Article 5(2))
* **The Rule:** Copyright protection arises **automatically** the instant you fix an original work in writing, Markdown, or source code.
* **What It Means for You:** You do **not** have to register with a government office, pay filing fees, or lock your work behind a private paywall to own your copyright. Publishing publicly on GitHub or Zenodo does not surrender your authorship.

### Pillar B: Original Intellectual Creation (Article 2)
* **The Rule:** Protection applies to works that reflect **free, deliberate human creative choices**.
* **What It Means for You:** Bulk repository cloning, automated metadata scraping, and unedited statistical LLM mutations do **not** generate independent human authorship, nor do they erase the upstream human creator's rights.

### Pillar C: Inalienable Moral Rights (Article 6bis · Irish CRRA 2000, Chapter 7)
Separate from economic licensing (such as selling copies or granting open-source reuse), international and Irish/EU law protect the personal bond between a creator and their work:
1. **Right of Attribution / Paternity (Irish CRRA 2000 § 107):** Your right to be clearly identified as the author whenever your work is published, reproduced, or adapted.
2. **Right of Integrity (Irish CRRA 2000 § 109):** Your right to object to any distortion, mutilation, or silent alteration of your work that misrepresents your meaning or harms your honor and reputation.
3. **Protection Against False Attribution (Irish CRRA 2000 § 113):** Your right not to have someone else's text—or an AI model's hallucinated summary—falsely credited to your name.

---

## 3. Sovereignty vs. Autonomy: Why Creators Need Both
Technical governance discussions often focus solely on **Sovereignty**—cryptographic keys, hashes, and access walls. While Sovereignty is essential, protecting human creators in an AI-mediated ecosystem requires pairing **Sovereignty** with **Autonomy**:

| Principle | Core Focus | Practical Meaning for Creators |
| :--- | :--- | :--- |
| **Author Sovereignty** *(Boundary & Custody)* | **Who owns and verifies the artifact?** | Establishing tamper-evident custody (`SHA-256` digests, `Ed25519` signatures, canonical `DOI`s, and `ORCID` anchors) so origin cannot be erased or forged. |
| **Author Autonomy** *(Agency & Voice)* | **Who decides how the work speaks and travels?** | Preserving the human author's intentional framing, preventing automated tools from silently rewriting your tone or context, and keeping human judgment in control. |

* **Sovereignty alone** protects a locked vault, but can leave creators isolated if they want to collaborate openly.
* **Autonomy alone** expresses creative intent, but leaves your words vulnerable to silent stripping and distortion by automated pipelines.
* **Together**, Sovereignty and Autonomy allow you to share ideas openly under permissive licenses (`MIT`, `CC-BY-4.0`) while maintaining cryptographic receipts (`provenance-chain.jsonl`) and auditing downstream tools (`mcp_provenance_auditor.py`).

---

## 4. Practical Checklist for Creators Publishing Online
1. **Anchor Your Identity:** Include your full author name, `ORCID`, and canonical `DOI` or origin URL inside the header or provenance footer of every major document.
2. **Hash Your Releases:** Record the `SHA-256` digest of canonical files in a versioned manifest (`manifest/provenance-chain.jsonl`) so any silent downstream edit is immediately provable.
3. **Audit Downstream Tools:** Run `audit-tools/mcp_provenance_auditor.py` against MCP server responses or third-party aggregations to verify that attribution and text integrity remain intact.

---

*Disclaimer: This curriculum module is a descriptive educational resource and does not constitute formal legal advice.*
