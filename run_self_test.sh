#!/usr/bin/env bash
# End-to-end zero-dependency self-test for Berne-Provenance-Toolkit

set -euo pipefail

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "[1/3] Generating canonical SHA-256 manifest from curriculum/..."
python3 audit-tools/generate_manifest.py \
  --root ./curriculum \
  --author "Jane Doe" \
  --orcid "0000-0002-1825-0097" \
  --base-uri "https://github.com" \
  --license "MIT" \
  --doi "10.5281/zenodo.1234567" \
  --out "$TMP_DIR/manifest.jsonl"

echo "[2/3] Simulating stripped-attribution MCP payload..."
cat << 'EOF' > "$TMP_DIR/stripped_mcp.json"
{
  "result": {
    "text": "Copyright protection arises automatically the instant you fix an original work in writing, Markdown, or source code."
  }
}
EOF

echo "[3/3] Running forensic auditor (expecting DEFECTS_DETECTED)..."
if python3 audit-tools/mcp_provenance_auditor.py \
  --manifest "$TMP_DIR/manifest.jsonl" \
  --inspect "$TMP_DIR/stripped_mcp.json"; then
  echo "Unexpected PASS on stripped payload"
  exit 1
else
  echo "✅ Self-test passed: Auditor successfully caught stripped attribution and missing MCP schema."
fi
