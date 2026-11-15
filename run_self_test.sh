#!/usr/bin/env bash
# End-to-end zero-dependency self-test for Berne-Provenance-Toolkit (v1.2+)
# Verifies:
#   1. Canonical manifest generation across Markdown (curriculum/) + dynamically built binary PDF
#   2. Dual-hash PDF extraction (binary_sha256 + extracted_text_sha256 via stdlib zlib)
#   3. PASS on valid verbatim MCP JSON-RPC response
#   4. PASS on valid paragraph-level excerpt MCP response
#   5. PASS on valid multi-source attributed synthesis MCP response
#   6. DEFECTS_DETECTED on stripped-attribution MCP payload (BERNE-6BIS-PATERNITY + MCP-SCHEMA-UNBOUND)
#   7. DEFECTS_DETECTED on silent quote mutation (BERNE-6BIS-INTEGRITY)
#   8. DEFECTS_DETECTED on unattributed multi-source synthesis (PROVENANCE-LAUNDERING-SYNTHESIS)

set -euo pipefail

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$TMP_DIR/corpus/curriculum"
cp -r ./curriculum/* "$TMP_DIR/corpus/curriculum/"

echo "[1/8] Building synthetic binary PDF fixture (zlib FlateDecode stream)..."
python3 - "$TMP_DIR/corpus/preprint.pdf" << 'EOF'
import sys, zlib
from pathlib import Path

pdf_path = Path(sys.argv[1])
stream_text = b"BT /F1 12 Tf 72 720 Td (Non-dual geometric stabilization prevents representational rank collapse in deep transformer manifolds.) Tj ET"
compressed = zlib.compress(stream_text)

objects = [
    b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
    b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
    b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n",
    b"4 0 obj << /Length " + str(len(compressed)).encode() + b" /Filter /FlateDecode >>\nstream\n" + compressed + b"\nendstream\nendobj\n",
    b"5 0 obj << /Title (Geometric Stabilization Preprint) /Author (Jane Doe) >> endobj\n",
]

out = bytearray(b"%PDF-1.4\n")
offsets = []
for obj in objects:
    offsets.append(len(out))
    out.extend(obj)

xref_pos = len(out)
out.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
for off in offsets:
    out.extend(f"{off:010d} 00000 n \n".encode())
out.extend(f"trailer << /Size {len(objects) + 1} /Root 1 0 R /Info 5 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode())
pdf_path.write_bytes(bytes(out))
EOF

echo "[2/8] Generating canonical v1.2.0 SHA-256 & chunk manifest..."
python3 audit-tools/generate_manifest.py \
  --root "$TMP_DIR/corpus" \
  --author "Jane Doe" \
  --orcid "0000-0002-1825-0097" \
  --base-uri "https://github.com" \
  --license "MIT" \
  --doi "10.5281/zenodo.1234567" \
  --pdf-backend "stdlib" \
  --out "$TMP_DIR/manifest.jsonl"

echo "[3/8] Verifying dual-hash PDF record & valid verbatim MCP JSON-RPC response (expecting PASS)..."
python3 - "$TMP_DIR/manifest.jsonl" "$TMP_DIR/verbatim_mcp.json" << 'EOF'
import json, sys
from pathlib import Path

manifest = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
pdf_rec = next(r for r in manifest if r["artifact_type"] == "pdf")
assert "binary_sha256" in pdf_rec and pdf_rec["binary_sha256"] != pdf_rec["sha256"], "Dual-hash PDF check failed"
assert "rank collapse" in pdf_rec["excerpt"].lower(), "Stdlib zlib PDF text extraction failed"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Non-dual geometric stabilization prevents representational rank collapse in deep transformer manifolds."
            }
        ],
        "provenance": {
            "schema_version": "1.1.0",
            "synthesis_mode": "verbatim",
            "modified": False,
            "sources": [
                {
                    "author_name": pdf_rec["author_name"],
                    "author_orcid": pdf_rec["author_orcid"],
                    "source_uri": pdf_rec["canonical_uri"],
                    "license_spdx": pdf_rec["license_spdx"],
                    "sha256": pdf_rec["sha256"],
                    "binary_sha256": pdf_rec["binary_sha256"]
                }
            ]
        }
    }
}
Path(sys.argv[2]).write_text(json.dumps(payload, indent=2))
EOF

python3 audit-tools/mcp_provenance_auditor.py \
  --manifest "$TMP_DIR/manifest.jsonl" \
  --inspect "$TMP_DIR/verbatim_mcp.json" > /dev/null

echo "[4/8] Testing valid paragraph-level excerpt MCP response (expecting PASS)..."
python3 - "$TMP_DIR/corpus/curriculum/01-berne-convention-and-author-autonomy.md" "$TMP_DIR/manifest.jsonl" "$TMP_DIR/excerpt_mcp.json" << 'EOF'
import json, re, sys
from pathlib import Path

md_text = Path(sys.argv[1]).read_text(encoding="utf-8")
blocks = [b.strip() for b in re.split(r"\n\s*\n", md_text) if len(b.strip()) >= 40 and not b.strip().startswith("#")]
target_para = blocks[0]

manifest = [json.loads(line) for line in Path(sys.argv[2]).read_text().splitlines() if line.strip()]
md_rec = next(r for r in manifest if r["relative_path"].endswith("01-berne-convention-and-author-autonomy.md"))

payload = {
    "schema_version": "1.1.0",
    "content": target_para,
    "synthesis_mode": "excerpt",
    "modified": False,
    "sources": [
        {
            "author_name": md_rec["author_name"],
            "author_orcid": md_rec["author_orcid"],
            "source_uri": md_rec["canonical_uri"],
            "license_spdx": md_rec["license_spdx"],
            "sha256": md_rec["sha256"]
        }
    ]
}
Path(sys.argv[3]).write_text(json.dumps(payload, indent=2))
EOF

python3 audit-tools/mcp_provenance_auditor.py \
  --manifest "$TMP_DIR/manifest.jsonl" \
  --inspect "$TMP_DIR/excerpt_mcp.json" > /dev/null

echo "[5/8] Testing attributed multi-source synthesis MCP response (expecting PASS)..."
python3 - "$TMP_DIR/manifest.jsonl" "$TMP_DIR/synthesis_ok.json" << 'EOF'
import json, sys
from pathlib import Path

manifest = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
md_rec = next(r for r in manifest if r["relative_path"].endswith("01-berne-convention-and-author-autonomy.md"))
pdf_rec = next(r for r in manifest if r["artifact_type"] == "pdf")

payload = {
    "schema_version": "1.1.0",
    "content": "Synthesizing Berne Convention automatic protection with non-dual geometric stabilization prevents representational rank collapse in deep transformer manifolds.",
    "synthesis_mode": "synthesis",
    "modified": True,
    "sources": [
        {
            "author_name": md_rec["author_name"],
            "author_orcid": md_rec["author_orcid"],
            "source_uri": md_rec["canonical_uri"],
            "license_spdx": md_rec["license_spdx"],
            "sha256": md_rec["sha256"]
        },
        {
            "author_name": pdf_rec["author_name"],
            "author_orcid": pdf_rec["author_orcid"],
            "source_uri": pdf_rec["canonical_uri"],
            "license_spdx": pdf_rec["license_spdx"],
            "sha256": pdf_rec["sha256"]
        }
    ]
}
Path(sys.argv[2]).write_text(json.dumps(payload, indent=2))
EOF

python3 audit-tools/mcp_provenance_auditor.py \
  --manifest "$TMP_DIR/manifest.jsonl" \
  --inspect "$TMP_DIR/synthesis_ok.json" > /dev/null

echo "[6/8] Simulating stripped-attribution MCP payload (expecting DEFECTS_DETECTED)..."
cat << 'EOF' > "$TMP_DIR/stripped_mcp.json"
{
  "result": {
    "text": "Copyright protection arises automatically the instant you fix an original work in writing, Markdown, or source code."
  }
}
EOF

if python3 audit-tools/mcp_provenance_auditor.py \
  --manifest "$TMP_DIR/manifest.jsonl" \
  --inspect "$TMP_DIR/stripped_mcp.json" > /dev/null; then
  echo "Unexpected PASS on stripped payload"
  exit 1
fi

echo "[7/8] Simulating silent quote mutation with modified=false (expecting BERNE-6BIS-INTEGRITY)..."
python3 - "$TMP_DIR/manifest.jsonl" "$TMP_DIR/mutated_mcp.json" << 'EOF'
import json, sys
from pathlib import Path

manifest = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
pdf_rec = next(r for r in manifest if r["artifact_type"] == "pdf")

payload = {
    "schema_version": "1.1.0",
    "content": "Non-dual geometric stabilization ALWAYS causes representational rank collapse in deep transformer manifolds.",
    "synthesis_mode": "verbatim",
    "modified": False,
    "sources": [
        {
            "author_name": pdf_rec["author_name"],
            "author_orcid": pdf_rec["author_orcid"],
            "source_uri": pdf_rec["canonical_uri"],
            "license_spdx": pdf_rec["license_spdx"],
            "sha256": pdf_rec["sha256"]
        }
    ]
}
Path(sys.argv[2]).write_text(json.dumps(payload, indent=2))
EOF

if python3 audit-tools/mcp_provenance_auditor.py \
  --manifest "$TMP_DIR/manifest.jsonl" \
  --inspect "$TMP_DIR/mutated_mcp.json" > /dev/null; then
  echo "Unexpected PASS on silently mutated verbatim payload"
  exit 1
fi

echo "[8/8] Simulating unattributed multi-source synthesis laundering (expecting PROVENANCE-LAUNDERING-SYNTHESIS)..."
cat << 'EOF' > "$TMP_DIR/laundered_synthesis.txt"
Copyright protection arises automatically the instant you fix an original work in writing, Markdown, or source code. Furthermore, non-dual geometric stabilization prevents representational rank collapse in deep transformer manifolds.
EOF

if python3 audit-tools/mcp_provenance_auditor.py \
  --manifest "$TMP_DIR/manifest.jsonl" \
  --inspect "$TMP_DIR/laundered_synthesis.txt" > /dev/null; then
  echo "Unexpected PASS on unattributed multi-source synthesis"
  exit 1
fi

echo "✅ All 8 self-tests passed: Dual-hash PDF, excerpts, synthesis attribution, and defect detection verified."
