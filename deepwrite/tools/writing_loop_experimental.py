#!/usr/bin/env python3
"""Experimental writing orchestrator. Candidate delivery is never human acceptance.

Uses the existing transport, E15 closeout checker, PR12 verified assembler and
checkpoint/resume tools. All writing is private caller-owned output. CURRENT and
the collaboration bridge are never written. A scripted transport is test-only.
"""
from __future__ import annotations
import argparse
import copy
from dataclasses import asdict
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

DEEPWRITE = Path(__file__).resolve().parents[1]
FRONT_PART = "__front_matter__"
TAIL_PART = "__afterword__"
NON_CHAPTER_PARTS = {FRONT_PART, TAIL_PART}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    exec(compile(Path(path).read_bytes(), str(path), "exec"), obj.__dict__)
    return obj


transport = module("e18_responses", DEEPWRITE / "tools/model_adapter_openai_responses_experimental_v0_1.py")
checkpoint = module("e18_checkpoint", DEEPWRITE / "qa/checkpoint.py")
sys.path.insert(0, str(DEEPWRITE / "qa"))
resume_checker = module("e18_resume", DEEPWRITE / "qa/resume_check.py")
packager = module("e18_packager", DEEPWRITE / "tools/book_packager_v0.1.py")


class Blocked(Exception):
    pass


class Paused(Exception):
    pass


class AuthorReviewRequired(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def substantive_text(text):
    return "".join(c.casefold() for c in text if c.isalnum() or c in "+-=<>/%")


def json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def parse_object(text):
    text = text.strip()
    if text.startswith("\x60\x60\x60"):
        text = re.sub(r"^\x60\x60\x60(?:json)?\s*", "", text, count=1)
        text = re.sub(r"\s*\x60\x60\x60$", "", text, count=1)
    value = json.loads(text)
    if not isinstance(value, dict):
        raise Blocked("MODEL_RESPONSE_NOT_OBJECT")
    return value


def redact(text):
    text = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", text, flags=re.I)
    return re.sub(r"sk-[A-Za-z0-9_-]+", "[REDACTED_KEY]", text)


class CodexExec:
    """One fresh CLI turn; actual usage, not a hard provider-side token limit.

    Empty workdir and rejected tool events are observable safeguards, not proof
    of OS filesystem isolation. Rigorous B0/B1 fairness remains UNVERIFIED.
    """
    is_live = True
    output_limit_enforced = False

    def __init__(self, model, timeout=600, binary="codex"):
        if not model:
            raise Blocked("EXPLICIT_MODEL_REQUIRED")
        self.model, self.timeout, self.binary = model, timeout, binary
        self.events_parser = module("e18_codex_events", DEEPWRITE / "discovery-gate/execute_codex_cli.py")
        self.last_transport = {}

    def generate(self, instructions, prompt, max_output_tokens=6000):
        self.last_transport = {}
        with tempfile.TemporaryDirectory(prefix="e18-codex-") as work:
            last = Path(work) / "last.txt"
            cmd = [self.binary, "exec", "--json", "--ephemeral", "--ignore-user-config",
                   "--sandbox", "read-only", "--skip-git-repo-check", "--cd", work,
                   "--model", self.model, "--output-last-message", str(last), "-"]
            proc = subprocess.run(cmd, input=instructions + "\n\n" + prompt,
                                  text=True, capture_output=True, timeout=self.timeout)
            self.last_transport = {"events": redact(proc.stdout), "stderr": redact(proc.stderr),
                                   "returncode": proc.returncode,
                                   "output_limit": "POSTHOC_ONLY", "requested_output_cap": max_output_tokens,
                                   "model_identity_basis": "CLI_REQUEST_FLAG_NOT_SERVER_ATTESTATION"}
            if proc.returncode:
                raise Blocked("BLOCKED_CODEX_AUTH_OR_TRANSPORT")
            parsed = self.events_parser.parse_events(proc.stdout)
            self.last_transport["codex_tool_event_types"] = parsed["tool_event_types"]
            self.last_transport["event_count"] = parsed["event_count"]
            text = last.read_text(encoding="utf-8").strip()
            if not text:
                raise Blocked("EMPTY_MODEL_OUTPUT")
            usage = parsed["usage"]
            return transport.ModelResult(parsed["thread_id"], self.model, text, usage, "codex_cli_live")


class WritingLoop:
    def __init__(self, root, config, model=None, expected_state_sha=None, stop_after=None,
                 author_approval_receipt=None, expected_author_approval_sha=None):
        candidate_root = Path(root).absolute()
        try:
            checkpoint.no_symlinks(candidate_root)
        except ValueError as error:
            raise Blocked("SYMLINK_PROJECT_ROOT_OR_ANCESTOR") from error
        self.root = candidate_root.resolve()
        if self.root.is_relative_to(DEEPWRITE.parent.resolve()):
            raise Blocked("PROJECT_OUTPUT_MUST_BE_OUTSIDE_CODE_REPOSITORY")
        self.root.mkdir(parents=True, exist_ok=True)
        self.config = copy.deepcopy(config)
        self.cfg_sha = digest(json_bytes(config))
        self.stop_after, self.steps_this_turn = stop_after, 0
        self.guard = module("e18_closeout", DEEPWRITE / "candidates/e15-review-closure/review_closure_guard.py")
        self.reader_guard = module("e18_reader_source", DEEPWRITE / "candidates/e23-frame-wiring/reader_source_gate.py")
        self.source_first_guard = (module("e18_source_first", DEEPWRITE / "candidates/source-first/source_first_gate.py")
                                   if config.get("modules", {}).get("source_first_architecture") else None)
        self.source_first_receipt = None
        self._validate_config()
        self.author_receipt = None
        if author_approval_receipt is not None:
            external = checkpoint.no_symlinks(Path(author_approval_receipt).absolute()).resolve()
            if external.is_relative_to(self.root):
                raise Blocked("AUTHOR_APPROVAL_MUST_BE_EXTERNAL_TO_MODEL_PROJECT")
            raw = external.read_bytes()
            if not expected_author_approval_sha or digest(raw) != expected_author_approval_sha:
                raise Blocked("EXTERNAL_AUTHOR_APPROVAL_SHA_MISMATCH")
            self.author_receipt = (raw, json.loads(raw))
        state_path = self.root / "run_state.json"
        if state_path.exists():
            raw = state_path.read_bytes()
            if not expected_state_sha or digest(raw) != expected_state_sha:
                raise Blocked("EXTERNAL_STATE_SHA_REQUIRED_OR_MISMATCH")
            self.state = json.loads(raw)
            if self.state["config_sha256"] != self.cfg_sha:
                raise Blocked("FROZEN_CONFIG_MISMATCH")
            self.verify_files()
            if (self.state.get("execution_contract_sha256") != self.contract_sha or
                    self.state.get("reader_contract_sha256") != self.reader_contract_sha or
                    self.state.get("execution_mode") != config["execution_contract"]["mode"]):
                raise Blocked("RESUME_LOST_FROZEN_QUALITY_CONTRACT")
        else:
            if any(self.root.iterdir()) and not all(p.name == "sources" for p in self.root.iterdir()):
                raise Blocked("NEW_PROJECT_OUTPUT_NOT_EMPTY")
            self.state = {"schema": "deepwrite/writing-loop-state/v0", "config_sha256": self.cfg_sha,
                          "status": "STARTED", "files": {}, "completed": {}, "calls": {}, "call_completions": {},
                          "tokens": 0, "usage_uncertain_calls": [], "model_reported": None, "quality": "UNVERIFIED",
                          "run_mode": config.get("run_mode", "fresh"),
                          "draft_origin": ("FROZEN_BASELINE_REPLAY_NOT_FRESH_B0_B1" if config.get("run_mode") == "replay_frozen_drafts" else "MODEL_DRAFTED"),
                          "human_acceptance": "NOT_RUN", "fair_B0_B1": "UNVERIFIED",
                          "execution_mode": config["execution_contract"]["mode"],
                          "execution_contract_sha256": self.contract_sha,
                          "reader_contract_sha256": self.reader_contract_sha,
                          "source_first_intake": self.source_first_receipt or {"status": "NOT_REQUESTED"},
                          "run_id": config["run_id"], "gate_events": [],
                          "acceptance": {"ENGINEERING_VERIFIED": "NOT_RUN", "RUNNER_ACTIVE_VERIFIED": "CANDIDATE_ONLY",
                            "MODEL_INTERNAL_QUALITY_REVIEW": "NOT_RUN", "AUTHOR_ACCEPTANCE": "NOT_RUN",
                            "HUMAN_BLIND_EVALUATION": "NOT_RUN", "PUBLISHED": "NOT_AUTHORIZED"}}
            self.write("config.json", json_bytes(config))
            self.write("pins.json", json_bytes(config["pins"]))
            for item in config["sources"]:
                p = self.path(item["path"])
                raw = p.read_bytes()
                if digest(raw) != item["sha256"]:
                    raise Blocked("SOURCE_SHA_MISMATCH")
                self.track(item["path"])
            self.save_state()
        if model is None:
            if config["adapter"] == "responses":
                model = transport.OpenAIResponses(config["model"])
                model.is_live, model.output_limit_enforced = True, True
            elif config["adapter"] == "codex":
                model = CodexExec(config["model"], timeout=config.get("call_timeout", 600))
            else:
                raise Blocked("TEST_TRANSPORT_REQUIRES_EXPLICIT_INJECTION")
        self.model = model
        modules = self.module_receipt()
        if "module_receipt" in self.state:
            previous = self.state["module_receipt"]
            old_bytes = {k: (v.get("path"), v.get("sha256")) for k,v in previous["actually_loaded"].items()}
            new_bytes = {k: (v.get("path"), v.get("sha256")) for k,v in modules["actually_loaded"].items()}
            if previous["requested"] != modules["requested"] or old_bytes != new_bytes:
                raise Blocked("RESUME_LOADED_MODULE_IDENTITY_CHANGED")
        else:
            self.state["module_receipt"] = modules
        self.state["source_manifest_sha256"] = digest(json_bytes(config["sources"]))
        if "protocol_specs" not in self.state:
            current = json.loads((DEEPWRITE / "CURRENT.json").read_text())
            parent = json.loads((DEEPWRITE.parent / "wish-delivery/CURRENT.json").read_text())
            self.state["protocol_specs"] = {"deepwrite": {"version": current["active_workbench_version"],
                "sha256": digest((DEEPWRITE.parent / current["active_workbench_spec"]).read_bytes())},
                "wish_delivery": {"version": parent["active_version"],
                "sha256": digest((DEEPWRITE.parent / parent["active_spec"]).read_bytes())}}
        self.save_state()
        if bool(getattr(model, "is_live", False)) and config["guard"] != "on":
            raise Blocked("LIVE_WRITING_CANNOT_BYPASS_MANDATORY_CLOSEOUT")

    def _validate_config(self):
        c = self.config
        for key in ("project_id", "model", "working_title"):
            if not isinstance(c.get(key), str) or not c[key].strip():
                raise Blocked("CONFIG_REQUIRED_" + key)
        if c.get("guard") not in ("on", "off") or c.get("adapter") not in ("responses", "codex", "fixture"):
            raise Blocked("CONFIG_GUARD_OR_ADAPTER")
        for key in ("token_budget", "per_call_output_tokens", "max_revision_rounds"):
            if type(c.get(key)) is not int or c[key] < 1:
                raise Blocked("CONFIG_POSITIVE_INTEGER_" + key)
        rows = c.get("chapters")
        if not isinstance(rows, list) or not rows:
            raise Blocked("CHAPTERS_REQUIRED")
        ids = [x.get("artifact_id") for x in rows]
        if any(not isinstance(x, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", x) for x in ids) or len(ids) != len(set(ids)):
            raise Blocked("UNSAFE_OR_DUPLICATE_CHAPTER_ID")
        if set(ids) & NON_CHAPTER_PARTS:
            raise Blocked("CHAPTER_ID_COLLIDES_WITH_BOOK_PART")
        if c["guard"] != "on" and (c["adapter"] != "fixture" or c.get("channel") == "STABLE"):
            raise Blocked("REAL_WRITING_CANNOT_BYPASS_MANDATORY_CLOSEOUT")
        if not isinstance(c.get("sources"), list) or not c["sources"]:
            raise Blocked("FROZEN_SOURCES_REQUIRED")
        mode = c.get("run_mode", "fresh")
        if mode not in ("fresh", "replay_frozen_drafts"):
            raise Blocked("UNKNOWN_RUN_MODE")
        if mode == "fresh" and (c.get("replay_drafts") or c.get("known_findings")):
            raise Blocked("REPLAY_INPUT_FORBIDDEN_FRESH_EXPERIMENT")
        if mode == "replay_frozen_drafts":
            seeds = c.get("replay_drafts")
            if not isinstance(seeds, dict) or set(seeds) != set(ids):
                raise Blocked("REPLAY_NEEDS_EXACT_FROZEN_CHAPTER_INVENTORY")
            frozen_paths = {s["path"] for s in c["sources"]}
            if any(path not in frozen_paths for path in seeds.values()):
                raise Blocked("REPLAY_DRAFT_MUST_BE_HASH_PINNED_SOURCE")
            if not isinstance(c.get("known_findings", []), list):
                raise Blocked("KNOWN_FINDINGS_MUST_BE_FROZEN_LIST")
        if c.get("channel") not in ("CANDIDATE_OPT_IN", "SHADOW", "STABLE"):
            raise Blocked("EXPERIMENTAL_RUNNER_REQUIRES_CANDIDATE_CHANNEL")
        if c["channel"] == "STABLE":
            self.assert_stable_entry()
        supported = {"e18_loop", "reader_source_transfer", "e23_frame", "e23_perspective", "e23",
                     "source_first_architecture"}
        if c.get("modules", {}).get("source_first_architecture") and c["channel"] == "STABLE":
            raise Blocked("SOURCE_FIRST_CANDIDATE_NOT_AUTHORIZED_FOR_STABLE")
        if any(value and name not in supported for name, value in c.get("modules", {}).items()):
            raise Blocked("BLOCKED_UNSUPPORTED_MODULE")
        checkpoint.validate_pins(json_bytes(c["pins"]), c["project_id"])
        if not isinstance(c.get("run_id"), str) or not re.fullmatch(r"[A-Za-z0-9_-]+", c["run_id"]):
            raise Blocked("EXPLICIT_RUN_ID_REQUIRED")
        contract = c.get("execution_contract", {})
        if contract.get("mode") not in ("ASSISTED_AUTHOR_GATED", "AUTONOMOUS_FULL_DRAFT"):
            raise Blocked("FROZEN_AUTHOR_EXECUTION_MODE_REQUIRED")
        source_map = {s["path"]: s["sha256"] for s in c["sources"]}
        references = [contract.get("authorization", {})]
        if contract["mode"] == "ASSISTED_AUTHOR_GATED":
            samples = contract.get("sample_chapters")
            if not isinstance(samples, list) or not samples or not set(samples) <= set(ids):
                raise Blocked("ASSISTED_SAMPLE_SCOPE_REQUIRED")
            extra = contract.get("allowed_unapproved_candidate_chapters", [])
            if not isinstance(extra, list) or len(set(extra)) != len(extra) or not set(extra) <= set(ids):
                raise Blocked("AUTHOR_SCOPE_EXCEPTION_INVALID")
            if extra:
                references.append(contract.get("scope_authorization", {}))
        for ref in references:
            if (not isinstance(ref, dict) or ref.get("path") not in source_map or
                    ref.get("sha256") != source_map[ref["path"]] or not ref.get("provenance")):
                raise Blocked("AUTHOR_SCOPE_REQUIRES_ACTUAL_HASH_PINNED_SOURCE_REFERENCE")
            authority_raw = self.path(ref["path"]).read_bytes()
            if digest(authority_raw) != ref["sha256"]:
                raise Blocked("AUTHOR_AUTHORIZATION_SOURCE_BYTES_MISMATCH")
            authority = json.loads(authority_raw)
            if (authority.get("schema") != "deepwrite/author-project-authorization/v1" or
                    authority.get("project_id") != c["project_id"] or authority.get("mode") != contract["mode"]):
                raise Blocked("AUTHOR_AUTHORIZATION_PROJECT_OR_MODE_MISMATCH")
            scope = authority.get("chapter_scope")
            if contract["mode"] == "AUTONOMOUS_FULL_DRAFT":
                if scope != "ALL_CANDIDATE_CHAPTERS":
                    raise Blocked("AUTONOMOUS_PROJECT_AUTHORIZATION_SCOPE_REQUIRED")
            elif not isinstance(scope, list) or not set(scope) <= set(ids):
                raise Blocked("ASSISTED_PROJECT_AUTHORIZATION_SCOPE_INVALID")
            expected_scope = (set(contract["sample_chapters"]) if ref is references[0] else
                              set(contract.get("allowed_unapproved_candidate_chapters", []))) if contract["mode"] == "ASSISTED_AUTHOR_GATED" else set()
            if contract["mode"] == "ASSISTED_AUTHOR_GATED" and not expected_scope <= set(scope):
                raise Blocked("AUTHOR_SCOPE_EXCEPTION_NOT_ACTUALLY_AUTHORIZED")
        self.contract_sha = digest(json_bytes(contract))
        self.reader_guard.validate_contract(c.get("reader_prior_knowledge_contract"), c["chapters"])
        self.reader_contract_sha = digest(json_bytes(c["reader_prior_knowledge_contract"]))
        if self.source_first_guard is not None:
            try:
                self.source_first_receipt = self.source_first_guard.validate(
                    c, lambda relative: self.path(relative).read_bytes())
            except (ValueError, KeyError, TypeError, OSError, UnicodeError) as error:
                raise Blocked("SOURCE_FIRST_ARCHITECTURE_BLOCKED: " + str(error)) from error

    def assert_stable_entry(self):
        resolver = module("e18_formal_activation", DEEPWRITE / "release/activation.py")
        resolved = resolver.resolve(DEEPWRITE.parent)
        if (resolved.get("status") != "ACTIVE_ENGINE_IDENTITY_VERIFIED_QUALITY_NOT_IMPLIED" or
                resolved.get("runner") != "deepwrite/tools/writing_loop_experimental.py" or
                self.config.get("guard") != "on"):
            raise Blocked("STABLE_WRITER_NOT_FORMALLY_SELECTED_BY_CURRENT")
        record = json.loads((DEEPWRITE.parent / resolved["release_record"]).read_text())
        profile = record.get("execution_profile", {})
        gates = {"AUTHOR_PROJECT_MODE", "READER_SOURCE_TRANSFER", "ACTUAL_FILE_CLOSEOUT", "BOOKWIDE_RECHECK"}
        required = {"deepwrite/tools/writing_loop_experimental.py",
                    "deepwrite/tools/model_adapter_openai_responses_experimental_v0_1.py",
                    "deepwrite/qa/checkpoint.py", "deepwrite/qa/resume_check.py",
                    "deepwrite/tools/book_packager_v0.1.py",
                    "deepwrite/candidates/e15-review-closure/review_closure_guard.py",
                    "deepwrite/candidates/e23-frame-wiring/reader_source_gate.py",
                    "deepwrite/candidates/RESEARCH_LOOP.md", "deepwrite/candidates/EDITORIAL_LOOP.md"}
        if profile.get("kind") != "WRITING" or not gates <= set(profile.get("mandatory_gates", [])) or not required <= set(resolved["runtime_files"]):
            raise Blocked("STABLE_WRITER_RELEASE_PROFILE_OR_DEPENDENCY_INVENTORY_INCOMPLETE")
        if (self.config["pins"]["protocols"]["deepwrite"]["version"] != resolved["active_version"] or
                self.config["pins"]["protocols"]["wish_delivery"]["version"] != resolved["parent_wish_version"]):
            raise Blocked("STABLE_WRITER_PROJECT_PROTOCOL_PIN_MISMATCH")
        # A version label is not a protocol identity. Check the declared source
        # commit and Git blob against the same actual spec used by activation.
        parent_current = json.loads((DEEPWRITE.parent / "wish-delivery/CURRENT.json").read_text())
        protocol_paths = {"deepwrite": ("deepwrite/CURRENT.json", "active_workbench_version", "active_workbench_spec"),
                          "wish_delivery": ("wish-delivery/CURRENT.json", "active_version", "active_spec")}
        for name, (pointer, version_key, spec_key) in protocol_paths.items():
            pin = self.config["pins"]["protocols"][name]
            commit = pin.get("commit")
            if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
                raise Blocked("STABLE_WRITER_PROTOCOL_COMMIT_REQUIRED")
            expected_spec = resolved["active_spec"] if name == "deepwrite" else parent_current["active_spec"]
            try:
                if resolver.git(DEEPWRITE.parent, "cat-file", "-t", commit).strip() != b"commit":
                    raise ValueError("not a commit")
                resolver.git(DEEPWRITE.parent, "merge-base", "--is-ancestor", commit, "HEAD")
                pinned_pointer = json.loads(resolver.git(DEEPWRITE.parent, "show", commit + ":" + pointer))
                blob = resolver.git(DEEPWRITE.parent, "rev-parse", commit + ":" + expected_spec).decode().strip()
                if (pin.get("spec_sha") != blob or pinned_pointer.get(version_key) != pin["version"] or
                        pinned_pointer.get(spec_key) != expected_spec or
                        resolver.git(DEEPWRITE.parent, "show", commit + ":" + expected_spec) !=
                        (DEEPWRITE.parent / expected_spec).read_bytes()):
                    raise ValueError("protocol source does not match the activated spec")
            except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
                raise Blocked("STABLE_WRITER_PROTOCOL_GIT_IDENTITY_MISMATCH_" + name) from error

    def file_identity(self, relative):
        path = DEEPWRITE / relative
        raw = path.read_bytes()
        try:
            head = subprocess.check_output(["git", "-C", str(DEEPWRITE.parent), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
            pinned = subprocess.check_output(["git", "-C", str(DEEPWRITE.parent), "show", head + ":deepwrite/" + relative], stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError):
            head, pinned = None, None
        return {"path": "deepwrite/" + relative, "sha256": digest(raw),
                "implementation_commit": head if pinned == raw else None,
                "repository_head": head, "source_identity": "COMMITTED_BYTES" if pinned == raw else "WORKTREE_BYTES_NOT_COMMIT_ATTESTED"}

    def module_receipt(self):
        requested = {name: value for name, value in self.config.get("modules", {}).items() if value}
        loaded = {"e18_loop": self.file_identity("tools/writing_loop_experimental.py"),
                  "reader_source_transfer": self.file_identity("candidates/e23-frame-wiring/reader_source_gate.py"),
                  "actual_file_closeout": self.file_identity("candidates/e15-review-closure/review_closure_guard.py")}
        if requested.get("source_first_architecture"):
            loaded["source_first_architecture"] = self.file_identity("candidates/source-first/source_first_gate.py")
        if any(requested.get(name) for name in ("e23", "e23_frame", "e23_perspective")):
            receipt = self.config.get("e23_preprocess_receipt", {})
            expected = {"sources/e23_frame_manifest.json": receipt.get("frame_manifest_sha256"),
                        "sources/e23_frame_selection.json": receipt.get("selection_sha256"),
                        "sources/e23_frame_context.md": receipt.get("context_sha256")}
            if receipt.get("schema") != "deepwrite/e23-preprocess-receipt/v1" or any(
                    not sha or digest(self.path(path).read_bytes()) != sha for path, sha in expected.items()):
                raise Blocked("E23_REQUESTED_BUT_PREPROCESS_IDENTITY_NOT_VERIFIED")
            external = {"status": "PREPROCESS_RECEIPT_BYTES_VERIFIED", "receipt": receipt,
                        "invocation_authenticated": False, "current_run_invocation": "NOT_CALLED",
                        "requested_module_state": "NOT_LOADED_IN_THIS_RUN", "semantic_quality": "UNVERIFIED"}
        return {"requested": requested, "actually_loaded": loaded,
                "external_preprocessing": locals().get("external"),
                "formal_activation": "NOT_INFERRED_FROM_MODULE_FLAGS"}

    def path(self, relative):
        p = checkpoint.no_symlinks(self.root / checkpoint.relative_path(relative))
        try:
            p.relative_to(self.root)
        except ValueError:
            raise Blocked("PATH_OUTSIDE_PROJECT")
        return p

    def track(self, relative):
        p = self.path(relative)
        self.state["files"][relative] = digest(p.read_bytes())

    def write(self, relative, data):
        p = self.path(relative)
        p.parent.mkdir(parents=True, exist_ok=True)
        raw = data if isinstance(data, bytes) else data.encode("utf-8")
        if p.exists() and p.read_bytes() != raw:
            raise Blocked("IMMUTABLE_OUTPUT_COLLISION_" + relative)
        p.write_bytes(raw)
        self.state["files"][relative] = digest(raw)

    def verify_files(self):
        for relative, sha in self.state["files"].items():
            if digest(self.path(relative).read_bytes()) != sha:
                raise Blocked("RESUME_FILE_SHA_MISMATCH_" + relative)

    def save_state(self):
        raw = json_bytes(self.state)
        target = self.root / "run_state.json"
        temp = self.root / ".run_state.tmp"
        temp.write_bytes(raw)
        os.replace(temp, target)

    def event(self, phase, scope, status, evidence=None):
        self.state["gate_events"].append({"sequence": len(self.state["gate_events"]) + 1,
            "phase": phase, "scope": scope, "status": status,
            "evidence": evidence or {}, "accounted_tokens": self.state["tokens"]})
        self.save_state()

    def author_scope(self, current, next_chapter=None):
        contract = self.config["execution_contract"]
        if contract["mode"] == "AUTONOMOUS_FULL_DRAFT":
            return
        permitted = set(contract["sample_chapters"]) | set(contract.get("allowed_unapproved_candidate_chapters", []))
        if next_chapter in permitted:
            return
        valid = False
        if self.author_receipt is not None:
            raw, receipt = self.author_receipt
            approved = receipt.get("approved_artifacts", {})
            verification = receipt.get("verification", {})
            valid = (receipt.get("schema") == "deepwrite/external-author-sample-approval/v1" and
                receipt.get("project_id") == self.config["project_id"] and
                receipt.get("execution_contract_sha256") == self.contract_sha and
                receipt.get("status") == "APPROVED" and
                verification.get("method") == "EXTERNAL_OPERATOR_ATTESTATION" and
                bool(verification.get("evidence_reference")) and
                verification.get("model_generated") is False and
                all(art in current and approved.get(art) == digest(self.path(current[art]).read_bytes())
                    for art in contract["sample_chapters"]))
            if valid:
                relative = "author_receipts/" + digest(raw) + ".json"
                self.write(relative, raw)
                self.state["author_identity_verification"] = "EXTERNAL_OPERATOR_ATTESTATION_NOT_AUTHENTICATED_BY_RUNNER"
                self.event("AUTHOR_SAMPLE_REVIEW", next_chapter or "BOOK", "EXTERNAL_APPROVAL_REFERENCE_ACCEPTED",
                           {"receipt": relative, "whole_book_acceptance": "NOT_RUN"})
        if not valid:
            self.event("AUTHOR_SAMPLE_REVIEW", next_chapter or "BOOK", "AWAIT_AUTHOR_REVIEW",
                       {"sample_artifacts": {a: digest(self.path(p).read_bytes()) for a, p in current.items()},
                        "next_chapter": next_chapter, "scope_is_not_full_book_authorization": True})
            raise AuthorReviewRequired("AWAIT_AUTHOR_REVIEW_FROZEN_PROJECT_CONTRACT")

    def reader_review(self, key, art, relative, stage, sources=None):
        text = self.path(relative).read_text(encoding="utf-8")
        contract = self.config["reader_prior_knowledge_contract"]
        payload = {"chapter_id": art, "stage": stage, "manuscript": text,
                   "artifact_sha256": digest(self.path(relative).read_bytes()),
                   "contract_sha256": self.reader_contract_sha, "reader_contract": contract,
                   "task": self.reader_guard.review_instructions(contract, art, stage)}
        if sources is not None:
            payload["source_texts"] = sources
        data = self.call(key, "source_evidence_review" if stage == "SOURCE_LEARNING" else "reader_source_review", payload)
        review = parse_object(data["text"])
        review["reviewer"] = data["provider_kind"] + ":" + data["model"] + ":" + data["response_id"]
        result = self.reader_guard.evaluate(contract, art, text, review, stage=stage, source_texts=sources)
        path = "reader_reviews/" + key + ".json"
        self.write(path, json_bytes({"artifact": relative, "review": review, "result": result,
                                    "human_acceptance": "NOT_RUN"}))
        self.event("EVIDENCE" if stage == "SOURCE_LEARNING" else "READER_SOURCE_REVIEW", art,
                   result["status"], {"review": path, "response": "calls/" + key + ".response.json"})
        return review, result

    def prepare_chapter(self, art, row, sources, research, plan):
        self.event("DISCOVERY", art, "ENTERED")
        discovery = self.stage("discovery_" + art, lambda: self.save_text_call(
            "discovery_" + art, "discover", {"chapter": row, "sources": sources,
                "reader_contract": self.config["reader_prior_knowledge_contract"],
                "research": research, "plan": plan,
                "task": "Find the chapter's distinct causal question, rival explanation and conditions. "
                        "Do not substitute trading advice for understanding the source domain."},
            "research/" + art + ".discovery.md"))
        feedback = None
        for turn in range(self.config["max_revision_rounds"] + 1):
            key = art + "_source_" + str(turn)
            self.event("SOURCE_LEARNING", art, "ENTERED", {"attempt": turn})
            source = self.stage(key, lambda key=key, feedback=feedback: self.save_text_call(
                key, "source_learning" if feedback is None else "source_learning_revise",
                {"chapter": row, "sources": sources, "discovery": self.path(discovery).read_text(),
                 "reader_contract": self.config["reader_prior_knowledge_contract"], "prior_review": feedback,
                 "task": "Explain a concrete native source scene from zero: actors, actual rules/context, choices, "
                         "why it matters, causal process, misconception, counterexample, conditions and transfer limits. "
                         "Research conflicting interpretations; do not treat one reading as uncontested. "
                         "Do not transfer terms before the source mechanism is sound. Return source learning, not a plan."},
                "research/" + key + ".md"))
            if (feedback is not None and feedback["gate"]["status"] == "STOP_RESEARCH_MORE" and
                    substantive_text(feedback["source_learning"]) == substantive_text(self.path(source).read_text())):
                raise Blocked("BLOCKED_QUALITY_UNRESOLVED_SOURCE_REPAIR_WITHOUT_SUBSTANTIVE_CHANGE_" + art)
            review, result = self.stage(key + "_evidence", lambda key=key, source=source:
                self.reader_review(key + "_evidence", art, source, "SOURCE_LEARNING", sources))
            if result["status"] == "MODEL_INTERNAL_REVIEW_RECORDED":
                return {"discovery": discovery, "source_learning": source,
                        "source_evidence_review": "reader_reviews/" + key + "_evidence.json"}
            feedback = {"review": review, "gate": result, "source_learning": self.path(source).read_text()}
        raise Blocked("BLOCKED_QUALITY_UNRESOLVED_SOURCE_LEARNING_" + art)

    def reader_findings(self, art, review, result, prefix):
        rows = []
        for number, f in enumerate(review.get("findings", [])):
            if f.get("severity") in ("MAJOR", "CRITICAL") and f.get("status") not in ("CLOSED", "KEEP"):
                rows.append({"id": prefix + "_" + art + "_" + str(number), "artifact_id": art,
                    "kind": "model_review", "severity": f["severity"], "status": "OPEN",
                    "issue": str(f.get("code", "READER_SOURCE_FAILURE")) + ": " + str(f.get("issue", f.get("evidence", ""))),
                    "evidence": f.get("reason", f.get("evidence", "")), "paragraph": f.get("paragraph")})
        if not rows and result["status"] in ("CONTENT_REWORK", "STOP_RESEARCH_MORE"):
            bad = next((r for r in review.get("reader_checks", []) if r.get("verdict") != "SUPPORTED"), None)
            loc = bad or next(iter(review.get("source_evidence", [])), None)
            if loc:
                rows.append({"id": prefix + "_" + art + "_gate", "artifact_id": art, "kind": "model_review",
                    "severity": "MAJOR", "status": "OPEN", "issue": result["status"] + ": source or reader model review requires repair",
                    "evidence": str((bad or {}).get("rationale") or review.get("source_correctness", {}).get("rationale")),
                    "paragraph": loc["paragraph"]})
        if result["status"] != "MODEL_INTERNAL_REVIEW_RECORDED" and not rows:
            raise Blocked("BLOCKED_QUALITY_UNRESOLVED_READER_REVIEW_WITHOUT_LOCATED_FINDING_" + art)
        return rows

    def content_retention_review(self, key, art, old, new, force=False):
        before, after = self.path(old).read_text(), self.path(new).read_text()
        if not force and len(after) >= len(before) * .75:
            return None
        data = self.call(key + "_loss", "content_loss_review", {
            "baseline": before, "candidate": after, "baseline_sha256": digest(self.path(old).read_bytes()),
            "candidate_sha256": digest(self.path(new).read_bytes()),
            "task": "Length drop triggers investigation, not a word-count verdict. Return JSON units with "
                    "baseline_quote, classification REDUNDANT/MOVED_WITH_EVIDENCE/INDEPENDENT_VALUE_LOST, rationale, "
                    "candidate_quote when moved. Identify source scenes, mechanisms, evidence or counterexamples lost. "
                    "Do not pad prose to satisfy a threshold."})
        review = parse_object(data["text"])
        units = review.get("units")
        if not isinstance(units, list) or not units:
            raise Blocked("BLOCKED_QUALITY_UNRESOLVED_CONTENT_LOSS_REVIEW_MISSING")
        lost = []
        for unit in units:
            if (not unit.get("baseline_quote") or unit["baseline_quote"] not in before or not unit.get("rationale") or
                    unit.get("classification") not in ("REDUNDANT", "MOVED_WITH_EVIDENCE", "INDEPENDENT_VALUE_LOST")):
                raise Blocked("INVALID_CONTENT_LOSS_REVIEW")
            if unit["classification"] == "MOVED_WITH_EVIDENCE" and (not unit.get("candidate_quote") or unit["candidate_quote"] not in after):
                raise Blocked("CONTENT_MOVE_REQUIRES_ACTUAL_DESTINATION_EVIDENCE")
            if unit["classification"] == "INDEPENDENT_VALUE_LOST": lost.append(unit)
        review.update(baseline_sha256=digest(self.path(old).read_bytes()), candidate_sha256=digest(self.path(new).read_bytes()),
                      reviewer=data["provider_kind"] + ":" + data["model"] + ":" + data["response_id"], human_acceptance="NOT_RUN")
        self.write("reviews/" + key + ".content_loss.json", json_bytes(review))
        return lost

    def call(self, key, role, payload):
        self.verify_files()
        request = {"role": role, "model_requested": self.config["model"],
                   "instructions": "Perform the specified writing task. Use supplied material only. "
                   "No tool use. Never claim human acceptance or factual verification not actually done.",
                   "payload": payload}
        stem = "calls/" + key
        req, res = stem + ".request.json", stem + ".response.json"
        if self.path(req).exists():
            prior_request = json.loads(self.path(req).read_text())
            comparable = {k: v for k, v in prior_request.items() if k != "max_output_tokens"}
            if comparable != request:
                raise Blocked("CACHED_REQUEST_PAYLOAD_MISMATCH")
            request = prior_request
        else:
            request["max_output_tokens"] = min(self.config["per_call_output_tokens"],
                self.config["token_budget"] - self.state["tokens"])
        request_raw = json_bytes(request)
        if self.path(res).exists():
            completed = self.state.get("call_completions", {}).get(key)
            if not completed:
                raise Blocked("INCOMPLETE_CALL_COMMIT_NOT_AUTOMATICALLY_RETRIED")
            for part, relative in (("request", req), ("response", res), ("transport", stem + ".transport.json")):
                expected = completed.get(part)
                if (not expected or self.state["files"].get(relative) != expected or
                        digest(self.path(relative).read_bytes()) != expected):
                    raise Blocked("INCOMPLETE_OR_TAMPERED_CALL_COMMIT")
            data = json.loads(self.path(res).read_text())
            if data["request_sha256"] != digest(request_raw):
                raise Blocked("CACHED_RESPONSE_REQUEST_MISMATCH")
        else:
            if self.path(req).exists():
                raise Blocked("UNCERTAIN_OR_FAILED_CALL_NOT_AUTOMATICALLY_RETRIED")
            if self.state["tokens"] >= self.config["token_budget"]:
                raise Blocked("TOKEN_BUDGET_EXHAUSTED")
            self.write(req, request_raw)
            self.save_state()
            cap = request["max_output_tokens"]
            try:
                result = self.model.generate(request["instructions"], json.dumps(request, ensure_ascii=False), cap)
                data = asdict(result)
                data["request_sha256"] = digest(request_raw)
                data["is_live"] = bool(getattr(self.model, "is_live", False))
                data["output_limit_enforced"] = bool(getattr(self.model, "output_limit_enforced", False))
                self.write(res, json_bytes(data))
                raw_transport = getattr(self.model, "last_transport", None) or {
                    "payload_available": False, "reason": "ADAPTER_DID_NOT_EXPOSE_TRANSPORT_PAYLOAD"}
                self.write(stem + ".transport.json", json_bytes(raw_transport))
                self.state.setdefault("call_completions", {})[key] = {
                    "request": self.state["files"][req], "response": self.state["files"][res],
                    "transport": self.state["files"][stem + ".transport.json"]}
                self.save_state()
            except Exception as error:
                raw_transport = getattr(self.model, "last_transport", None)
                if raw_transport:
                    self.write(stem + ".transport.json", json_bytes(raw_transport))
                self.write(stem + ".failure.json", json_bytes({"error_type": type(error).__name__,
                           "message": redact(str(error))[:600], "request_sha256": digest(request_raw),
                           "usage": "UNKNOWN_NO_SUCCESSFUL_RESPONSE"}))
                self.save_state()
                if isinstance(error, transport.MissingCredential) or any(
                        flag in str(error).lower() for flag in ("401", "unauthorized", "login")):
                    raise Blocked("BLOCKED_MODEL_AUTH") from error
                raise Blocked("MODEL_CALL_FAILED_" + type(error).__name__) from error
        usage = data.get("usage")
        if not isinstance(usage, dict) or any(type(usage.get(k)) is not int or usage[k] < 0
                                             for k in ("input_tokens", "output_tokens")):
            if key not in self.state["usage_uncertain_calls"]:
                self.state["usage_uncertain_calls"].append(key)
            self.save_state()
            raise Blocked("MISSING_REAL_TOKEN_USAGE")
        reported = data.get("model")
        if key not in self.state["calls"]:
            cost = usage["input_tokens"] + usage["output_tokens"]
            self.state["calls"][key] = {"response_id": data.get("response_id"), "tokens": cost,
                                        "model": reported, "is_live": data.get("is_live", False)}
            self.state["tokens"] += cost
            self.save_state()
        log_path = self.path(stem + ".transport.json")
        raw_transport = json.loads(log_path.read_text()) if log_path.exists() else {}
        provider_response = raw_transport.get("provider_response", {})
        if raw_transport.get("codex_tool_event_types") or any(
                item.get("type") not in ("message", "reasoning")
                for item in provider_response.get("output", [])):
            raise Blocked("MODEL_TOOLS_USED_ISOLATION_UNVERIFIED")
        if not isinstance(reported, str) or not reported or reported == "UNKNOWN_MODEL":
            raise Blocked("MISSING_MODEL_IDENTITY")
        if self.state["model_reported"] not in (None, reported):
            raise Blocked("MODEL_CHANGED_DURING_RUN")
        self.state["model_reported"] = reported
        if self.state["tokens"] > self.config["token_budget"]:
            raise Blocked("TOKEN_BUDGET_EXCEEDED_RESPONSE_RETAINED")
        if usage["output_tokens"] > request["max_output_tokens"]:
            raise Blocked("OUTPUT_CAP_EXCEEDED_RESPONSE_RETAINED")
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            raise Blocked("EMPTY_MODEL_OUTPUT")
        return data

    def stage(self, key, action):
        if key in self.state["completed"]:
            self.verify_files()
            return copy.deepcopy(self.state["completed"][key])
        result = action()
        self.state["completed"][key] = result
        self.save_state()
        self.steps_this_turn += 1
        if self.stop_after is not None and self.steps_this_turn >= self.stop_after:
            raise Paused()
        return copy.deepcopy(result)

    def save_text_call(self, key, role, payload, path, manuscript=False):
        data = self.call(key, role, payload)
        text = data["text"].strip() + "\n"
        if manuscript and (not text.startswith("# ") or len(text.splitlines()) < 3):
            raise Blocked("NO_COMPLETE_MARKDOWN_MANUSCRIPT")
        self.write(path, text)
        return path

    def location(self, relative, number):
        parts = self.guard.paragraphs(self.path(relative).read_text(encoding="utf-8"))
        if type(number) is not int or number < 1 or number > len(parts):
            raise Blocked("INVALID_MODEL_PARAGRAPH_LOCATION")
        return {"paragraph": number, "sha256": digest(parts[number-1].encode("utf-8"))}

    def build_initial(self, data, current, identity):
        findings = data.get("findings")
        if not isinstance(findings, list) or not findings:
            raise Blocked("EMPTY_REVIEW_NO_READING_EVIDENCE")
        rows = []
        for raw in findings:
            art = raw.get("artifact_id")
            if art not in current:
                raise Blocked("REVIEW_UNKNOWN_ARTIFACT")
            status = raw.get("status", "OPEN")
            if status not in ("OPEN", "KEEP"):
                raise Blocked("INITIAL_REVIEW_CANNOT_CLAIM_CLOSED")
            if not re.fullmatch(r"[A-Za-z0-9_-]+", str(raw.get("id", ""))):
                raise Blocked("INVALID_FINDING_ID")
            loc = self.location(current[art], raw.get("paragraph"))
            f = {"id": raw["id"], "artifact_id": art, "kind": raw.get("kind", "model_review"),
                 "severity": raw["severity"], "status": status, "issue": raw["issue"],
                 "evidence": raw["evidence"], "location": {"baseline": loc, "candidate": loc}}
            if "assertion" in raw:
                f["assertion"] = raw["assertion"]
            if status == "KEEP":
                f["reason"] = raw.get("reason", "")
                if f["kind"] == "model_review":
                    f["review"] = {"verdict": "KEEP", "reviewer": identity,
                                   "rationale": raw["evidence"],
                                   "artifact_sha256": digest(self.path(current[art]).read_bytes()),
                                   "location_sha256": loc["sha256"]}
            rows.append(f)
        if {r["artifact_id"] for r in rows} != set(current):
            raise Blocked("REVIEW_COVERAGE_INCOMPLETE")
        if len({r["id"] for r in rows}) != len(rows):
            raise Blocked("DUPLICATE_FINDING_ID")
        return rows

    def record(self, baseline, candidate, findings):
        return {"schema": "deepwrite/review-closeout/v1",
                "artifacts": [{"artifact_id": art,
                               "baseline": {"path": baseline[art], "sha256": digest(self.path(baseline[art]).read_bytes())},
                               "candidate": {"path": candidate[art], "sha256": digest(self.path(candidate[art]).read_bytes())}}
                              for art in baseline],
                "coverage": list(baseline), "findings": findings}

    def check_record(self, record, expected):
        if self.config["guard"] == "off":
            return {"status": "BYPASSED_BASELINE_ARM", "semantic_status": "NOT_CERTIFIED"}
        return self.guard.check(record, self.root, expected_findings=expected)

    def review_cycle(self, key, current):
        baseline = dict(current)
        self.event("BOOKWIDE_REVIEW" if len(current) > 1 or key in ("cross", "full_book_recheck") else "ADVERSARIAL_REVIEW", key, "ENTERED")
        reader_rows = []
        for art, relative in current.items():
            if art in NON_CHAPTER_PARTS:
                # Front/back matter is part of the actual book-wide reading
                # below. It is not another source-learning chapter.
                continue
            rr, rg = self.reader_review(key + "_" + art + "_reader_0", art, relative, "CHAPTER")
            reader_rows.extend(self.reader_findings(art, rr, rg, "reader"))
        known = ([copy.deepcopy(f) for f in self.config.get("known_findings", [])
                  if f.get("artifact_id") == key] if self.config.get("run_mode") == "replay_frozen_drafts" else [])
        payload = {"manuscripts": {a: self.path(p).read_text() for a, p in current.items()},
                   "review_scope": key,
                   "part_kinds": {a: ("FRONT_MATTER" if a == FRONT_PART else "AFTERWORD" if a == TAIL_PART else "CHAPTER")
                                  for a in current},
                   "task": "Review actual prose and cross-chapter contribution when multiple chapters. "
                   "Return JSON findings; each manuscript needs at least one located finding or justified NOTE KEEP. "
                   "Findings: id,artifact_id,kind(model_review or computable),severity,status(OPEN or KEEP),"
                   "issue,evidence,paragraph(1-based blank-line-delimited),reason for KEEP. "
                   "Computable assertions only contains/not_contains/literal_count with value/count. "
                   "Check independent causal derivation, source rules and disputed interpretations, strong counterexamples, "
                   "evidence limits, false transfer, adjacent-chapter duplicate insights, lost original mechanisms and "
                   "late-book compression. Check concepts used before their necessary explanation, repeated remedial "
                   "teaching and old misconceptions reinforced in later chapters. Front/back matter must also be read "
                   "for claims, source consistency and overstatement; do not require a chapter's source-learning template there. "
                   "Mathematical correctness alone is not thought quality. Flag formulaic prose "
                   "without imposing a new template. G0/G1/G2/G3/G4/G6 still govern. "
                   "Do not invent defects to force rewriting.",
                   "reader_contract": self.config["reader_prior_knowledge_contract"]}
        if known:
            payload["caller_frozen_known_findings"] = known
            payload["task"] += " Known finding ids belong to the caller; do not duplicate or override them."
        reviewed = self.call(key + "_review", "review", payload)
        identity = reviewed["provider_kind"] + ":" + reviewed["model"] + ":" + reviewed["response_id"]
        initial = parse_object(reviewed["text"])
        initial["findings"] = initial.get("findings", []) + reader_rows
        if known:
            reported = initial.get("findings", [])
            if not isinstance(reported, list) or any(f.get("id") in {k["id"] for k in known} for f in reported):
                raise Blocked("MODEL_CANNOT_OVERRIDE_CALLER_FROZEN_FINDING")
            initial["findings"] = reported + known
        findings = self.build_initial(initial, current, identity)
        self.write("reviews/" + key + ".frozen.json", json_bytes(findings))
        expected = copy.deepcopy(findings)
        record = self.record(baseline, current, findings)
        outcome = self.check_record(record, expected)
        for turn in range(self.config["max_revision_rounds"] + 1):
            self.write("reviews/" + key + "." + str(turn) + ".json",
                       json_bytes({"record": record, "guard": outcome}))
            unresolved = any(f["status"] == "OPEN" and f["severity"] in ("MAJOR", "CRITICAL") for f in findings)
            if not unresolved and outcome["status"] in ("PASS_STRUCTURAL_ONLY", "BYPASSED_BASELINE_ARM"):
                return current
            if turn == self.config["max_revision_rounds"]:
                raise Blocked("BLOCKED_QUALITY_UNRESOLVED_REVIEW_STILL_OPEN_" + key)
            affected = {f["artifact_id"] for f in findings if f["status"] == "OPEN"}
            if outcome["status"] == "HOLD" and not affected:
                affected = {f["artifact_id"] for f in findings
                            if f["status"] == "CLOSED" and f["severity"] in ("MAJOR", "CRITICAL")}
            if not affected:
                raise Blocked("BLOCKED_QUALITY_UNRESOLVED_UNLOCATED_CLOSEOUT_FAILURE_" + key)
            self.event("CROSS_CHAPTER_REPAIR" if key in ("cross", "full_book_recheck") else "REVISION_IF_FAILED", key, "ENTERED", {"attempt": turn+1})
            for art in sorted(affected):
                old = current[art]
                path = "chapters/" + art + "." + key + ".r" + str(turn+1) + ".md"
                prompt = {"chapter": self.path(old).read_text(),
                          "frozen_findings": [f for f in expected if f["artifact_id"] == art],
                          "recheck": [f for f in findings if f["artifact_id"] == art],
                          "reader_contract": self.config["reader_prior_knowledge_contract"],
                          "prepared_source_learning": self.state["completed"].get("prepare_" + art),
                          "task": "Return a complete revised Markdown chapter, not a plan or review. "
                                  "Repair the findings while preserving sound prose. Original remains frozen."}
                self.save_text_call(key + "_" + art + "_revise_" + str(turn+1), "revise",
                                    prompt, path, manuscript=True)
                diff = "".join(difflib.unified_diff(self.path(old).read_text().splitlines(True),
                        self.path(path).read_text().splitlines(True), fromfile=old, tofile=path))
                self.write("diffs/" + art + "." + key + "." + str(turn+1) + ".patch", diff)
                lost = self.content_retention_review(key + "_" + art + "_" + str(turn+1), art, old, path)
                if lost:
                    # The candidate is preserved. Do real body work before recheck;
                    # if the budget/repair cap cannot restore it, stop this run.
                    repaired = path + ".retained.md"
                    self.save_text_call(key + "_" + art + "_restore_value_" + str(turn+1), "restore_independent_value",
                        {"baseline": self.path(old).read_text(), "candidate": self.path(path).read_text(),
                         "independent_value_lost": lost,
                         "task": "Return the complete chapter restoring the missing independent mechanism/evidence. "
                                 "Keep justified compression; do not pad to hit a word target."}, repaired, manuscript=True)
                    retained = self.content_retention_review(key + "_" + art + "_restored_" + str(turn+1), art, old, repaired, force=True)
                    if retained:
                        raise Blocked("BLOCKED_QUALITY_UNRESOLVED_INDEPENDENT_VALUE_LOST_" + art)
                    self.write("diffs/" + art + "." + key + "." + str(turn+1) + ".retained.patch",
                        "".join(difflib.unified_diff(self.path(path).read_text().splitlines(True),
                            self.path(repaired).read_text().splitlines(True), fromfile=path, tofile=repaired)))
                    path = repaired
                semantic_major = any(f["artifact_id"] == art and f["kind"] == "model_review" and
                                     f["severity"] in ("MAJOR", "CRITICAL") and f["status"] == "OPEN" for f in findings)
                if semantic_major and substantive_text(self.path(old).read_text()) == substantive_text(self.path(path).read_text()):
                    raise Blocked("BLOCKED_QUALITY_UNRESOLVED_PUNCTUATION_ONLY_REPAIR_" + art)
                current[art] = path
            self.event("RECHECK", key, "ENTERED", {"attempt": turn+1})
            reader_unresolved = set()
            for art, relative in current.items():
                if art in NON_CHAPTER_PARTS:
                    continue
                rr, rg = self.reader_review(key + "_" + art + "_reader_" + str(turn+1), art, relative, "CHAPTER")
                if rg["status"] != "MODEL_INTERNAL_REVIEW_RECORDED":
                    reader_unresolved.add(art)
                    pending_reader = self.reader_findings(art, rr, rg, "reader")
                    self.write("reviews/" + key + ".new_reader_findings." + str(turn+1) + "." + art + ".json", json_bytes(pending_reader))
                    # A new MAJOR must retain its severity. Never map it onto
                    # an old NOTE/KEEP and allow that lower severity through.
                    existing_reader_major = any(f["artifact_id"] == art and f["id"].startswith("reader_") and
                        f["severity"] in ("MAJOR", "CRITICAL") for f in expected)
                    if not existing_reader_major:
                        raise Blocked("BLOCKED_QUALITY_UNRESOLVED_NEW_READER_MAJOR_" + art)
            data = self.call(key + "_recheck_" + str(turn+1), "recheck",
                    {"frozen_findings": expected,
                     "manuscripts": {a: self.path(p).read_text() for a, p in current.items()},
                     "task": "Return JSON findings exactly covering frozen ids: id,status(OPEN/CLOSED/KEEP),"
                             "paragraph,evidence,reason if KEEP. Re-read actual manuscript; do not claim closure from intent. "
                             "Use new_findings:[{artifact_id,severity,issue,evidence,paragraph}] for newly discovered "
                             "issues; never drop a major new issue or replace a frozen id."})
            rechecked = parse_object(data["text"])
            new_findings = rechecked.get("new_findings", [])
            if not isinstance(new_findings, list):
                raise Blocked("NEW_FINDINGS_NOT_LIST")
            if new_findings:
                self.write("reviews/" + key + ".new_findings." + str(turn+1) + ".json", json_bytes(new_findings))
                for fresh in new_findings:
                    if (fresh.get("artifact_id") not in current or fresh.get("severity") not in
                            ("NOTE", "MINOR", "MAJOR", "CRITICAL") or not fresh.get("issue") or not fresh.get("evidence")):
                        raise Blocked("INVALID_NEW_FINDING")
                    self.location(current[fresh["artifact_id"]], fresh.get("paragraph"))
                if any(f["severity"] in ("MAJOR", "CRITICAL") for f in new_findings):
                    raise Blocked("NEW_MAJOR_FINDINGS_HOLD_REVIEW_SCOPE_NOT_SILENTLY_EXPANDED")
            replies = rechecked.get("findings", [])
            if len(replies) != len(expected) or {x.get("id") for x in replies} != {x["id"] for x in expected}:
                raise Blocked("RECHECK_FROZEN_FINDING_SET_MISMATCH")
            mapping = {x["id"]: x for x in replies}
            findings = []
            for original in expected:
                item = copy.deepcopy(original)
                reply = mapping[original["id"]]
                art = original["artifact_id"]
                item.update(status=reply["status"], evidence=reply["evidence"])
                if art in reader_unresolved:
                    item["status"] = "OPEN"
                item["location"]["candidate"] = self.location(current[art], reply["paragraph"])
                if reply["status"] == "KEEP":
                    item["reason"] = reply.get("reason", "")
                if item["kind"] == "model_review":
                    item["review"] = {"verdict": reply["status"],
                        "reviewer": data["provider_kind"] + ":" + data["model"] + ":" + data["response_id"],
                        "rationale": reply["evidence"],
                        "artifact_sha256": digest(self.path(current[art]).read_bytes()),
                        "location_sha256": item["location"]["candidate"]["sha256"]}
                findings.append(item)
            record = self.record(baseline, current, findings)
            outcome = self.check_record(record, expected)
        raise Blocked("UNREACHABLE_REVIEW_STATE")

    def check_historical_findings(self, current):
        """Final bytes must still satisfy earlier known computable resolutions.

        A later edit invalidates an earlier model-review byte binding. Hold for
        explicit located rereading; do not pretend the old judgment covers it.
        """
        if self.config["guard"] == "off":
            return {"status": "BYPASSED_BASELINE_ARM"}
        latest = {}
        for relative in sorted(self.state["files"]):
            match = re.fullmatch(r"reviews/([A-Za-z0-9_-]+)\.([0-9]+)\.json", relative)
            if match:
                key, turn = match.group(1), int(match.group(2))
                if key not in latest or turn > latest[key][0]:
                    latest[key] = (turn, relative)
        checks, failures = [], []
        for key, (_, relative) in sorted(latest.items()):
            record = json.loads(self.path(relative).read_text())["record"]
            for finding in record["findings"]:
                if finding["status"] not in ("CLOSED", "KEEP"):
                    continue
                art = finding["artifact_id"]
                final = self.path(current[art])
                row = {"review": key, "finding_id": finding["id"], "artifact_id": art,
                       "final_path": current[art], "final_sha256": digest(final.read_bytes())}
                if finding["kind"] == "computable":
                    evaluated = self.guard.evaluate(finding["assertion"], final.read_text())
                    row["assertion_result"] = evaluated
                    if not evaluated["passed"]:
                        failures.append({"reason": "COMPUTABLE_REGRESSION", **row})
                elif finding["review"]["artifact_sha256"] != row["final_sha256"]:
                    call_key = "history_" + digest(json_bytes([key, finding["id"], row["final_sha256"]]))[:20]
                    data = self.call(call_key, "historical_recheck", {
                        "frozen_finding": finding, "manuscript": final.read_text(),
                        "artifact_sha256": row["final_sha256"],
                        "task": "A later edit invalidated this prior semantic judgment. Re-read the actual final chapter "
                            "against this exact earlier issue. Return JSON status OPEN/CLOSED/KEEP, paragraph, evidence, "
                            "reason for KEEP, new_findings. Do not inherit the previous closure or call this human acceptance."})
                    reply = parse_object(data["text"])
                    loc = self.location(current[art], reply.get("paragraph"))
                    receipt = {"source_review": relative, "frozen_finding_id": finding["id"],
                        "issue": finding["issue"], "artifact_sha256": row["final_sha256"], "location": loc,
                        "reply": reply, "reviewer": data["provider_kind"] + ":" + data["model"] + ":" + data["response_id"],
                        "human_acceptance": "NOT_RUN", "semantic_status": "MODEL_REVIEW_NOT_MACHINE_CERTIFIED"}
                    self.write("reviews/" + call_key + ".json", json_bytes(receipt))
                    row["actual_model_recheck"] = "reviews/" + call_key + ".json"
                    if (reply.get("status") not in ("KEEP", "CLOSED") or not reply.get("evidence") or
                            (reply["status"] == "KEEP" and not reply.get("reason")) or
                            any(f.get("severity") in ("MAJOR", "CRITICAL") for f in reply.get("new_findings", []))):
                        failures.append({"reason": "MODEL_RECHECK_UNRESOLVED_PRIOR_FINDING", **row})
                checks.append(row)
        outcome = {"status": "HOLD" if failures else "PASS_KNOWN_FINDINGS_ONLY",
                   "checks": checks, "failures": failures, "semantic_status": "NOT_MACHINE_CERTIFIED"}
        self.write("reviews/final_historical_findings.json", json_bytes(outcome))
        if failures:
            raise Blocked("BLOCKED_QUALITY_UNRESOLVED_HISTORICAL_FINDING_REGRESSION_OR_STALE_MODEL_REVIEW")
        return outcome

    def checkpoint_now(self):
        self.save_state()
        files = sorted(self.state["files"])
        required = ["run_state.json", *files]
        policy = {"project_id": self.config["project_id"], "required_files": required,
                  "protocols": self.config["pins"]["protocols"], "channel": self.config["channel"],
                  "module_policy": self.config["module_policy"],
                  "enabled_candidate_commits": self.config["module_commits"]}
        requirements = self.root.parent / (self.root.name + ".requirements.json")
        policy_raw = json_bytes(policy)
        if requirements.exists() and requirements.read_bytes() != policy_raw:
            requirements = self.root.parent / (self.root.name + "." + str(len(self.state["completed"])) + ".requirements.json")
        requirements.write_bytes(policy_raw)
        state_hash = digest((self.root / "run_state.json").read_bytes())
        dest = self.root.parent / (self.root.name + ".checkpoint." + str(len(self.state["completed"])) + "." + state_hash[:16])
        result = checkpoint.snapshot(self.root, dest, self.config["project_id"],
                                     "run_state.json", "pins.json", "config.json",
                                     [p for p in files if p not in ("pins.json", "config.json")])
        check = resume_checker.check(dest, result["manifest_sha256"],
                                     requirements, digest(policy_raw))
        if check["status"] != resume_checker.PASS:
            raise Blocked("DECLARED_CHECKPOINT_RESUME_REJECTED")
        return {"path": str(dest), "manifest_sha256": result["manifest_sha256"],
                "requirements": str(requirements), "requirements_sha256": digest(policy_raw),
                "state_sha256": digest((self.root / "run_state.json").read_bytes()),
                "scope": "DECLARED_FILES_ONLY_NOT_FULL_PROJECT_AUTHORITY"}

    def run(self):
        try:
            if self.state["status"] in ("CANDIDATE_PENDING_HUMAN", "ENGINEERING_FIXTURE_ONLY_NOT_LIVE"):
                self.verify_files()
                return {"status": self.state["status"], "tokens": self.state["tokens"],
                        "book_sha256": self.state["files"]["book.md"], "resume": "ALREADY_COMPLETE_NO_MODEL_CALL",
                        "quality": "UNVERIFIED", "fair_B0_B1": "UNVERIFIED"}
            sources = {s["path"]: self.path(s["path"]).read_text() for s in self.config["sources"]}
            policy = "\n".join((DEEPWRITE / "candidates" / name).read_text()
                               for name in ("RESEARCH_LOOP.md", "EDITORIAL_LOOP.md"))
            replay = self.config.get("run_mode") == "replay_frozen_drafts"
            research, plan = None, None
            if not replay:
                research = self.stage("research", lambda: self.save_text_call(
                    "research", "research", {"wish": self.config["wish"], "sources": sources,
                                             "workflow": policy}, "research.md"))
                plan = self.stage("direction", lambda: self.save_text_call(
                    "direction", "select_direction", {"research": self.path(research).read_text(),
                    "topics": self.config["chapters"], "task": "Compare genuinely different directions, select chapter-specific "
                    "questions, counterexamples and dependencies. Return the selected plan as Markdown."}, "plan.md"))
            chapters = {}
            for row in self.config["chapters"]:
                art = row["artifact_id"]
                self.author_scope(chapters, art)
                prepared = self.stage("prepare_" + art, lambda art=art, row=row:
                    self.prepare_chapter(art, row, sources,
                        self.path(research).read_text() if research else "FROZEN_DRAFT_REPLAY",
                        self.path(plan).read_text() if plan else "FROZEN_DRAFT_REPLAY"))
                def draft(row=row, art=art):
                    dest = "chapters/" + art + ".draft.md"
                    if replay:
                        source = self.config["replay_drafts"][art]
                        self.write(dest, self.path(source).read_bytes())
                        return dest
                    self.event("DRAFT", art, "ENTERED", {"source_evidence": prepared})
                    return self.save_text_call(
                        "draft_" + art, "draft", {"chapter": row, "sources": sources,
                        "research": self.path(research).read_text(), "plan": self.path(plan).read_text(),
                        "already_completed": {a: self.path(p).read_text() for a, p in chapters.items()},
                        "reader_contract": self.config["reader_prior_knowledge_contract"],
                        "source_learning": self.path(prepared["source_learning"]).read_text(),
                        "source_evidence_review": json.loads(self.path(prepared["source_evidence_review"]).read_text()),
                        "task": "Write the complete readable chapter in Markdown, not a plan or audit."},
                        dest, manuscript=True)
                path = self.stage("draft_" + art, draft)
                reviewed = self.stage("close_" + art,
                                      lambda art=art, path=path: self.review_cycle(art, {art: path}))
                chapters.update(reviewed)
                self.event("CHAPTER_CANDIDATE_READY", art, "MODEL_INTERNAL_REVIEW_RECORDED",
                           {"artifact": chapters[art], "sha256": digest(self.path(chapters[art]).read_bytes()), "human_acceptance": "NOT_RUN"})
            self.author_scope(chapters)
            self.event("BOOKWIDE_REVIEW", "BOOK", "ENTERED")
            chapters = self.stage("cross_close", lambda: self.review_cycle("cross", dict(chapters)))
            front = self.stage("front", lambda: self.save_text_call(
                "front", "front_matter", {"chapters": {a: self.path(p).read_text() for a,p in chapters.items()},
                "task": "Write a short honest preface in Markdown; do not oversell evidence."},
                "front.md", manuscript=True))
            tail = self.stage("tail", lambda: self.save_text_call(
                "tail", "afterword", {"chapters": {a: self.path(p).read_text() for a,p in chapters.items()},
                "task": "Write a short afterword in Markdown; no claim of human acceptance or validation."},
                "tail.md", manuscript=True))
            self.event("FULL_BOOK_RECHECK", "BOOK", "ENTERED")
            all_parts = {FRONT_PART: front, **chapters, TAIL_PART: tail}
            all_parts = self.stage("full_book_recheck", lambda: self.review_cycle("full_book_recheck", dict(all_parts)))
            self.stage("historical_findings", lambda: self.check_historical_findings(all_parts))
            chapters = {row["artifact_id"]: all_parts[row["artifact_id"]] for row in self.config["chapters"]}
            front, tail = all_parts[FRONT_PART], all_parts[TAIL_PART]
            def package():
                def entry(path):
                    raw = self.path(path).read_bytes()
                    return {"relative_path": path, "sha256": digest(raw), "bytes": len(raw)}
                manifest = {"working_title": self.config["working_title"],
                            "expected_chapters": len(chapters), "front": entry(front), "tail": entry(tail),
                            "chapters": [dict(number=i+1, title=row["title"], **entry(chapters[row["artifact_id"]]))
                                         for i,row in enumerate(self.config["chapters"])]}
                self.write("manifest.json", json_bytes(manifest))
                packager.assemble(manifest, self.root, self.path("book.md"), self.path("package.json"),
                                  self.path("manifest.json"))
                self.track("book.md"); self.track("package.json")
                return "book.md"
            self.stage("package", package)
            self.state["status"] = ("CANDIDATE_PENDING_HUMAN" if all(x["is_live"] for x in self.state["calls"].values())
                                    else "ENGINEERING_FIXTURE_ONLY_NOT_LIVE")
            self.state["acceptance"]["ENGINEERING_VERIFIED"] = "ACTUAL_FILE_CHECKS_RECORDED"
            self.state["acceptance"]["MODEL_INTERNAL_QUALITY_REVIEW"] = ("ACTUAL_MODEL_REVIEW_RECORDED_NOT_AUTHOR_ACCEPTANCE"
                if all(x["is_live"] for x in self.state["calls"].values()) else "ENGINEERING_FIXTURE_ONLY_NOT_MODEL_REVIEW")
            receipt = self.checkpoint_now()
            return {"status": self.state["status"], "tokens": self.state["tokens"],
                    "book_sha256": self.state["files"]["book.md"], "checkpoint": receipt,
                    "quality": "UNVERIFIED", "fair_B0_B1": "UNVERIFIED"}
        except AuthorReviewRequired as error:
            self.state["status"] = "AWAIT_AUTHOR_REVIEW"
            self.state["unique_next_step"] = "Obtain actual author review for this project's exact sample SHA, or an explicit narrowly scoped new author instruction; do not change execution mode."
            self.state["failure"] = {"type": type(error).__name__, "message": str(error)}
            receipt = self.checkpoint_now()
            return {"status": "AWAIT_AUTHOR_REVIEW", "checkpoint": receipt, "failure": self.state["failure"]}
        except Paused:
            self.state["status"] = "PAUSED"
            receipt = self.checkpoint_now()
            return {"status": "PAUSED", "checkpoint": receipt}
        except (Blocked, OSError, ValueError, KeyError, TypeError, SystemExit) as error:
            quality_block = "QUALITY_UNRESOLVED" in str(error) or "NEW_MAJOR_FINDINGS_HOLD" in str(error)
            self.state["status"] = "BLOCKED_QUALITY_UNRESOLVED" if quality_block else "BLOCKED"
            self.state["unique_next_step"] = "Resolve the located saved quality finding or missing execution evidence before the next chapter; preserve original drafts and failed responses."
            self.state["failure"] = {"type": type(error).__name__, "message": redact(str(error))[:600]}
            self.save_state()
            return {"status": self.state["status"], "failure": self.state["failure"],
                    "state_sha256": digest((self.root / "run_state.json").read_bytes())}


def restore_project(checkpoint_path, destination, manifest_sha, requirements_path, requirements_sha):
    checked = resume_checker.check(Path(checkpoint_path), manifest_sha, Path(requirements_path), requirements_sha)
    if checked["status"] != resume_checker.PASS:
        raise Blocked("RESTORE_DECLARED_REQUIREMENTS_REJECTED")
    return checkpoint.restore(Path(checkpoint_path), Path(destination), manifest_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("root", type=Path)
    parser.add_argument("--expected-state-sha256")
    parser.add_argument("--stop-after", type=int)
    parser.add_argument("--author-approval-receipt", type=Path)
    parser.add_argument("--author-approval-sha256")
    args = parser.parse_args()
    try:
        cfg = json.loads(args.config.read_text(encoding="utf-8"))
        result = WritingLoop(args.root, cfg, expected_state_sha=args.expected_state_sha256,
                             stop_after=args.stop_after, author_approval_receipt=args.author_approval_receipt,
                             expected_author_approval_sha=args.author_approval_sha256).run()
    except Exception as error:
        result = {"status": "BLOCKED", "error_type": type(error).__name__, "message": redact(str(error))[:600]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in ("CANDIDATE_PENDING_HUMAN", "PAUSED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
