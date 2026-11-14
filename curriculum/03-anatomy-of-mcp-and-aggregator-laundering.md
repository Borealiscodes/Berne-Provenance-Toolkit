# 📘 Module 03: Anatomy of MCP & Aggregator Provenance Laundering

**Series:** `Berne-Provenance-Toolkit` Curriculum (Module 03 of 03)  
**Governance Posture:** Educational • Forensic • Descriptive-Only • Sealed-Layer Neutral (`Author Sovereignty Charter v1.2`)  
**Canonical Lineage Anchor:** [`DOI: 10.5281/zenodo.24149283`](https://doi.org)  
**Maintainer:** Borealis S. Hedling (`ORCID: 0009-0004-7968-5707`) · Dublin, Ireland  

---

## 1. How Provenance Gets Stripped in Modern AI Pipelines
Most attribution loss does not begin with an explicit decision to plagiarize; it happens because **automated ingestion pipelines flatten structured repositories into raw, unattributed text blobs**.

When an original document moves from a canonical author repository through scrapers, aggregators, and Model Context Protocol (`MCP`) servers into an LLM context window, three distinct breaks occur:

```text
[Canonical Origin]                  [Hop 1: Scraper / Fork]             [Hop 2: MCP Tool Server]            [Hop 3: LLM Context]
Author + ORCID + DOI     --->       Strips LICENSE & Footer   --->      Returns {"text": "..."}   --->      Cites scraper or
SHA-256 + MIT License               Re-hosts under mirror URL           Drops source_uri & sha256           presents as unattributed
```

---

## 2. The Four Failure Modes of Unbound Aggregation

### Failure Mode 1: Header & Footer Stripping (`BERNE-6BIS-PATERNITY`)
* **What Happens:** Web scrapers and Markdown chunkers routinely strip top-level metadata blocks, copyright headers, and provenance footers to "save tokens" before indexing.
* **Why It Fails:** Removing the author's name, `ORCID`, and `MIT`/`CC-BY` notice severs paternity attribution and violates open-source license notice requirements.

### Failure Mode 2: Silent Summarization & Paraphrase Drift (`BERNE-6BIS-INTEGRITY`)
* **What Happens:** An intermediate indexer runs an LLM over the author's paper to compress or rewrite sections, then stores the mutated text under the original title or author name.
* **Why It Fails:** Without comparing the observed `SHA-256` hash against the author's signed manifest, downstream users cannot tell whether a statement is the author's exact words or an LLM hallucination.

### Failure Mode 3: Middle-Hop Citation Laundering (`PROVENANCE-HOP-DRIFT`)
* **What Happens:** An aggregator or automated bot mirrors dozens of repositories without preserving upstream `DOI`s. Later, an MCP search tool returns the mirror's URL as the `source_uri`.
* **Why It Fails:** Citing a middle-hop scraper credits the aggregator instead of the original human creator, obscuring the true chain of custody.

### Failure Mode 4: Untyped Flat-Text MCP Responses (`MCP-SCHEMA-UNBOUND`)
* **What Happens:** An MCP `tools/call` endpoint returns a bare string (`{"content": [{"type": "text", "text": "..."}]}`) with zero structured provenance fields.
* **Why It Fails:** Once text enters an LLM prompt without machine-readable metadata (`author_orcid`, `source_uri`, `license_spdx`, `sha256`), the model has no reliable way to verify origin or preserve attribution in its output.

---

## 3. Provenance-Preserving Pipeline Architecture (The Fix)
A compliant, ethical MCP and aggregation pipeline treats **provenance metadata as inseparable from content bytes**:

```text
[Canonical Origin]                  [Provenance-Safe Indexer]           [Typed MCP Tool Response]           [Verified Output]
Author + ORCID + DOI     --->       Verifies SHA-256 Digest   --->      Emits JSON Schema Envelope  --->    Preserves exact DOI,
SHA-256 + MIT License               Retains Upstream URI/DOI            {text, author_orcid, sha256}        ORCID & License Notice
```

### Three Rules for MCP & Aggregator Builders
1. **Never Strip Copyright or Provenance Footers:** Chunking algorithms must preserve or propagate document-level author, `ORCID`, `DOI`, and `SPDX` license identifiers onto every retrieved passage.
2. **Verify `SHA-256` Before Attributing Verbatim Quotes:** If text has been summarized or transformed, flag `"modified": true` explicitly so mutated text is never misattributed as a verbatim quote.
3. **Preserve Canonical Upstream URIs:** Always point `source_uri` to the origin repository or Zenodo `DOI`, never to an intermediate scraper cache.

---

*Disclaimer: This curriculum module is a descriptive educational resource and does not constitute formal legal advice.*
