#!/usr/bin/env python3
"""Candidate fail-closed bridge: E18 book -> PR26 source audit -> author-review gate.

This verifies artifact identities and audit evidence shape, NOT real comprehension
or literary quality. Not part of the formally activated DeepWrite v0.3.1.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

TRUSTED_GATE_GIT_BLOB_SHA1 = "f790049eaa9b3583b6bd0cb3bd51674eb59f47d4"

class Hold(ValueError):
    pass

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise Hold("INVALID_JSON_OBJECT:" + path.name)
    return obj

def safe(root, relative):
    p = Path(relative)
    if p.is_absolute() or not p.parts or ".." in p.parts:
        raise Hold("PATH_ESCAPE")
    dest = root / p
    if not dest.resolve().is_relative_to(root.resolve()) or any(q.is_symlink() for q in (dest, *dest.parents) if q != root.parent):
        raise Hold("SYMLINK_OR_ESCAPE")
    return dest

def require(condition, msg):
    if not condition:
        raise Hold(msg)

def verify(project, bundle, gate):
    project, bundle = project.resolve(), bundle.resolve()
    require(gate.is_file() and not gate.is_symlink(), "TRUSTED_AUDIT_GATE_MISSING_OR_SYMLINK")
    gate_bytes = gate.read_bytes()
    actual_gate_blob = hashlib.sha1(b"blob " + str(len(gate_bytes)).encode() + b"\0" + gate_bytes).hexdigest()
    require(actual_gate_blob == TRUSTED_GATE_GIT_BLOB_SHA1, "UNTRUSTED_AUDIT_GATE_IDENTITY")
    require(not bundle.is_relative_to(project / "writer_project"), "AUDIT_EVIDENCE_CANNOT_OVERWRITE_WRITER")
    binding = load(safe(bundle, "BINDING.json"))
    book = safe(project, binding.get("selected_book_relative", ""))
    require(book.is_file(), "SELECTED_BOOK_MISSING")
    raw = book.read_bytes()
    book_sha = digest(raw)
    require(book_sha == binding.get("selected_book_sha256"), "SELECTED_BOOK_SHA_MISMATCH")
    require(book_sha == binding.get("final_read_book_sha256"), "FINAL_READ_STALE_BOOK")
    primary = safe(project, "writer_project/book.md")
    require(primary.is_file(), "E18_BOOK_MISSING")
    result = load(safe(project, "discovery_evidence/RESULT.json"))
    config = load(safe(project, "discovery_evidence/research/writer_config.json"))
    writer_state = safe(project, "writer_project/run_state.json")
    require(writer_state.is_file(), "E18_WRITER_STATE_MISSING")
    primary_state = load(writer_state)
    require(result.get("writer_state_sha256") == digest(writer_state.read_bytes()), "WRITER_STATE_SHA_MISMATCH")
    require(result.get("writer_config_sha256") == digest(safe(project, "discovery_evidence/research/writer_config.json").read_bytes()), "WRITER_CONFIG_SHA_MISMATCH")
    mode = config.get("execution_contract", {}).get("mode")
    require(mode == "AUTONOMOUS_FULL_DRAFT", "AUTHOR_GATED_MODE_MUST_NOT_SKIP_SAMPLE")
    status = primary_state.get("status")
    require(status in ("CANDIDATE_PENDING_HUMAN", "ENGINEERING_FIXTURE_ONLY_NOT_LIVE"), "E18_NOT_FINISHED")
    require(result.get("writer_result", {}).get("status") == status, "E18_RESULT_STATUS_MISMATCH")
    require(primary_state.get("files", {}).get("book.md") == digest(primary.read_bytes()), "E18_TRACKED_BOOK_CHANGED")
    topo = result.get("bookwide_topology_recheck", {})
    topology_status = topo.get("status")
    require(topology_status in ("STRUCTURE_KEPT_MODEL_INTERNAL_ONLY", "REPLAN_DERIVATION_PENDING_HUMAN"), "TOPOLOGY_NOT_CLOSED")
    if topology_status == "STRUCTURE_KEPT_MODEL_INTERNAL_ONLY":
        require(book == primary, "KEEP_SELECTED_BOOK_MISMATCH")
    else:
        derived = safe(project, "writer_project_topology_r2/book.md")
        require(book == derived and topo.get("derived_book_sha256") == book_sha, "REPLAN_MUST_AUDIT_DERIVED_BOOK")
        require(topo.get("derived_writer_result", {}).get("status") in
                ("CANDIDATE_PENDING_HUMAN", "ENGINEERING_FIXTURE_ONLY_NOT_LIVE"), "DERIVED_BOOK_NOT_FINISHED")
    require(binding.get("writer_result_sha256") == digest(safe(project, "discovery_evidence/RESULT.json").read_bytes()), "RESULT_STALE")
    require(binding.get("author_acceptance") == "NOT_RUN", "MODEL_MUST_NOT_SIGN_AUTHOR")
    receipts = binding.get("receipts", [])
    require(isinstance(receipts, list) and receipts, "ACTUAL_READ_RECEIPTS_REQUIRED")
    cmd = [sys.executable, str(gate), "complete", "--source", str(book),
           "--contract", str(safe(bundle, "CONTRACT.json")),
           "--manifest", str(safe(bundle, "MANIFEST.json")),
           "--semantic-ledger", str(safe(bundle, "SEMANTIC_LEDGER.json"))]
    for rec in receipts:
        cmd += ["--receipt", str(safe(bundle, rec))]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    require(proc.returncode == 0, "PR26_SOURCE_AUDIT_GATE_FAILED:" + proc.stderr[:180])
    gate_report = json.loads(proc.stdout)
    require(gate_report.get("status") == "SOURCE_RECEIPTS_COMPLETE_SCOPED", "SOURCE_AUDIT_NOT_COMPLETE")
    record = load(safe(bundle, "SEMANTIC_LEDGER.json"))
    require(record.get("book_sha256") == book_sha, "SEMANTIC_LEDGER_STALE")
    require(isinstance(record.get("sections"), list) and record["sections"], "SECTION_SEMANTICS_MISSING")
    require(isinstance(record.get("issue_clusters"), list), "ISSUE_LEDGER_MISSING")
    require(isinstance(record.get("final_read"), dict), "FINAL_READ_MISSING")
    reread = record["final_read"]
    require(reread.get("book_sha256") == book_sha, "FINAL_READ_STALE")
    require(reread.get("status") == "READ_CONFIRMED" and bool(reread.get("response_id")), "FINAL_READ_RECEIPT_MISSING")
    manifest = load(safe(project, "writer_project/manifest.json"))
    ids = ["FRONT", *[f"CH{i+1:02d}" for i in range(len(manifest.get("chapters", [])))], "TAIL"]
    section_map = {s.get("id"): s for s in record["sections"]}
    require(set(section_map) == set(ids) and len(section_map) == len(ids), "WHOLE_CHAPTER_SEMANTIC_COVERAGE_REQUIRED")
    require(reread.get("section_ids") == ids, "FINAL_READ_SECTION_ORDER_OR_COVERAGE_FAIL")
    for item in section_map.values():
        require(item.get("book_sha256") == book_sha and len(str(item.get("mechanism", ""))) >= 25
                and len(str(item.get("counterargument", ""))) >= 25 and bool(item.get("response_id")),
                "SECTION_SEMANTICS_UNVERIFIED")
    for item in record["issue_clusters"]:
        if item.get("severity") in ("MAJOR", "CRITICAL"):
            require(item.get("status") == "CLOSED" and bool(item.get("repair_artifact")), "UNRESOLVED_MAJOR_ISSUE")
        elif item.get("status") not in ("CLOSED", "KEEP"):
            raise Hold("UNRESOLVED_OPEN_ISSUE")
    return {"status": "ENGINEERING_EVIDENCE_PASS_BOOK_QUALITY_UNVERIFIED", "book_sha256": book_sha,
            "receipts_verified": gate_report["read_receipts_verified"], "segments": len(ids),
            "author_acceptance": "NOT_RUN", "reader_quality": "UNVERIFIED"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--audit-gate", type=Path, required=True)
    args = p.parse_args()
    try:
        result = verify(args.project, args.bundle, args.audit_gate)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (Hold, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as e:
        print(json.dumps({"status": "FAIL_CLOSED", "reason": str(e)[:220]}, ensure_ascii=False), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
