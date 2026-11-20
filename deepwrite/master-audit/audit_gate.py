#!/usr/bin/env python3
"""Fail-closed *evidence* gate for DeepWrite master audit.

Verifies byte coverage and attributable read receipts. This does NOT certify
actual human/model comprehension, literary quality, or author sign-off.
No network, third-party dependencies, or manuscript output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys


def die(reason: str) -> None:
    raise ValueError(reason)


def load(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        die("NOT_JSON_OBJECT:" + str(path))
    return data


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def git_blob(blob: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()


def validate_contract(contract: dict, actual_sha: str) -> None:
    required = ("project_id", "author_goal", "source_blob_sha1",
                "workflow_policy", "author_fulltext_required")
    if any(not contract.get(k) for k in required):
        die("MISSING_MASTER_AUDIT_CONTRACT")
    if contract["author_fulltext_required"] is not True:
        die("FULL_CHAPTER_AUTHOR_DELIVERY_MUST_BE_TRUE")
    if contract["source_blob_sha1"] != actual_sha:
        die("CONTRACT_SOURCE_SHA_MISMATCH")


def validate_manifest(manifest: dict, source: bytes, actual_sha: str) -> list:
    chunks = manifest.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        die("NO_SOURCE_CHUNKS")
    if manifest.get("source_blob_sha1", manifest.get("git_blob_sha1")) != actual_sha:
        die("MANIFEST_GIT_BLOB_MISMATCH")
    declared_length = manifest.get("source_bytes_utf8", manifest.get("source_bytes"))
    if declared_length != len(source):
        die("SOURCE_LENGTH_MISMATCH")
    if manifest.get("source_sha256", manifest.get("sha256")) != sha256(source):
        die("SOURCE_SHA256_MISMATCH")
    expected_byte = 0
    previous_line = 0
    for i, part in enumerate(chunks, 1):
        first, last = part.get("start_byte"), part.get("end_byte_exclusive")
        if not isinstance(first, int) or not isinstance(last, int) or first != expected_byte or last <= first or last > len(source):
            die("SOURCE_BYTE_COVERAGE_FAIL_AT:" + str(i))
        if part.get("sha256") != sha256(source[first:last]):
            die("CHUNK_SHA256_MISMATCH:" + str(i))
        line_from = part.get("start_line")
        line_to = part.get("end_line")
        if not isinstance(line_from, int) or not isinstance(line_to, int) or line_from != previous_line + 1 or line_to < line_from:
            die("LINE_COVERAGE_FAIL_AT:" + str(i))
        expected_byte = last
        previous_line = line_to
    if expected_byte != len(source) or previous_line != len(source.splitlines()):
        die("INCOMPLETE_SOURCE_COVERAGE")
    return chunks


def validate_receipts(files: list[Path], chunks: list, source: bytes, source_sha: str) -> dict:
    expected = {part["id"]: part for part in chunks}
    seen: dict = {}
    for path in files:
        envelope = load(path)
        if envelope.get("source_blob") != source_sha:
            die("RECEIPT_SOURCE_BLOB_MISMATCH:" + str(path))
        rows = envelope.get("receipts", envelope.get("records"))
        if not isinstance(rows, list) or not rows:
            die("RECEIPT_LIST_EMPTY:" + str(path))
        for row in rows:
            key = row.get("id")
            if key not in expected or key in seen:
                die("UNKNOWN_OR_DUPLICATED_RECEIPT:" + str(key))
            part = expected[key]
            for field in ("start_byte", "end_byte_exclusive", "start_line", "end_line"):
                if row.get(field) != part.get(field):
                    die("RECEIPT_CHUNK_BOUNDARY_MISMATCH:" + str(key))
            if row.get("source_chunk_sha256") != part.get("sha256") or row.get("source_blob") != source_sha:
                die("RECEIPT_CHUNK_HASH_MISMATCH:" + str(key))
            quote = row.get("quote")
            explanation = row.get("semantic_function")
            if not isinstance(quote, str) or len(quote.strip()) < 8:
                die("READING_QUOTE_REQUIRED:" + str(key))
            if not isinstance(explanation, str) or len(explanation.strip()) < 24:
                die("SUBSTANTIVE_EDIT_NOTE_REQUIRED:" + str(key))
            raw = source[part["start_byte"]:part["end_byte_exclusive"]].decode("utf-8")
            if quote not in raw:
                die("QUOTE_NOT_IN_FROZEN_CHUNK:" + str(key))
            if not str(row.get("status", "")).startswith("READ_CONFIRMED"):
                die("NO_REAL_READ_CONFIRMATION:" + str(key))
            seen[key] = row
    return seen


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("phase", choices=["preflight", "progress", "complete"])
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--receipt", action="append", type=Path, default=[])
    p.add_argument("--semantic-ledger", type=Path)
    args = p.parse_args()
    try:
        source = args.source.read_bytes()
        source.decode("utf-8")
        actual_sha = git_blob(source)
        validate_contract(load(args.contract), actual_sha)
        parts = validate_manifest(load(args.manifest), source, actual_sha)
        if args.phase != "preflight" and not args.receipt:
            die("PROGRESS_REQUIRES_ACTUAL_RECEIPTS")
        seen = validate_receipts(args.receipt, parts, source, actual_sha) if args.receipt else {}
        if args.phase == "complete":
            if len(seen) != len(parts):
                die("STRICT_FULL_READ_INCOMPLETE")
            if args.semantic_ledger is None or not args.semantic_ledger.is_file() or args.semantic_ledger.stat().st_size < 100:
                die("SEMANTIC_BOOKWIDE_LEDGER_REQUIRED")
        print(json.dumps({
            "phase": args.phase, "mechanical_source_coverage": "PASS",
            "chunks_total": len(parts), "read_receipts_verified": len(seen),
            "unread": len(parts) - len(seen), "source_blob": actual_sha,
            "status": "SOURCE_RECEIPTS_COMPLETE_SCOPED" if args.phase == "complete"
                      else "PARTIAL_EVIDENCE_ONLY_NOT_BOOK_QUALITY_PASS",
            "book_literary_quality": "UNVERIFIED", "author_approval": "PENDING"
        }, ensure_ascii=False))
        return 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL_CLOSED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
