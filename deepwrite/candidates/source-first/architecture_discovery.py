#!/usr/bin/env python3
"""Source-first TWO-PHASE DeepWrite candidate: study source before defining chapters.

Stage 1: call the chosen actual model to study frozen original materials and
compare source-domain directions. Stage 2: call it to propose (not authenticate)
book architecture and chapter count, then validate and freeze an E18 config.

This candidate is not a stable launcher. Its model judgments cannot certify
originality, source truth, author approval, reader experience, or book quality.
No live provider is accessed by tests or unless the CLI is actually invoked.
"""
from __future__ import annotations

from dataclasses import asdict
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
DEEPWRITE = HERE.parent.parent
CODE_ROOT = DEEPWRITE.parent
HEX = re.compile(r"[0-9a-f]{64}\Z")
CHAPTER = re.compile(r"[A-Za-z0-9_-]+\Z")


class Blocked(ValueError):
    """Fail closed, preserve the actual model evidence if already received."""


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def secure_path(root: Path, rel: str) -> Path:
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise Blocked("DISCOVERY_SOURCE_PATH_INVALID")
    pieces = Path(rel).parts
    if any(p in ("..", ".") for p in pieces) or not pieces or pieces[0] != "sources":
        raise Blocked("DISCOVERY_SOURCE_MUST_BE_PRIVATE_SOURCES_PATH")
    path = root.joinpath(*pieces)
    if not path.resolve().is_relative_to(root.resolve()):
        raise Blocked("DISCOVERY_SOURCE_SYMLINK_ESCAPE")
    return path


def text(value):
    return isinstance(value, str) and len(value.strip()) >= 8


def _parse_reply(result, stage: str, max_tokens: int, calls: list, out: Path):
    usage = result.usage
    if (not isinstance(usage, dict) or
            any(type(usage.get(k)) is not int or usage[k] < 0 for k in ("input_tokens", "output_tokens"))):
        raise Blocked("DISCOVERY_MODEL_TOKEN_USAGE_UNVERIFIED")
    cost = usage["input_tokens"] + usage["output_tokens"]
    if cost > max_tokens:
        raise Blocked("DISCOVERY_TOKEN_BUDGET_EXCEEDED")
    if (not isinstance(result.model, str) or not result.model or
            not isinstance(result.response_id, str) or not result.response_id):
        raise Blocked("DISCOVERY_PROVIDER_RESPONSE_IDENTITY_MISSING")
    if not isinstance(result.text, str):
        raise Blocked("DISCOVERY_MODEL_TEXT_MISSING")
    evidence = {"schema": "deepwrite/discovery-model-call/v1", "stage": stage,
                "model": result.model, "provider_kind": result.provider_kind,
                "response_id": result.response_id, "usage": usage,
                "response_sha256": digest(result.text.encode("utf-8")),
                "response": result.text,
                "author_acceptance": "NOT_RUN", "human_blind_evaluation": "NOT_RUN"}
    (out / (stage + ".response.json")).write_bytes(encoded(evidence))
    calls.append({"stage": stage, "model": result.model, "response_id": result.response_id,
                  "sha256": evidence["response_sha256"], "tokens": cost})
    try:
        data = json.loads(result.text)
    except json.JSONDecodeError as error:
        raise Blocked("DISCOVERY_MODEL_MUST_RETURN_EXACT_JSON") from error
    if not isinstance(data, dict):
        raise Blocked("DISCOVERY_MODEL_OBJECT_REQUIRED")
    return data, cost


def validate_intake(cfg: dict, project: Path, out: Path):
    if not isinstance(cfg, dict):
        raise Blocked("DISCOVERY_BASE_CONFIG_REQUIRED")
    if any(key in cfg for key in ("chapters", "source_first_architecture",
                                 "reader_prior_knowledge_contract", "replay_drafts", "known_findings")):
        raise Blocked("DISCOVERY_PRESET_CHAPTERS_OR_OUTLINE_FORBIDDEN")
    if cfg.get("channel") != "CANDIDATE_OPT_IN":
        raise Blocked("DISCOVERY_REQUIRES_EXPLICIT_CANDIDATE_OPT_IN")
    if cfg.get("run_mode", "fresh") != "fresh":
        raise Blocked("DISCOVERY_REPLAY_NOT_FRESH_DISCOVERY")
    if not text(cfg.get("wish")) or not text(cfg.get("working_title")):
        raise Blocked("DISCOVERY_WRITING_GOAL_REQUIRED")
    if cfg.get("adapter") not in ("responses", "codex", "fixture"):
        raise Blocked("DISCOVERY_ADAPTER_REQUIRED")
    if type(cfg.get("discovery_token_budget")) is not int or cfg["discovery_token_budget"] < 100:
        raise Blocked("DISCOVERY_EXPLICIT_BUDGET_REQUIRED")
    if type(cfg.get("discovery_output_cap")) is not int or cfg["discovery_output_cap"] < 100:
        raise Blocked("DISCOVERY_OUTPUT_CAP_REQUIRED")
    if (type(cfg.get("min_chapters")) is not int or type(cfg.get("max_chapters")) is not int or
            cfg["min_chapters"] < 1 or cfg["max_chapters"] < cfg["min_chapters"] or
            cfg["max_chapters"] > 40):
        raise Blocked("DISCOVERY_AUTHOR_LIMITS_REQUIRED")
    if not project.is_dir() or not (project / "sources").is_dir():
        raise Blocked("DISCOVERY_PRIVATE_PROJECT_SOURCES_REQUIRED")
    if project.resolve().is_relative_to(CODE_ROOT.resolve()) or out.resolve().is_relative_to(CODE_ROOT.resolve()):
        raise Blocked("DISCOVERY_PRIVATE_LOCATION_OUTSIDE_CODE_REPO_REQUIRED")
    if project.resolve() == out.resolve() or project.resolve().is_relative_to(out.resolve()) or out.resolve().is_relative_to(project.resolve()):
        raise Blocked("DISCOVERY_OUTPUT_MUST_BE_SEPARATE_FROM_WRITER_PROJECT")
    if out.exists() and any(out.iterdir()):
        raise Blocked("DISCOVERY_OUTPUT_NOT_EMPTY_OR_UNSAFE_RETRY")
    if any(p.name != "sources" for p in project.iterdir()):
        raise Blocked("DISCOVERY_WRITER_PROJECT_ALREADY_STARTED")
    if not cfg.get("modules", {}).get("source_first_architecture") or not cfg.get("modules", {}).get("e18_loop"):
        raise Blocked("DISCOVERY_SOURCE_FIRST_WRITER_MODULES_REQUIRED")
    if cfg.get("execution_contract", {}).get("mode") not in ("AUTONOMOUS_FULL_DRAFT", "ASSISTED_AUTHOR_GATED"):
        raise Blocked("DISCOVERY_AUTHOR_MODE_INVALID")
    source_rows = cfg.get("sources")
    if not isinstance(source_rows, list) or not source_rows:
        raise Blocked("DISCOVERY_FROZEN_SOURCES_REQUIRED")
    sources = {}
    for row in source_rows:
        if not isinstance(row, dict) or not HEX.fullmatch(str(row.get("sha256", ""))):
            raise Blocked("DISCOVERY_SOURCE_HASH_REQUIRED")
        name = row.get("path")
        path = secure_path(project, name)
        if name in sources or not path.is_file():
            raise Blocked("DISCOVERY_DUPLICATE_OR_UNREADABLE_SOURCE")
        data = path.read_bytes()
        if digest(data) != row["sha256"]:
            raise Blocked("DISCOVERY_SOURCE_SHA_MISMATCH")
        sources[name] = data
    authority = cfg["execution_contract"].get("authorization", {})
    if (authority.get("path") not in sources or
            sources[authority["path"]] is None or
            authority.get("sha256") != digest(sources[authority["path"]]) or
            not text(authority.get("provenance"))):
        raise Blocked("DISCOVERY_REAL_AUTHOR_SOURCE_REFERENCE_REQUIRED")
    auth = json.loads(sources[authority["path"]])
    mode = cfg["execution_contract"]["mode"]
    required_scope = ("ALL_CANDIDATE_CHAPTERS" if mode == "AUTONOMOUS_FULL_DRAFT"
                      else "FIRST_SAMPLE_AFTER_DISCOVERY")
    if (auth.get("schema") != "deepwrite/author-project-authorization/v1" or
            auth.get("project_id") != cfg.get("project_id") or
            auth.get("mode") != mode or
            auth.get("chapter_scope") != required_scope):
        raise Blocked("DISCOVERY_AUTHOR_PROJECT_SCOPE_INVALID")
    if cfg.get("adapter") == "fixture" and cfg.get("allow_fixture") is not True:
        raise Blocked("DISCOVERY_FIXTURE_NOT_AUTHORIZED")
    return sources, authority["path"]


def _study(data, sources, excluded):
    if not text(data.get("study_markdown")):
        raise Blocked("DISCOVERY_FULL_NATIVE_STUDY_REQUIRED")
    concepts, rivals = data.get("source_concepts"), data.get("rival_directions")
    if not isinstance(concepts, list) or not concepts:
        raise Blocked("DISCOVERY_SOURCE_CONCEPTS_REQUIRED")
    if not isinstance(rivals, list) or len(rivals) < 2:
        raise Blocked("DISCOVERY_SOURCE_RIVALS_REQUIRED")
    ids = set()
    for c in concepts:
        if not isinstance(c, dict) or not text(c.get("id")) or c["id"] in ids:
            raise Blocked("DISCOVERY_SOURCE_CONCEPT_ID_DUPLICATE")
        ids.add(c["id"])
        path = c.get("source_path")
        if path not in sources or path == excluded:
            raise Blocked("DISCOVERY_ORIGINAL_NOT_AUTHORIZATION_SOURCE_REQUIRED")
        try:
            decoded = sources[path].decode("utf-8")
        except UnicodeDecodeError as error:
            raise Blocked("DISCOVERY_ORIGINAL_NOT_UTF8") from error
        if not text(c.get("quote")) or c["quote"] not in decoded:
            raise Blocked("DISCOVERY_SOURCE_QUOTE_NOT_IN_BYTES")
        for key in ("causal_mechanism", "counterinterpretation", "transfer_limit"):
            if not text(c.get(key)):
                raise Blocked("DISCOVERY_SOURCE_MECHANISM_INCOMPLETE")
    rivals_ids = set()
    for d in rivals:
        if not isinstance(d, dict) or not text(d.get("id")) or d["id"] in rivals_ids:
            raise Blocked("DISCOVERY_RIVAL_DUPLICATE")
        rivals_ids.add(d["id"])
        for key in ("source_question", "reader_problem", "tradeoff"):
            if not text(d.get(key)):
                raise Blocked("DISCOVERY_RIVAL_UNSUPPORTED")
    return ids, rivals_ids


def _architecture(data, source_data, cfg, project, study_path, study_bytes):
    rows = data.get("chapters")
    if (not isinstance(rows, list) or not cfg["min_chapters"] <= len(rows) <= cfg["max_chapters"] or
            any(not isinstance(x, dict) or not CHAPTER.fullmatch(str(x.get("artifact_id", ""))) or
                not text(x.get("title")) for x in rows)):
        raise Blocked("DISCOVERY_CHAPTER_COUNT_OR_ID_NOT_JUSTIFIED")
    if len(set(row["artifact_id"] for row in rows)) != len(rows):
        raise Blocked("DISCOVERY_DUPLICATE_CHAPTERS")
    if data.get("selected_direction_id") not in {v["id"] for v in source_data["rival_directions"]}:
        raise Blocked("DISCOVERY_SELECTION_NOT_AMONG_STUDIED_RIVALS")
    if not text(data.get("why_selected_over_rivals")):
        raise Blocked("DISCOVERY_SELECTION_REASON_REQUIRED")
    book = data.get("book_design")
    if not isinstance(book, dict):
        raise Blocked("DISCOVERY_BOOK_DESIGN_REQUIRED")
    contract = data.get("reader_prior_knowledge_contract")
    reader_gate = module("deepwrite_discovery_reader_gate", DEEPWRITE / "candidates/e23-frame-wiring/reader_source_gate.py")
    if not isinstance(contract, dict) or contract.get("knowledge_compounding", {}).get("enabled") is not True:
        raise Blocked("DISCOVERY_COMPOUNDING_CONTRACT_REQUIRED")
    reader_gate.validate_contract(contract, rows)
    study = {"path": study_path, "sha256": digest(study_bytes)}
    arch = {"schema": "deepwrite/source-first-architecture/v1",
            "project_id": cfg["project_id"],
            "status": "PROVISIONAL_NOT_AUTHOR_APPROVED",
            "source_study": study,
            "source_concepts": source_data["source_concepts"],
            "rival_directions": source_data["rival_directions"],
            "selected_direction_id": data["selected_direction_id"],
            "why_selected_over_rivals": data["why_selected_over_rivals"],
            "book_design": {"status": "PROVISIONAL",
                            "why_these_chapters_not_source_outline": book.get("why_these_chapters_not_source_outline"),
                            "chapter_contributions": book.get("chapter_contributions")}}
    frozen = copy.deepcopy(cfg)
    for key in ("discovery_token_budget", "discovery_output_cap", "min_chapters", "max_chapters", "allow_fixture"):
        frozen.pop(key, None)
    frozen["chapters"] = rows
    if cfg["execution_contract"]["mode"] == "ASSISTED_AUTHOR_GATED":
        frozen["execution_contract"]["sample_chapters"] = [rows[0]["artifact_id"]]
        frozen["execution_contract"]["allowed_unapproved_candidate_chapters"] = []
    frozen["reader_prior_knowledge_contract"] = contract
    frozen["source_first_architecture"] = arch
    frozen["sources"].append(study)
    source_gate = module("deepwrite_discovery_source_gate", HERE / "source_first_gate.py")
    source_gate.validate(frozen, lambda rel: (study_bytes if rel == study_path else
                         secure_path(project, rel).read_bytes()))
    return frozen, arch


def discover(config: dict, project: Path, out: Path, model=None):
    project, out = Path(project).absolute(), Path(out).absolute()
    sources, authority = validate_intake(config, project, out)
    out.mkdir(parents=True, exist_ok=True)
    origin_receipt = {"status": "NOT_REQUESTED", "independent_novelty": "UNVERIFIED"}
    if config.get("author_guidance") is not None:
        gate = module("deepwrite_author_guidance", DEEPWRITE / "candidates/e23-frame-wiring/insight_origin_gate.py")
        origin_receipt = gate.check_author_guided_contract(config)
        origin_receipt["semantic_independence"] = "NOT_CLAIMED_USER_GUIDED"
    if model is None:
        writer = module("deepwrite_discovery_writer", DEEPWRITE / "tools/writing_loop_experimental.py")
        if config["adapter"] == "codex":
            model = writer.CodexExec(config["model"], timeout=config.get("call_timeout", 600))
        elif config["adapter"] == "responses":
            model = writer.transport.OpenAIResponses(config["model"])
        else:
            raise Blocked("DISCOVERY_FIXTURE_INJECTION_REQUIRED")
    calls = []
    tokens = 0
    def call(role, payload):
        nonlocal tokens
        if tokens >= config["discovery_token_budget"]:
            raise Blocked("DISCOVERY_TOKEN_BUDGET_EXHAUSTED")
        req = {"role": role, "payload": payload, "model_requested": config["model"]}
        (out / (role + ".request.json")).write_bytes(encoded(req))
        result = model.generate(
            "Read the frozen primary source as a source domain, not as a prewritten book outline. "
            "Use no tools. Return ONLY a JSON object. Do not claim author approval or human reading.",
            json.dumps(req, ensure_ascii=False), min(config["discovery_output_cap"],
                    config["discovery_token_budget"] - tokens))
        response, cost = _parse_reply(result, role, config["discovery_token_budget"]-tokens, calls, out)
        tokens += cost
        return response
    try:
        readable = {k: v.decode("utf-8") for k, v in sources.items() if k != authority}
        if not readable:
            raise Blocked("DISCOVERY_NO_NATIVE_SOURCE")
        first = call("source_domain_study", {
            "wish": config["wish"], "sources": readable,
            "origin_requirement": ("ALSO_PROPOSE_THREE_SOURCE_GROUNDED_RIVAL_DECISION_FRAMES_UNVERIFIED" if config.get("insight_origin_scan") else "SOURCE_FIRST_ONLY"),
            "task": "Independently study the source BEFORE proposing any chapters. Return JSON with "
                    "study_markdown (full native reasoning and contradictions), source_concepts "
                    "(id,source_path,quote exact verbatim,causal_mechanism,counterinterpretation,transfer_limit), "
                    "rival_directions (at least two objects: id,source_question,reader_problem,tradeoff). "
                    "If origin_requirement requests frames, ALSO include origin_status=MODEL_PROPOSAL_UNVERIFIED and "
                    "lenses (at least three): id,default_question,alternative_question,decision_before,decision_after,"
                    "source_falsifier,source_anchor:{path,quote}; each quote must appear in source bytes. "
                    "No chapter outline in this phase; do not borrow an older book's chapter map."})
        _study(first, sources, authority)
        if config.get("insight_origin_scan"):
            gate = module("deepwrite_source_question_origin", DEEPWRITE / "candidates/e23-frame-wiring/insight_origin_gate.py")
            scan = gate.inspect_proposals(first, readable)
            if scan["status"] != "PASS_STRUCTURAL_ORIGIN_FROZEN_SEMANTICS_UNVERIFIED":
                raise Blocked("DISCOVERY_ORIGIN_QUESTION_COMPETITION_INVALID: " + str(scan["errors"])[:140])
            origin_receipt = {**scan, "mode": ("AUTHOR_GUIDED" if config.get("author_guidance") else "SOURCE_FIRST_PROPOSAL_NOT_ATTESTED_BLIND"),
                              "true_blind_origin_claim": "NOT_VERIFIED", "human_quality": "NOT_RUN"}
            (out / "source_question_origination.json").write_bytes(encoded(origin_receipt))
        study_path = "sources/discovery_native_study.md"
        study_file = secure_path(project, study_path)
        if study_file.exists() or study_path in sources:
            raise Blocked("DISCOVERY_STUDY_DESTINATION_ALREADY_EXISTS")
        study_bytes = (first["study_markdown"].rstrip() + "\n").encode("utf-8")
        second = call("book_architecture_discovery", {
            "wish": config["wish"], "source_study": first["study_markdown"],
            "source_concepts": first["source_concepts"],
            "rival_directions": first["rival_directions"],
            "reader_goal": config.get("reader_goal", ""),
            "chapter_bounds": [config["min_chapters"], config["max_chapters"]],
            "task": "Only NOW derive a provisional chapter count/order from reader knowledge dependencies. "
                    "Return JSON chapters (artifact_id,title), selected_direction_id, "
                    "why_selected_over_rivals, book_design:{why_these_chapters_not_source_outline,"
                    "chapter_contributions:[{chapter_id,source_concept_ids,distinct_reader_change}]}, "
                    "reader_prior_knowledge_contract:{schema:'deepwrite/reader-prior-contract/v1',known,"
                    "unknown,concepts:[{id,first_explained_in,first_used_in,prerequisites}],"
                    "knowledge_compounding:{enabled:true,transfer_goal}}. "
                    "No forced one-to-one mapping of course lessons to book chapters; all author claims provisional."})
        frozen, arch = _architecture(second, first, config, project, study_path, study_bytes)
        study_file.write_bytes(study_bytes)
        (out / "architecture.json").write_bytes(encoded(arch))
        (out / "writer_config.json").write_bytes(encoded(frozen))
        manifest = {"schema": "deepwrite/two-phase-source-discovery-receipt/v1",
                    "status": "ENGINEERING_STRUCTURE_FROZEN_QUALITY_UNVERIFIED",
                    "stage_order": ["source_domain_study", "book_architecture_discovery"],
                    "project_id": config["project_id"], "model_calls": calls,
                    "tokens": tokens, "chapter_count": len(frozen["chapters"]),
                    "chapters": [row["artifact_id"] for row in frozen["chapters"]],
                    "study_sha256": digest(study_bytes),
                    "writer_config_sha256": digest((out / "writer_config.json").read_bytes()),
                    "author_acceptance": "NOT_RUN", "human_blind_evaluation": "NOT_RUN",
                    "source_correctness": "MODEL_REVIEW_NOT_INDEPENDENTLY_VALIDATED",
                    "insight_origin_provenance": origin_receipt,
                    "live_provider_verified": bool(getattr(model, "is_live", False)),
                    "actual_writer_run": "NOT_RUN",
                    "next_step": "Invoke E18 writer with exact writer_config.json and private project root; preserve hashes."}
        (out / "STATE.json").write_bytes(encoded(manifest))
        return manifest
    except Exception as error:
        (out / "STATE.json").write_bytes(encoded({
            "schema": "deepwrite/two-phase-source-discovery-receipt/v1",
            "status": "BLOCKED", "error_type": type(error).__name__,
            "message": str(error)[:180], "model_calls": calls, "tokens": tokens,
            "original_source_files_modified": False,
            "author_acceptance": "NOT_RUN", "writer_started": False,
            "next_step": "Resolve exact gate; archive failed evidence; never retry ambiguously over same output."}))
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("base_config", type=Path)
    p.add_argument("private_writer_project", type=Path)
    p.add_argument("private_discovery_evidence", type=Path)
    args = p.parse_args()
    try:
        base = json.loads(args.base_config.read_text(encoding="utf-8"))
        result = discover(base, args.private_writer_project, args.private_discovery_evidence)
    except Exception as error:
        result = {"status": "BLOCKED", "error_type": type(error).__name__,
                  "message": str(error)[:180]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"].startswith("ENGINEERING_STRUCTURE") else 2


if __name__ == "__main__":
    sys.exit(main())
