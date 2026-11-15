#!/usr/bin/env python3
"""
pdf_stdlib.py — Zero-Dependency PDF Text, Metadata & Dual-Hash Extractor
Part of Berne-Provenance-Toolkit (v1.2+)

Uses strictly Python 3 standard library modules (zlib, re, hashlib, subprocess, shutil)
to compute binary container digests, parse PDF Info/XMP metadata, and extract UTF-8
text streams offline—with optional graceful fallback to pdftotext or pypdf.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import zlib
from pathlib import Path
from typing import Any, Dict, Optional


def normalize_text(text: str) -> str:
    """Normalize whitespace and line endings for deterministic SHA-256 hashing."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _unescape_pdf_literal(raw: str) -> str:
    """Unescape standard PDF literal string escape sequences."""
    replacements = {
        r"\n": "\n",
        r"\r": "\r",
        r"\t": "\t",
        r"\b": "\b",
        r"\f": "\f",
        r"\(": "(",
        r"\)": ")",
        r"\\ ": "\\",
        r"\\": "\\",
    }
    for esc, char in replacements.items():
        raw = raw.replace(esc, char)
    return raw


def _extract_metadata_stdlib(pdf_bytes: bytes) -> Dict[str, str]:
    """Extract basic Title, Author, and DOI fields from PDF Info/XMP dictionaries."""
    meta: Dict[str, str] = {}
    decoded_header = pdf_bytes.decode("latin-1", errors="ignore")

    for key in ("Title", "Author", "Subject", "Keywords"):
        match = re.search(rf"/{key}\s*\(([^()\\]*(?:\\.[^()\\]*)*)\)", decoded_header)
        if match:
            val = _unescape_pdf_literal(match.group(1)).strip()
            if val:
                meta[key] = val

    doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", decoded_header)
    if doi_match:
        meta["DOI"] = doi_match.group(1).rstrip(".)>;")

    return meta


def _extract_text_stdlib(pdf_bytes: bytes) -> str:
    """
    Decompress FlateDecode streams using built-in zlib and parse BT...ET text blocks.
    Handles both uncompressed and standard zlib-compressed content streams offline.
    """
    streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, flags=re.DOTALL)
    extracted_chunks = []

    for stream in streams:
        decompressed: Optional[bytes] = None
        try:
            decompressed = zlib.decompress(stream)
        except zlib.error:
            # Stream may be uncompressed ASCII/Latin-1 or use another filter
            if b"BT" in stream and b"ET" in stream:
                decompressed = stream

        if not decompressed:
            continue

        text_stream = decompressed.decode("latin-1", errors="ignore")
        bt_blocks = re.findall(r"BT\s*(.*?)\s*ET", text_stream, flags=re.DOTALL)

        for block in bt_blocks:
            # Match literal strings inside Tj or TJ array operators
            literals = re.findall(r"\(([^()\\]*(?:\\.[^()\\]*)*)\)", block)
            if literals:
                line = "".join(_unescape_pdf_literal(lit) for lit in literals)
                if line.strip():
                    extracted_chunks.append(line.strip())

    return normalize_text("\n".join(extracted_chunks))


def _extract_text_pdftotext(pdf_path: Path) -> Optional[str]:
    """Optional external delegation to Poppler's pdftotext CLI if installed."""
    if not shutil.which("pdftotext"):
        return None
    try:
        proc = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
        return normalize_text(proc.stdout)
    except (subprocess.SubprocessError, OSError):
        return None


def _extract_text_pypdf(pdf_path: Path) -> Optional[str]:
    """Optional external delegation to pypdf if installed in user environment."""
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return normalize_text("\n\n".join(pages))
    except Exception:
        return None


def extract_pdf_provenance(
    pdf_path: str | Path,
    backend: str = "auto",
) -> Dict[str, Any]:
    """
    Compute dual SHA-256 digests and extract text + metadata from a PDF file.

    Args:
        pdf_path: Path to the target .pdf file.
        backend: 'auto' | 'stdlib' | 'pdftotext' | 'pypdf'

    Returns:
        Dictionary containing binary_sha256, extracted_text, extracted_text_sha256,
        backend_used, and pdf_metadata.
    """
    path = Path(pdf_path)
    raw_bytes = path.read_bytes()
    binary_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    pdf_metadata = _extract_metadata_stdlib(raw_bytes)

    extracted_text: Optional[str] = None
    backend_used = "stdlib"

    if backend == "pdftotext":
        extracted_text = _extract_text_pdftotext(path)
        backend_used = "pdftotext"
    elif backend == "pypdf":
        extracted_text = _extract_text_pypdf(path)
        backend_used = "pypdf"
    elif backend == "auto":
        extracted_text = _extract_text_pdftotext(path)
        if extracted_text:
            backend_used = "pdftotext"
        else:
            extracted_text = _extract_text_pypdf(path)
            if extracted_text:
                backend_used = "pypdf"

    if not extracted_text:
        extracted_text = _extract_text_stdlib(raw_bytes)
        backend_used = "stdlib"

    text_sha256 = hashlib.sha256(extracted_text.encode("utf-8")).hexdigest()

    return {
        "binary_sha256": binary_sha256,
        "extracted_text": extracted_text,
        "extracted_text_sha256": text_sha256,
        "backend_used": backend_used,
        "pdf_metadata": pdf_metadata,
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 pdf_stdlib.py <path/to/file.pdf> [auto|stdlib|pdftotext|pypdf]")
        sys.exit(1)

    target = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "auto"
    result = extract_pdf_provenance(target, backend=mode)
    # Omit full text body in CLI summary preview
    preview = {k: v for k, v in result.items() if k != "extracted_text"}
    preview["extracted_char_count"] = len(result["extracted_text"])
    print(json.dumps(preview, indent=2))
