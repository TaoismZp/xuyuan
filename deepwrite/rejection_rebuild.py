#!/usr/bin/env python3
"""Author REJECTED -> independent source-first DeepWrite rerun, preserving originals.

This is an additive adapter: the *released* DeepWrite v0.3 entrypoint remains
byte-for-byte unchanged and its activation resolver verifies release identity.
It does not make an author decision, claim semantic novelty or synthesize a
provider run. In particular, a ChatGPT-authored draft with no E18 run_state
is NOT eligible for a fake engine "resume".
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

DEEPWRITE = Path(__file__).resolve().parent
REPO = DEEPWRITE.parent
REQUEST_SCHEMA = "deepwrite/one-call-author-request/v1"
REJECTION_SCHEMA = "deepwrite/external-author-sample-rejection/v1"
RECEIPT_SCHEMA = "deepwrite/rejected-sample-research-restart/v1"
ID = re.compile(r"[A-Za-z0-9_-]{4,100}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
SOURCE = re.compile(r"sources/native_[0-9]{3}\.md\Z")


class Blocked(ValueError):
    pass


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def safe_path(value) -> Path:
    path = Path(value).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise Blocked("REJECTION_SYMLINK_FORBIDDEN")
    resolved = path.resolve()
    if resolved.is_relative_to(REPO.resolve()):
        raise Blocked("REJECTION_PRIVATE_DATA_INSIDE_PUBLIC_REPO")
    return resolved


def child(root: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or
            Path(relative).is_absolute() or
            ".." in Path(relative).parts):
        raise Blocked("REJECTION_UNSAFE_ARTIFACT_PATH")
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise Blocked("REJECTION_SYMLINK_SOURCE_FORBIDDEN")
    if not path.resolve().is_relative_to(root.resolve()):
        raise Blocked("REJECTION_PATH_ESCAPE")
    return path


def document(path: Path, expected_hash: str, label: str) -> bytes:
    if not SHA.fullmatch(str(expected_hash)):
        raise Blocked("REJECTION_EXTERNAL_SHA_REQUIRED_" + label)
    raw = path.read_bytes()
    if digest(raw) != expected_hash:
        raise Blocked("REJECTION_SHA_MISMATCH_" + label)
    return raw


def prepare(original_root, author_receipt, expected_receipt_sha,
            expected_old_state_sha, new_request_path, new_root):
    """Freeze author rejection, then prepare a *new* author-scoped source run.

    No old manuscript, outline, or source study text goes into model input.
    Its failures are represented only by an explicit user-authored negative
    constraint on the new wish; resemblance is NOT certified automatically.
    """
    original_root, new_root = safe_path(original_root), safe_path(new_root)
    author_receipt, new_request_path = safe_path(author_receipt), safe_path(new_request_path)
    if (original_root == new_root or original_root.is_relative_to(new_root) or
            new_root.is_relative_to(original_root)):
        raise Blocked("REJECTION_NEW_PROJECT_MUST_BE_INDEPENDENT")
    if new_root.exists() or new_request_path.exists():
        raise Blocked("REJECTION_NO_OVERWRITE_RESTART_OR_REQUEST")
    if new_request_path.is_relative_to(new_root) or new_root.is_relative_to(new_request_path):
        raise Blocked("REJECTION_REQUEST_MUST_BE_OUTSIDE_NEW_PROJECT")
    writer = original_root / "writer_project"
    evidence = original_root / "discovery_evidence"
    state_raw = document(writer / "run_state.json", expected_old_state_sha, "STATE")
    state = json.loads(state_raw)
    config = json.loads((evidence / "research" / "writer_config.json").read_bytes())
    if (state.get("status") != "AWAIT_AUTHOR_REVIEW" or
            state.get("execution_mode") != "ASSISTED_AUTHOR_GATED" or
            config.get("execution_contract", {}).get("mode") != "ASSISTED_AUTHOR_GATED"):
        raise Blocked("REJECTION_REQUIRES_REAL_AUTHOR_GATED_SAMPLE_CHECKPOINT")
    sample = config["execution_contract"].get("sample_chapters")
    if not isinstance(sample, list) or len(sample) != 1:
        raise Blocked("REJECTION_ONE_FROZEN_SAMPLE_REQUIRED")
    art = sample[0]
    completed = state.get("completed", {}).get("close_" + art)
    if not isinstance(completed, dict) or art not in completed:
        raise Blocked("REJECTION_COMPLETED_SOURCE_REVIEWED_CHAPTER_REQUIRED")
    chapter_path = child(writer, completed[art])
    expected_chapter = state.get("files", {}).get(completed[art])
    chapter = document(chapter_path, expected_chapter, "CHAPTER")
    if not chapter.startswith(b"# "):
        raise Blocked("REJECTION_SAMPLE_NOT_COMPLETE_MARKDOWN")
    receipt_raw = document(author_receipt, expected_receipt_sha, "AUTHOR_RECEIPT")
    rejection = json.loads(receipt_raw)
    method = rejection.get("verification", {})
    if (rejection.get("schema") != REJECTION_SCHEMA or
            rejection.get("status") != "REJECTED" or
            rejection.get("project_id") != config.get("project_id") or
            rejection.get("sample_artifact_id") != art or
            rejection.get("sample_artifact_sha256") != expected_chapter or
            rejection.get("expected_run_state_sha256") != expected_old_state_sha or
            rejection.get("execution_contract_sha256") != state.get("execution_contract_sha256") or
            method.get("method") != "EXTERNAL_OPERATOR_ATTESTATION" or
            method.get("model_generated") is not False or
            not isinstance(method.get("evidence_reference"), str) or
            not method["evidence_reference"].strip()):
        raise Blocked("REJECTION_NOT_MATCHED_TO_ACTUAL_AUTHOR_AND_FROZEN_ARTIFACT")
    reason = rejection.get("reason")
    if not isinstance(reason, str) or not 20 <= len(reason.strip()) <= 3000:
        raise Blocked("REJECTION_SUBSTANTIVE_AUTHOR_FEEDBACK_REQUIRED")
    new_id = rejection.get("new_project_id")
    if not isinstance(new_id, str) or not ID.fullmatch(new_id) or new_id == config["project_id"]:
        raise Blocked("REJECTION_UNIQUE_NEW_PROJECT_ID_REQUIRED")
    if (config.get("pins", {}).get("project_id") != config["project_id"] or
            state.get("config_sha256") != digest(canonical(config))):
        raise Blocked("REJECTION_ORIGINAL_PROJECT_IDENTITY_MISMATCH")
    request_raw = (evidence / "USER_REQUEST.json").read_bytes()
    original_request = json.loads(request_raw)
    if (original_request.get("schema") != REQUEST_SCHEMA or
            original_request.get("project_id") != config["project_id"] or
            original_request.get("mode") != "ASSISTED_AUTHOR_GATED" or
            original_request.get("authorized_scope") != "FIRST_SAMPLE_AFTER_DISCOVERY"):
        raise Blocked("REJECTION_ORIGINAL_USER_SCOPE_NOT_VERIFIABLE")
    contract = next((x for x in config["sources"] if x["path"] == "sources/author-contract.txt"), None)
    if contract is None:
        raise Blocked("REJECTION_AUTHOR_CONTRACT_MISSING")
    contract_raw = document(child(writer, contract["path"]), contract["sha256"], "CONTRACT")
    if json.loads(contract_raw).get("original_request_sha256") != digest(request_raw):
        raise Blocked("REJECTION_USER_REQUEST_ORIGIN_CHANGED")
    source_rows = [x for x in config["sources"] if SOURCE.fullmatch(x.get("path", ""))]
    if len(source_rows) != len(original_request["source_files"]) or not source_rows:
        raise Blocked("REJECTION_SOURCE_COUNT_CHANGED")
    native_sources = []
    for row in source_rows:
        source = child(writer, row["path"])
        if state.get("files", {}).get(row["path"]) != row["sha256"]:
            raise Blocked("REJECTION_SOURCE_STATE_SHA_MISMATCH")
        document(source, row["sha256"], "SOURCE")
        native_sources.append(str(source))
    new_request = dict(original_request)
    new_request["project_id"] = new_id
    new_request["source_files"] = native_sources
    # The model receives the human's critique but NOT old manuscript, outline,
    # selected question or previous model answer. Source study is genuinely fresh.
    new_request["wish"] = (
        original_request["wish"] + "\n\nAuthor rejected an earlier sample. "
        "Start source-domain research independently from the frozen ORIGINAL materials. "
        "Generate rival questions and derive a fresh book structure; do not merely "
        "polish or paraphrase the old question or fabricate an everyday scene. "
        "Negative author feedback (not a recommended outline): " + reason)
    if len(new_request["wish"]) > 12000:
        raise Blocked("REJECTION_REVISED_WISH_OVERSIZED")
    # Check original sample title separately in the outcome; do not send it to
    # research stage and bias the fresh discovery.
    original_chapter_title = next(x["title"] for x in config["chapters"] if x["artifact_id"] == art)
    lineage = {
        "schema": RECEIPT_SCHEMA,
        "status": "AUTHOR_REJECTED_REDISCOVERY_INPUT_PREPARED_NOT_MODEL_RUN",
        "original_project_id": config["project_id"],
        "new_project_id": new_id,
        "old_run_state_sha256": digest(state_raw),
        "old_chapter_sha256": digest(chapter),
        "old_chapter_title_sha256": digest(original_chapter_title.encode("utf-8")),
        "old_chapter_title": original_chapter_title,
        "author_receipt_sha256": digest(receipt_raw),
        "rejection_reason": reason,
        "source_bytes_sha256": [x["sha256"] for x in source_rows],
        "source_count": len(source_rows),
        "author_acceptance": "REJECTED_OLD_CHAPTER_NEW_UNVERIFIED",
        "identity_attestation": "SELF_REPORTED_EXTERNAL_NOT_CRYPTOGRAPHICALLY_VERIFIED",
        "new_model_calls": "NOT_RUN",
        "old_model_status": ("LIVE_CALLS_RECORDED" if state.get("calls") and
              all(x.get("is_live") is True for x in state["calls"].values()) else
              "NOT_VERIFIED_AS_LIVE_MODEL")
    }
    new_request_path.parent.mkdir(parents=True, exist_ok=True)
    new_request_path.write_bytes(canonical(new_request))
    provenance = new_request_path.with_suffix(".rejection.json")
    if provenance.exists():
        # Avoid leaving a second self-declared provenance on an existing path.
        new_request_path.unlink()
        raise Blocked("REJECTION_PROVENANCE_COLLISION")
    provenance.write_bytes(canonical({**lineage,
        "new_request_sha256": digest(new_request_path.read_bytes()),
        "private_new_project_root": str(new_root)}))
    return {**lineage, "status": "REJECTED_SAMPLE_RESET_PREPARED_MODEL_NOT_RUN",
            "request_file": str(new_request_path), "provenance_file": str(provenance),
            "project_root": str(new_root)}


def assess_new_run(prepared, result):
    """Never certify the first chapter's literary or human quality."""
    new_root = Path(prepared["project_root"])
    study = new_root / "discovery_evidence/research/STATE.json"
    config = new_root / "discovery_evidence/research/writer_config.json"
    state_file = new_root / "writer_project/run_state.json"
    out = {"status": "NEW_RUN_BLOCKED_OR_UNVERIFIED", "result": result,
           "quality": "UNVERIFIED", "human_acceptance": "PENDING",
           "original_chapter_preserved": True}
    if not all(x.is_file() for x in (study, config, state_file)):
        return out
    study_data = json.loads(study.read_bytes())
    new_config = json.loads(config.read_bytes())
    state = json.loads(state_file.read_bytes())
    title = new_config["chapters"][0]["title"]
    if title.strip().casefold() == prepared["old_chapter_title"].strip().casefold():
        out["status"] = "BLOCKED_REJECTED_FIRST_CHAPTER_TITLE_REUSED"
        return out
    if (len(study_data.get("model_calls", [])) < 2 or
            state.get("status") != "AWAIT_AUTHOR_REVIEW" or
            not state.get("calls") or
            any(not x.get("response_id") for x in state["calls"].values())):
        return out
    if (study_data.get("live_provider_verified") is True and
            all(x.get("is_live") is True for x in state["calls"].values())):
        out["status"] = "LIVE_V0_3_NEW_SAMPLE_AWAIT_AUTHOR_REVIEW_NOT_QUALITY_PASS"
    else:
        out["status"] = "ENGINEERING_FIXTURE_ONLY_NOT_LIVE"
    out["new_chapter_title"] = title
    out["new_run_state_sha256"] = digest(state_file.read_bytes())
    out["new_source_study_sha256"] = digest((new_root / "writer_project" /
        new_config["source_first_architecture"]["source_study"]["path"]).read_bytes())
    return out


def run_release(prepared, timeout_seconds=7200):
    """Actually invoke formally released v0.3; no manual prose as substitute."""
    activation = DEEPWRITE / "release/activation.py"
    command = [sys.executable, "-B", str(activation), "--root", str(REPO),
               "--run", "--", "run", prepared["request_file"], prepared["project_root"]]
    log = Path(prepared["provenance_file"]).with_suffix(".execution.json")
    if log.exists():
        raise Blocked("REJECTION_EXECUTION_RECEIPT_ALREADY_EXISTS")
    try:
        proc = subprocess.run(command, cwd=REPO, capture_output=True, text=True,
                              timeout=timeout_seconds)
        execution = {"command": [sys.executable, "-B", "deepwrite/release/activation.py",
             "--root", ".", "--run", "--", "run", "<PRIVATE_REQUEST>", "<PRIVATE_PROJECT>"],
             "exit_code": proc.returncode, "stdout": proc.stdout[-15000:],
             "stderr": proc.stderr[-10000:], "real_provider": "UNVERIFIED_UNTIL_TRACE"}
        if proc.returncode == 0:
            try:
                result = json.loads(proc.stdout)
            except json.JSONDecodeError:
                result = {"status": "INVALID_EXECUTOR_STDOUT"}
            report = assess_new_run(prepared, result)
        else:
            report = {"status": "BLOCKED_RELEASED_ENGINE_EXIT_NONZERO",
                      "exit_code": proc.returncode, "quality": "UNVERIFIED",
                      "human_acceptance": "NOT_RUN"}
    except subprocess.TimeoutExpired:
        execution = {"exit_code": "TIMEOUT_UNCERTAIN_CALL_MUST_NOT_AUTO_RETRY"}
        report = {"status": "BLOCKED_TIMEOUT_DO_NOT_OVERWRITE_OR_AUTO_RETRY",
                  "quality": "UNVERIFIED", "human_acceptance": "NOT_RUN"}
    log.write_bytes(canonical({"execution": execution, "assessment": report}))
    return report


def main():
    parser = argparse.ArgumentParser(description="DeepWrite author rejection -> fresh source-first E18 sample run")
    parser.add_argument("original_private_project", type=Path)
    parser.add_argument("external_author_rejection", type=Path)
    parser.add_argument("new_private_request", type=Path)
    parser.add_argument("new_private_project", type=Path)
    parser.add_argument("--expected-author-rejection-sha256", required=True)
    parser.add_argument("--expected-original-state-sha256", required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    try:
        prepared = prepare(args.original_private_project, args.external_author_rejection,
                           args.expected_author_rejection_sha256,
                           args.expected_original_state_sha256,
                           args.new_private_request, args.new_private_project)
        if args.prepare_only:
            report = prepared
        else:
            report = {"prepared": {k: v for k,v in prepared.items() if k not in
                      ("rejection_reason", "old_chapter_title")},
                      "run": run_release(prepared)}
    except Exception as err:
        report = {"status": "BLOCKED", "code": type(err).__name__,
                  "reason": str(err)[:300], "author_acceptance": "NOT_RUN"}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "REJECTED_SAMPLE_RESET_PREPARED_MODEL_NOT_RUN" or (
        report.get("run", {}).get("status") ==
        "LIVE_V0_3_NEW_SAMPLE_AWAIT_AUTHOR_REVIEW_NOT_QUALITY_PASS") else 2


if __name__ == "__main__":
    sys.exit(main())
