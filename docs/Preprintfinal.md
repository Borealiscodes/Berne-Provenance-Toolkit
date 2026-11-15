# Operationalizing Moral Rights in AI Ingestion Pipelines: Zero-Dependency Forensic Provenance Auditing and Multi-Source Synthesis Verification for Model Context Protocol (MCP) Ecosystems

Author: Borealis Serenity Hedling (ORCID: 0009-0004-7968-5707)
Affiliation: Independent Systems Researcher & Interdisciplinary Artist (NDH-Research-Pilot)
Date: November 2026

Abstract

As Model Context Protocol (MCP) servers, retrieval-augmented generation (RAG) pipelines, and automated web scrapers ingest open-source repositories and scholarly preprints at scale, human creators face systematic provenance laundering: upstream author identities, persistent identifiers (ORCIDs, DOIs), and license boundaries are routinely stripped, while probabilistic model outputs silently mutate source text without disclosure. Although international copyright law—specifically Articles 2, 5(2), and 6bis of the Berne Convention—grants automatic protection and inalienable moral rights of paternity and integrity even under permissive licenses (MIT, CC-BY-4.0), creators lack lightweight, offline-capable tools to audit downstream AI pipelines. This paper introduces Berne-Provenance-Toolkit (v2.0), a zero-dependency Python 3 forensic CLI, JSON Schema envelope specification, and runtime middleware architecture. We formalize a multi-granularity cryptographic custody model combining full-document SHA-256 hashing, dual-hash PDF stream extraction, paragraph-level chunk digests, and 5-gram containment metrics to distinguish good-faith multi-source synthesis (SYNTHESIS-ATTRIBUTED) from silent quote mutation (BERNE-6BIS-INTEGRITY) and uncredited blending (PROVENANCE-LAUNDERING-SYNTHESIS). Finally, we situate this prototype alongside established industry standards (C2PA, Sigstore, in-toto, SLSA, and SPDX) and discuss governance boundaries separating reversible, good-faith knowledge organization from adversarial extraction.
Keywords: Berne Convention, Moral Rights, Model Context Protocol (MCP), Provenance Auditing, SHA-256 Custody Chains, Multi-Source Synthesis, W3C ODRL, C2PA, Author Autonomy, Open-Source Governance

1. Introduction: The Provenance Laundering Gap in AI Pipelines

Modern AI agent architectures increasingly rely on standardized tool-calling interfaces—most notably the Model Context Protocol (MCP)—to retrieve external documentation, source code, and scholarly literature into model context windows (Anthropic, 2024). While MCP standardizes transport between data sources and language models, standard tool responses frequently return unstructured, flat text strings devoid of cryptographic provenance, author attribution, or modification flags.
When automated scrapers, multi-hop aggregators, and MCP wrappers strip metadata prior to LLM synthesis, three structural failures emerge:
1. Attribution Stripping (Paternity Loss): Downstream consumers cannot trace claims back to canonical Digital Object Identifiers (DOIs), ORCIDs, or origin repositories.
2. Silent Text Mutation (Integrity Erosion): Probabilistic summarization or truncation alters technical numbers, legal caveats, or authorial intent while presenting the output as verbatim source material.
3. Middle-Hop Laundering: Downstream aggregators cite secondary scraper mirrors rather than upstream primary works, severing verifiable chains of custody.
Existing enterprise supply-chain frameworks—such as C2PA for digital media (Coalition for Content Provenance and Authenticity [C2PA], 2023), Sigstore for artifact signing (Newman et al., 2022), and in-toto / SLSA for build pipelines (Torres-Arias et al., 2019)—provide gold-standard cryptographic assurances for heavy infrastructure. However, independent writers, artists, and researchers working on constrained devices or offline environments require a zero-dependency, human-legible toolset capable of anchoring plain-text, source-code, and PDF artifacts directly against statutory moral-rights norms.

2. Legal-Technical Grounding: Berne Moral Rights and Open Licenses

Under the Berne Convention for the Protection of Literary and Artistic Works (1886/1979), copyright protection attaches automatically upon fixation without registration formalities (Article 5(2)) and covers original intellectual creations in literary, scientific, and artistic domains (Article 2). Crucially, Article 6bis (implemented in Irish domestic law via Chapter 7 of the Copyright and Related Rights Act 2000) establishes moral rights independent of economic transfer:
• Right of Attribution (Paternity): The right to be identified as the creator of a work.
• Right of Integrity: The right to object to any distortion, mutilation, or other derogatory modification that would be prejudicial to the author's honor or reputation.
A widespread misconception in software and AI engineering is that releasing works under permissive licenses (MIT, Apache-2.0, CC-BY-4.0) waives moral rights or permits unattributed ingestion. In fact, open licenses explicitly condition reuse on preserving copyright and attribution notices, and statutory moral rights remain intact unless validly waived under applicable national law.

2.1 Governance Distinction: Good-Faith Synthesis vs. Malicious Extraction

A rigorous provenance framework must avoid penalizing legitimate scholarly synthesis or collaborative knowledge management:
• Good-Faith Constellation Ecosystems: In open research networks, digital gardens, and collaborative repositories, ideas are legitimately synthesized, summarized, and cross-referenced. When pipelines declare synthesis_mode: "synthesis" (modified: true) and credit all upstream sources transparently, reversible corrections to dropped metadata represent normal collaborative housekeeping rather than bad faith.
• Malicious Scraping & Opaque Laundering: Conversely, adversarial scrapers and unattributed MCP wrappers harm authors when they deliberately strip upstream identifiers, masquerade altered text as verbatim (modified: false), or obscure primary origins behind mirror forks.

3. System Architecture: Multi-Granularity Forensic Auditing

To operationalize both Author Sovereignty (cryptographic boundary and custody proof) and Author Autonomy (preserving human voice and fair synthesis), Berne-Provenance-Toolkit (v2.0) implements a four-layer zero-dependency Python 3 architecture (stdlib only).

3.1 Canonical Manifest Generation & Dual-Hash PDF Anchoring

Let an authored corpus \(\mathcal{C} = \{d_1, d_2, \dots, d_m\}\) consist of Markdown, source code, or binary .pdf preprints. For each document \(d_{i}\), generate_manifest.py computes a multi-granularity fingerprint record \(R_{i}\) stored in an append-only JSON Lines ledger (provenance-chain.jsonl):
1. Normalized Text Digest (\(H_{\text{text}}\)): Line endings and redundant whitespace are canonicalized via \(\nu(d_i)\), yielding:
\(H_{\text{text}}(d_{i})=\text{SHA-256}\big(\text{UTF-8}(\nu (d_{i}))\big)\)
2. Dual-Hash Binary Container Digest (\(H_{\text{bin}}\)): For .pdf deposits, a pure-stdlib extractor (extractors/pdf_stdlib.py, utilizing built-in zlib stream decompression and BT ... ET operator parsing with optional pdftotext/pypdf delegation) extracts embedded UTF-8 text and XMP/Info metadata (Title, Author, DOI) while separately recording the exact container hash \(H_{\text{bin}}(d_i) = \text{SHA-256}(\text{bytes}(d_i))\).
3. Paragraph-Level Chunk Digests (\(C_{i}\)): Splitting \(\nu(d_i)\) into substantive blocks \(b_{i,1}, \dots, b_{i,k}\) (≥ 40 characters) produces a set of block hashes:
\(C_{i}=\big\{\text{SHA-256}(b_{i,j})\;\big|{}\;j=1,\dots ,k\big\}\)
enabling exact verification of direct excerpts without requiring full-document reproduction.
4. 5-Gram Word Shingle Sets (\(S_{i}\)): Extracting normalized alphanumeric 5-grams \(S_i \subset \Sigma^5\) supports overlap detection across paraphrased or multi-source synthesized outputs.

3.2 Synthesis-Aware Forensic Auditing & Containment Metrics

Given an observed MCP JSON-RPC payload or scraped text Y with normalized text body \(T_{Y}\), mcp_provenance_auditor.py computes \(H_{\text{text}}(T_Y)\), paragraph chunks \(C_{Y}\), and 5-gram shingles \(S_{Y}\). Against each anchored record \(R_{i}\), it evaluates the shingle containment coefficient:
\(\mu (S_{Y},S_{i})=\frac{|{}S_{Y}\cap S_{i}|{}}{\min (|{}S_{Y}|{},|{}S_{i}|{})}\)
An artifact \(R_{i}\) is flagged as a contributing source if \(H_{\text{text}}(T_Y) = H_{\text{text}}(d_i)\), \(C_Y \cap C_i \neq \emptyset\), \(\mu(S_Y, S_i) \ge \tau\) (default τ = 0.25), or \(R_{i}\)'s canonical URI/DOI appears in \(T_{Y}\).
The auditor then enforces a formal five-code defect taxonomy:
The auditor classifies audit results and defects across a structured taxonomy, ranging from verified verbatim passes and transparent multi-source synthesis to schema non-compliance and moral-rights violations (such as BERNE-6BIS-PATERNITY, BERNE-6BIS-INTEGRITY, PROVENANCE-HOP-DRIFT, and PROVENANCE-LAUNDERING-SYNTHESIS), as detailed in the technical documentation of the reference repository Borealiscodes/Berne-Provenance-Toolkit.

4. Runtime Middleware and Ecosystem Interoperability

To minimize adoption friction for developers, the toolkit provides zero-dependency bridges across the software lifecycle:
• 1-Line MCP Decorator (@berne_provenance): Wraps Python MCP tool functions (compatible with FastMCP and the official mcp SDK) to emit schema-valid v1.1.0 JSON envelopes at runtime.
• Git pre-commit & CI Automation: Hooks and GitHub Actions workflows validate manifest integrity on commit and pull request events.
• Standards Interoperability (CITATION.cff, SPDX, W3C ODRL, C2PA, OpenSSH): Importers parse repository CITATION.cff and SPDX 2.3+ SBOM files (SPDX Workgroup, 2022), while exporters serialize custody ledgers into W3C ODRL 2.2 JSON-LD policies (Iannella & Villata, 2018), C2PA-aligned CreativeWork assertions, and detached Ed25519 signatures (.sig) via system ssh-keygen -Y sign.

5. Limitations, Epistemic Humility, and Gold-Standard Baselines

Berne-Provenance-Toolkit is an early-stage research prototype that has not undergone formal adversarial security auditing or large-scale production benchmarking. Three technical limitations must be noted:
1. Paraphrase Sensitivity: Deterministic 5-gram shingle containment detects verbatim copying, chunk extraction, and moderate mosaic synthesis, but deep semantic paraphrasing by frontier LLMs can evade lexical n-gram thresholds without neural embedding similarity.
2. PDF Stream Coverage: The zero-dependency zlib extractor handles uncompressed and standard FlateDecode PDF streams offline, whereas complex CIDFont encodings or encrypted PDFs require delegating to external backends (pdftotext or pypdf).
3. Complementary Role Alongside Industry Gold Standards: Cryptographic hashing detects post-anchoring tampering but does not establish hardware root-of-trust or transparency-log inclusion on its own. For production supply-chain security, practitioners should combine this toolkit with C2PA (C2PA, 2023), Sigstore (cosign/rekor; Newman et al., 2022), in-toto (Torres-Arias et al., 2019), and SLSA.

6. Conclusion

Protecting human creators in automated AI ecosystems does not require abandoning open licenses or imposing heavy infrastructure dependencies. By pairing statutory moral-rights principles with lightweight, zero-dependency SHA-256 custody chains, dual-hash PDF extraction, and synthesis-aware MCP schemas, Berne-Provenance-Toolkit offers a practical baseline for verifiable attribution and mathematical honesty across open-source and scholarly workflows.

References (APA 7th Edition)

• Anthropic. (2024). Introducing the Model Context Protocol. anthropic.com
• Berne Convention for the Protection of Literary and Artistic Works, September 9, 1886, as revised at Paris on July 24, 1971, and amended in 1979, S. Treaty Doc. No. 99-27 (1986). wipo.int
• Coalition for Content Provenance and Authenticity (C2PA). (2023). C2PA technical specification (Version 1.3). c2pa.org
• Copyright and Related Rights Act 2000, No. 28 of 2000 (Ireland). irishstatutebook.ie
• Iannella, R., & Villata, S. (Eds.). (2018). ODRL Information Model 2.2 (W3C Recommendation). World Wide Web Consortium. w3.org
• Newman, Z., Meyers, J. S., & Torres-Arias, S. (2022). Sigstore: Software signing for everybody. In Proceedings of the 2022 ACM SIGSAC Conference on Computer and Communications Security (pp. 2353–2367). Association for Computing Machinery. doi.org
• SPDX Workgroup. (2022). System Package Data Exchange (SPDX) specification version 2.3. The Linux Foundation. github.io
• Torres-Arias, S., Afzali, H., Kuppusamy, T. K., Curtmola, R., & Cappos, J. (2019). in-toto: Providing farm-to-table guarantees for bits and bytes. In 28th USENIX Security Symposium (USENIX Security 19) (pp. 1393–1410). USENIX Association. usenix.org

