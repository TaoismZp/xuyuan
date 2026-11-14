#!/usr/bin/env python3
"""One DeepWrite entry: request -> native research -> derived chapters -> E18 book.

Do not confuse a released DeepWrite with an unmerged checked-out candidate.
Production default is determined by main CURRENT, not this file's existence.
This command simplifies selecting modules; it does not grant model credentials,
approve a manuscript, publish the work, or create an implicit author signature.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
DEEPWRITE = ROOT / "deepwrite"
REQUEST_SCHEMA = "deepwrite/one-call-author-request/v1"
MODES = {"AUTONOMOUS_FULL_DRAFT": "ALL_CANDIDATE_CHAPTERS",
         "ASSISTED_AUTHOR_GATED": "FIRST_SAMPLE_AFTER_DISCOVERY"}
SAFE_ID = re.compile(r"[A-Za-z0-9_-]{4,100}\Z")


class Blocked(ValueError):
    pass


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(data) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def git(*args: str) -> str:
    proc = subprocess.run(["git", "--no-replace-objects", "-C", str(ROOT), *args],
                          capture_output=True, text=True, timeout=25)
    if proc.returncode:
        raise Blocked("DEEPWRITE_GIT_COMMIT_IDENTITY_UNAVAILABLE")
    return proc.stdout.strip()


def private_path(value) -> Path:
    p = Path(value).absolute()
    if any(x.is_symlink() for x in (p, *p.parents)):
        raise Blocked("DEEPWRITE_PRIVATE_SYMLINK_NOT_ALLOWED")
    resolved = p.resolve()
    if resolved.is_relative_to(ROOT.resolve()):
        raise Blocked("DEEPWRITE_PRIVATE_PROJECT_INSIDE_PUBLIC_CODE")
    return resolved


def official_identity():
    current = json.loads((DEEPWRITE / "CURRENT.json").read_text("utf-8"))
    parent = json.loads((ROOT / "wish-delivery/CURRENT.json").read_text("utf-8"))
    return {
        "formal_workbench_version": current["active_workbench_version"],
        "formal_engine": current.get("active_engine"),
        "parent_version": parent["active_version"],
        "current_spec": current["active_workbench_spec"],
        "parent_spec": parent["active_spec"],
        "formal_engine_active": bool(current.get("active_engine"))
    }


def effective_channel():
    """Resolve formally verified stable engine; never run an unactivated writer on main."""
    ident = official_identity()
    if ident["formal_engine_active"]:
        activation = load("deepwrite_default_release_resolver", DEEPWRITE / "release/activation.py")
        released = activation.resolve(ROOT)
        if (released.get("status") != "ACTIVE_ENGINE_IDENTITY_VERIFIED_QUALITY_NOT_IMPLIED" or
                released.get("runner") != "deepwrite/deepwrite.py"):
            raise Blocked("DEEPWRITE_DEFAULT_RUNNER_NOT_FORMALLY_RELEASED")
        return "STABLE"
    if git("branch", "--show-current") == "main":
        raise Blocked("DEEPWRITE_MAIN_CURRENT_V0_1_NO_RELEASED_WRITER")
    return "CANDIDATE_OPT_IN"


def validate_request(request):
    if not isinstance(request, dict) or request.get("schema") != REQUEST_SCHEMA:
        raise Blocked("DEEPWRITE_EXPLICIT_USER_REQUEST_SCHEMA_REQUIRED")
    if not SAFE_ID.fullmatch(str(request.get("project_id", ""))):
        raise Blocked("DEEPWRITE_UNSAFE_PROJECT_ID")
    if any(not isinstance(request.get(k), str) or len(request[k].strip()) < 8
           for k in ("wish", "working_title")):
        raise Blocked("DEEPWRITE_AUTHOR_GOAL_AND_TITLE_REQUIRED")
    if not isinstance(request.get("model"), str) or not request["model"].strip():
        raise Blocked("DEEPWRITE_MODEL_ID_REQUIRED")
    if request.get("adapter") not in ("codex", "responses"):
        raise Blocked("DEEPWRITE_ACTUAL_MODEL_ADAPTER_REQUIRED")
    mode = request.get("mode")
    if mode not in MODES or request.get("authorized_scope") != MODES[mode]:
        raise Blocked("DEEPWRITE_EXPLICIT_FULL_OR_SAMPLE_SCOPE_REQUIRED")
    if not isinstance(request.get("source_files"), list) or not request["source_files"]:
        raise Blocked("DEEPWRITE_ORIGINAL_SOURCE_FILES_REQUIRED_NO_FABRICATED_SOURCE")
    if len(request["source_files"]) > 60 or len(set(map(str, request["source_files"]))) != len(request["source_files"]):
        raise Blocked("DEEPWRITE_SOURCE_LIST_DUPLICATE_OR_TOO_LONG")
    for key, lower, upper in (("min_chapters", 1, 40), ("max_chapters", 1, 40),
                              ("discovery_token_budget", 100, 2000000),
                              ("token_budget", 100, 8000000),
                              ("per_call_output_tokens", 100, 150000),
                              ("max_revision_rounds", 1, 20)):
        val = request.get(key)
        if type(val) is not int or not lower <= val <= upper:
            raise Blocked("DEEPWRITE_REQUEST_INTEGER_RANGE_" + key)
    if request["min_chapters"] > request["max_chapters"]:
        raise Blocked("DEEPWRITE_CHAPTER_BOUND_INVERSION")
    if not isinstance(request.get("reader_goal"), str) or not request["reader_goal"].strip():
        raise Blocked("DEEPWRITE_READER_GOAL_REQUIRED")
    if request.get("chapter_titles") or request.get("fixed_outline") or request.get("modules"):
        raise Blocked("DEEPWRITE_NO_PRESET_OUTLINE_OR_MANUAL_MODULE_SELECTION")
    guide = request.get("author_guidance_source_index")
    if guide is not None and (type(guide) is not int or guide < 0 or guide >= len(request["source_files"])):
        raise Blocked("DEEPWRITE_AUTHOR_GUIDANCE_INDEX_INVALID")
    return mode


def source_bytes(request):
    items = []
    for i, value in enumerate(request["source_files"], 1):
        path = private_path(value)
        if not path.is_file() or path.stat().st_size > 15_000_000:
            raise Blocked("DEEPWRITE_UNAVAILABLE_OR_OVERSIZED_SOURCE")
        try:
            raw = path.read_bytes()
            raw.decode("utf-8")
        except UnicodeDecodeError as err:
            raise Blocked("DEEPWRITE_SOURCE_MUST_BE_UTF8_TEXT") from err
        if len(raw) < 24:
            raise Blocked("DEEPWRITE_SOURCE_TOO_SHORT_FOR_STUDY")
        items.append((f"sources/native_{i:03d}.md", raw))
    return items


def pins(project_id, commit: str, current: dict):
    for key in ("current_spec", "parent_spec"):
        if not isinstance(current.get(key), str):
            raise Blocked("DEEPWRITE_PROTOCOL_SPEC_REQUIRED")
    return {
        "project_id": project_id, "channel": effective_channel(),
        "protocols": {
            "deepwrite": {
                "version": current["formal_workbench_version"], "commit": commit,
                "spec_sha": git("rev-parse", commit + ":" + current["current_spec"])
            },
            "wish_delivery": {
                "version": current["parent_version"], "commit": commit,
                "spec_sha": git("rev-parse", commit + ":" + current["parent_spec"])
            }
        },
        "modules": [{"id": ident, "commit": commit}
                    for ident in ("e18_loop", "source_first_architecture")]
    }


def prepare(request_file: Path, private_root: Path, *, allow_fixture=False):
    """Create immutable input and two-stage config, never trust AI-made approval.

    Returns (project_root, discovery_evidence, base_config). Requires a NEW
    private project directory: failed jobs are never overwritten or auto-retried.
    """
    request_file, private_root = private_path(request_file), private_path(private_root)
    if not request_file.is_file():
        raise Blocked("DEEPWRITE_REQUEST_NOT_FOUND")
    raw_request = request_file.read_bytes()
    request = json.loads(raw_request)
    mode = validate_request(request)
    files = source_bytes(request)
    if private_root.exists():
        raise Blocked("DEEPWRITE_PROJECT_ALREADY_EXISTS_USE_RESUME_OR_NEW_ID")
    private_root.parent.mkdir(parents=True, exist_ok=True)
    project = private_root / "writer_project"
    evidence = private_root / "discovery_evidence"
    project.mkdir(parents=True)
    (project / "sources").mkdir()
    evidence.mkdir()
    (evidence / "USER_REQUEST.json").write_bytes(raw_request)
    commit = git("rev-parse", "HEAD")
    ident = official_identity()
    channel = effective_channel()
    rows = []
    for relative, raw in files:
        path = project / relative
        path.write_bytes(raw)
        rows.append({"path": relative, "sha256": sha(raw)})
    authorization = {
        "schema": "deepwrite/author-project-authorization/v1",
        "project_id": request["project_id"], "mode": mode,
        "chapter_scope": request["authorized_scope"],
        "author_identity_verification": "UNVERIFIED_EXTERNAL_REQUEST_FILE",
        "original_request_sha256": sha(raw_request),
        "model_generated": "UNKNOWN", "private_original_request_archived": "../discovery_evidence/USER_REQUEST.json",
        "model_may_create_drafts": True,
        "public_release_authorized": False
    }
    auth_raw = canonical(authorization)
    auth_path = "sources/author-contract.txt"
    (project / auth_path).write_bytes(auth_raw)
    rows.append({"path": auth_path, "sha256": sha(auth_raw)})
    base = {
        "project_id": request["project_id"],
        "run_id": "deepwrite-" + request["project_id"],
        "working_title": request["working_title"],
        "wish": request["wish"],
        "reader_goal": request["reader_goal"],
        "adapter": request["adapter"], "model": request["model"],
        "channel": channel,
        "guard": "on", "run_mode": "fresh",
        "token_budget": request["token_budget"],
        "discovery_token_budget": request["discovery_token_budget"],
        "discovery_output_cap": min(request["per_call_output_tokens"], request["discovery_token_budget"]),
        "per_call_output_tokens": request["per_call_output_tokens"],
        "max_revision_rounds": request["max_revision_rounds"],
        "min_chapters": request["min_chapters"], "max_chapters": request["max_chapters"],
        "insight_origin_scan": True,
        "modules": {"e18_loop": True, "source_first_architecture": True},
        "module_policy": {name: ("STABLE" if channel == "STABLE" else "CANDIDATE")
                          for name in ("e18_loop", "source_first_architecture")},
        "module_commits": {"e18_loop": commit, "source_first_architecture": commit},
        "pins": pins(request["project_id"], commit, ident),
        "sources": rows,
        "execution_contract": {
            "mode": mode, "authorization": {
                "path": auth_path, "sha256": sha(auth_raw),
                "provenance": "USER_REQUEST_EXPLICIT_SCOPE_SHA256:" + sha(raw_request)}
        }
    }
    if request.get("author_guidance_source_index") is not None:
        index = request["author_guidance_source_index"] + 1
        base["author_guidance"] = {
            "schema": "deepwrite/author-guided-frame/v0.1",
            "mode": "AUTHOR_GUIDED", "origin": "USER_SUPPLIED_PERSPECTIVE",
            "count_as_autonomous": False,
            "experiment_or_project_id": request["project_id"],
            "source_path": f"sources/native_{index:03d}.md"
        }
    (evidence / "base_config.json").write_bytes(canonical(base))
    (evidence / "START_STATE.json").write_bytes(canonical({
        "schema": "deepwrite/one-call-start/v1",
        "status": "SOURCE_BYTES_FROZEN_AUTHOR_SCOPE_UNVERIFIED_MODEL_NOT_RUN",
        "request_sha256": sha(raw_request), "code_commit": commit,
        "module_selection": "AUTOMATIC_ALL_APPLICABLE_GATES",
        "source_sha256": rows, "formal_version": ident["formal_workbench_version"],
        "formal_engine_active": ident["formal_engine_active"],
        "author_human_approval": "NOT_RUN", "next_step": "EXECUTE_SOURCE_DOMAIN_DISCOVERY"
    }))
    return project, evidence, base


def run_bounded_bookwide_topology_check(project, evidence, cfg, writer_result, model=None):
    """A genuine post-book call, not a free self-certification of topology quality.

    Revision preserves the original book and derives one new writer project.
    Author-gated sample mode never enters here.
    """
    topology = load("deepwrite_bookwide_topology_rethink",
                    DEEPWRITE / "candidates/source-first/bookwide_restructure.py")
    source_bytes = (project / "book.md").read_bytes()
    book = source_bytes.decode("utf-8")
    request = {
        "role": "bookwide_topology_recheck",
        "model_requested": cfg["model"],
        "payload": {
            "source_domain_study": (project / cfg["source_first_architecture"]["source_study"]["path"]).read_text(),
            "book_manuscript": book[:230000],
            "chapter_map": cfg["chapters"],
            "source_concepts": cfg["source_first_architecture"]["source_concepts"],
            "reader_contract": cfg["reader_prior_knowledge_contract"],
            "task": "Now that complete draft exists, independently consider if the book requires a different number or "
                    "order of chapters. Do NOT force changes; KEEP is valid. Return ONLY JSON "
                    "schema=deepwrite/bookwide-topology-audit/v1, decision KEEP/REPLAN, reason (20+ chars). "
                    "If REPLAN, include evidence_quote exact 15+ chars from book, chapters, old_to_new all chapters "
                    "with treatment, new reader_prior_knowledge_contract, and new book_design chapter_contributions "
                    "bound to original source_concept_ids. No author/human signoff claims."}
    }
    (evidence / "bookwide_topology.request.json").write_bytes(canonical(request))
    if model is None:
        writer = load("deepwrite_bookwide_model_factory", DEEPWRITE / "tools/writing_loop_experimental.py")
        model = (writer.CodexExec(cfg["model"], timeout=cfg.get("call_timeout", 600))
                 if cfg["adapter"] == "codex" else writer.transport.OpenAIResponses(cfg["model"]))
    try:
        result = model.generate("Use supplied verified materials only. No tools. Return exact JSON.",
                                json.dumps(request, ensure_ascii=False),
                                max_output_tokens=min(cfg["per_call_output_tokens"], 12000))
        identity = {"model": result.model, "response_id": result.response_id,
                    "provider_kind": result.provider_kind, "usage": result.usage,
                    "is_live": bool(getattr(model, "is_live", False)),
                    "response_sha256": sha(result.text.encode("utf-8")),
                    "author_acceptance": "NOT_RUN"}
        (evidence / "bookwide_topology.response.json").write_bytes(canonical({**identity, "text": result.text}))
        if not isinstance(result.usage,dict) or any(type(result.usage.get(k)) is not int
                for k in ("input_tokens", "output_tokens")):
            raise Blocked("BOOKWIDE_MODEL_USAGE_REQUIRED")
        proposal = json.loads(result.text)
        examined = topology.validate(proposal,cfg,book)
        if examined["decision"] == "KEEP":
            return {"status": "STRUCTURE_KEPT_MODEL_INTERNAL_ONLY",
                    "original_book_sha256": sha(source_bytes), **identity}
        rewritten_config = topology.derive_config(proposal,cfg)
        derived = project.parent / "writer_project_topology_r2"
        frozen = topology.make_private_derived_project(project,derived,cfg,rewritten_config)
        (evidence / "topology_r2_writer_config.json").write_bytes(canonical(rewritten_config))
        writer=load("deepwrite_bounded_rewrite", DEEPWRITE / "tools/writing_loop_experimental.py")
        retry=writer.WritingLoop(derived,rewritten_config,model=model).run()
        finish={"status":"REPLAN_DERIVATION_PENDING_HUMAN","derived_project":str(derived),
                "original_book_sha256":sha(source_bytes),"derived_writer_result":retry,
                "frozen_source_receipt":frozen,"model_review":identity,
                "original_book_preserved":True,"human_quality":"NOT_RUN"}
        if retry["status"] in ("CANDIDATE_PENDING_HUMAN","ENGINEERING_FIXTURE_ONLY_NOT_LIVE"):
            new_bytes=(derived / "book.md").read_bytes()
            finish["derived_book_sha256"]=sha(new_bytes)
            finish["content_size_ratio"]=round(len(new_bytes)/len(source_bytes),3)
            if len(new_bytes)<len(source_bytes)*.75:
                finish["status"]="REPLAN_CONTENT_LOSS_REQUIRES_INDEPENDENT_REVIEW"
        (evidence / "bookwide_topology_outcome.json").write_bytes(canonical(finish))
        return finish
    except Exception as error:
        blocked={"status":"BOOKWIDE_STRUCTURE_RECHECK_BLOCKED",
                 "reason":type(error).__name__ + ": " + str(error)[:180],
                 "original_book_sha256":sha(source_bytes),
                 "old_book_preserved":True,"next_step":"INSPECT_REVIEW_EVIDENCE_DO_NOT_PROMOTE_MODEL_JUDGMENT"}
        (evidence / "bookwide_topology_outcome.json").write_bytes(canonical(blocked))
        return blocked


def run(request_file: Path, private_root: Path, *, research_model=None, writer_model=None):
    """One invocation performs discovery and E18; no manual source module flags."""
    project, evidence, base = prepare(request_file, private_root)
    discovery = load("deepwrite_one_call_discovery", DEEPWRITE / "candidates/source-first/architecture_discovery.py")
    research_evidence = evidence / "research"
    try:
        preflight = discovery.discover(base, project, research_evidence, model=research_model)
    except Exception as error:
        return {"status": "BLOCKED_DISCOVERY", "evidence": str(research_evidence / "STATE.json"),
                "failure_code": type(error).__name__ + ": " + str(error)[:140],
                "private_project": str(project), "next_step": "INSPECT_FROZEN_DISCOVERY_FAILURE"}
    if not preflight["status"].startswith("ENGINEERING_STRUCTURE"):
        raise Blocked("DEEPWRITE_DISCOVERY_UNFINISHED")
    writer = load("deepwrite_one_call_writer", DEEPWRITE / "tools/writing_loop_experimental.py")
    final = json.loads((research_evidence / "writer_config.json").read_text("utf-8"))
    result = writer.WritingLoop(project, final, model=writer_model).run()
    replan = {"status": "NOT_RUN", "reason": "ASSISTED_AUTHOR_GATE_OR_WRITER_INCOMPLETE"}
    if (final["execution_contract"]["mode"] == "AUTONOMOUS_FULL_DRAFT" and
            result["status"] in ("CANDIDATE_PENDING_HUMAN", "ENGINEERING_FIXTURE_ONLY_NOT_LIVE")):
        replan = run_bounded_bookwide_topology_check(project, evidence, final, result,
                                                     research_model or writer_model)
    receipt = {
        "schema": "deepwrite/one-call-execution-receipt/v1",
        "status": result["status"], "project_id": final["project_id"],
        "source_study_sha256": preflight["study_sha256"],
        "chapter_count_proposed": preflight["chapter_count"],
        "chapter_count_author_approved": False,
        "module_selection": "AUTOMATIC",
        "bookwide_topology_recheck": replan,
        "writer_result": result, "author_acceptance": "NOT_RUN",
        "independent_reader_quality": "NOT_RUN",
        "real_model_verified": bool(result["status"] == "CANDIDATE_PENDING_HUMAN"),
        "default_formal_main_pointer_changed": False
    }
    (evidence / "RESULT.json").write_bytes(canonical(receipt))
    return receipt


def status(path: Path):
    path = private_path(path)
    identity = official_identity()
    evidence = path / "discovery_evidence"
    if not path.exists():
        return {"status": "PROJECT_NOT_FOUND", **identity}
    for name in ("RESULT.json", "research/STATE.json", "START_STATE.json"):
        file = evidence / name
        if file.is_file():
            value = json.loads(file.read_text("utf-8"))
            return {"project": str(path), "latest_checkpoint": str(file),
                    "project_status": value.get("status"), "formal": identity,
                    "author_acceptance": value.get("author_acceptance", "NOT_RUN")}
    return {"status": "NO_VERIFIED_PRIVATE_CHECKPOINT", **identity}


def resume(path: Path, expected_state_sha: str, author_approval_receipt=None, author_approval_sha256=None, *, writer_model=None):
    path = private_path(path)
    project = path / "writer_project"
    frozen = path / "discovery_evidence" / "research" / "writer_config.json"
    if not frozen.is_file():
        raise Blocked("DEEPWRITE_NO_FROZEN_DISCOVERY_CONFIG_TO_RESUME")
    writer = load("deepwrite_one_call_resume_writer", DEEPWRITE / "tools/writing_loop_experimental.py")
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_state_sha)):
        raise Blocked("DEEPWRITE_EXTERNAL_EXPECTED_STATE_SHA_REQUIRED")
    result = writer.WritingLoop(project, json.loads(frozen.read_text("utf-8")),
                                model=writer_model, expected_state_sha=expected_state_sha,
                                author_approval_receipt=author_approval_receipt,
                                expected_author_approval_sha=author_approval_sha256).run()
    (path / "discovery_evidence" / "RESUME_RESULT.json").write_bytes(canonical(result))
    return result


def main():
    parser = argparse.ArgumentParser(description="DeepWrite single command: research→plan→write→review→archive")
    sub = parser.add_subparsers(dest="cmd", required=True)
    go = sub.add_parser("run")
    go.add_argument("user_request", type=Path)
    go.add_argument("private_project_root", type=Path)
    st = sub.add_parser("status")
    st.add_argument("private_project_root", type=Path)
    rs = sub.add_parser("resume")
    rs.add_argument("private_project_root", type=Path)
    rs.add_argument("--expected-state-sha256", required=True)
    rs.add_argument("--author-approval-receipt", type=Path)
    rs.add_argument("--author-approval-sha256")
    args = parser.parse_args()
    try:
        if args.cmd == "run":
            result = run(args.user_request, args.private_project_root)
        elif args.cmd == "resume":
            result = resume(args.private_project_root, args.expected_state_sha256,
                            args.author_approval_receipt, args.author_approval_sha256)
        else:
            result = status(args.private_project_root)
    except Exception as error:
        result = {"status": "BLOCKED", "type": type(error).__name__, "reason": str(error)[:260],
                  "formal": official_identity()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("CANDIDATE_PENDING_HUMAN",
                                        "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", "AWAIT_AUTHOR_REVIEW") else 2


if __name__ == "__main__":
    sys.exit(main())
