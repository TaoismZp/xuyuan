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


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
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


def digest(data):
    return hashlib.sha256(data).hexdigest()


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
    def __init__(self, root, config, model=None, expected_state_sha=None, stop_after=None):
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
        self._validate_config()
        state_path = self.root / "run_state.json"
        if state_path.exists():
            raw = state_path.read_bytes()
            if not expected_state_sha or digest(raw) != expected_state_sha:
                raise Blocked("EXTERNAL_STATE_SHA_REQUIRED_OR_MISMATCH")
            self.state = json.loads(raw)
            if self.state["config_sha256"] != self.cfg_sha:
                raise Blocked("FROZEN_CONFIG_MISMATCH")
            self.verify_files()
        else:
            if any(self.root.iterdir()) and not all(p.name == "sources" for p in self.root.iterdir()):
                raise Blocked("NEW_PROJECT_OUTPUT_NOT_EMPTY")
            self.state = {"schema": "deepwrite/writing-loop-state/v0", "config_sha256": self.cfg_sha,
                          "status": "STARTED", "files": {}, "completed": {}, "calls": {}, "call_completions": {},
                          "tokens": 0, "usage_uncertain_calls": [], "model_reported": None, "quality": "UNVERIFIED",
                          "run_mode": config.get("run_mode", "fresh"),
                          "draft_origin": ("FROZEN_BASELINE_REPLAY_NOT_FRESH_B0_B1" if config.get("run_mode") == "replay_frozen_drafts" else "MODEL_DRAFTED"),
                          "human_acceptance": "NOT_RUN", "fair_B0_B1": "UNVERIFIED"}
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
        if c.get("channel") not in ("CANDIDATE_OPT_IN", "SHADOW"):
            raise Blocked("EXPERIMENTAL_RUNNER_REQUIRES_CANDIDATE_CHANNEL")
        checkpoint.validate_pins(json_bytes(c["pins"]), c["project_id"])

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
        known = ([copy.deepcopy(f) for f in self.config.get("known_findings", [])
                  if f.get("artifact_id") == key] if self.config.get("run_mode") == "replay_frozen_drafts" else [])
        payload = {"manuscripts": {a: self.path(p).read_text() for a, p in current.items()},
                   "task": "Review actual prose and cross-chapter contribution when multiple chapters. "
                   "Return JSON findings; each manuscript needs at least one located finding or justified NOTE KEEP. "
                   "Findings: id,artifact_id,kind(model_review or computable),severity,status(OPEN or KEEP),"
                   "issue,evidence,paragraph(1-based blank-line-delimited),reason for KEEP. "
                   "Computable assertions only contains/not_contains/literal_count with value/count. "
                   "Do not invent defects to force rewriting."}
        if known:
            payload["caller_frozen_known_findings"] = known
            payload["task"] += " Known finding ids belong to the caller; do not duplicate or override them."
        reviewed = self.call(key + "_review", "review", payload)
        identity = reviewed["provider_kind"] + ":" + reviewed["model"] + ":" + reviewed["response_id"]
        initial = parse_object(reviewed["text"])
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
                raise Blocked("REVIEW_STILL_OPEN_" + key)
            affected = {f["artifact_id"] for f in findings
                        if f["status"] == "OPEN" or outcome["status"] == "HOLD"}
            for art in sorted(affected):
                old = current[art]
                path = "chapters/" + art + "." + key + ".r" + str(turn+1) + ".md"
                prompt = {"chapter": self.path(old).read_text(),
                          "frozen_findings": [f for f in expected if f["artifact_id"] == art],
                          "recheck": [f for f in findings if f["artifact_id"] == art],
                          "task": "Return a complete revised Markdown chapter, not a plan or review. "
                                  "Repair the findings while preserving sound prose. Original remains frozen."}
                self.save_text_call(key + "_" + art + "_revise_" + str(turn+1), "revise",
                                    prompt, path, manuscript=True)
                diff = "".join(difflib.unified_diff(self.path(old).read_text().splitlines(True),
                        self.path(path).read_text().splitlines(True), fromfile=old, tofile=path))
                self.write("diffs/" + art + "." + key + "." + str(turn+1) + ".patch", diff)
                current[art] = path
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
            match = re.fullmatch(r"reviews/(.+)\.([0-9]+)\.json", relative)
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
                    failures.append({"reason": "MODEL_REVIEW_BINDING_STALE_EXPLICIT_REREAD_REQUIRED", **row})
                checks.append(row)
        outcome = {"status": "HOLD" if failures else "PASS_KNOWN_FINDINGS_ONLY",
                   "checks": checks, "failures": failures, "semantic_status": "NOT_MACHINE_CERTIFIED"}
        self.write("reviews/final_historical_findings.json", json_bytes(outcome))
        if failures:
            raise Blocked("HISTORICAL_FINDING_REGRESSION_OR_STALE_MODEL_REVIEW")
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
        dest = self.root.parent / (self.root.name + ".checkpoint." + str(len(self.state["completed"])))
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
                def draft(row=row, art=art):
                    dest = "chapters/" + art + ".draft.md"
                    if replay:
                        source = self.config["replay_drafts"][art]
                        self.write(dest, self.path(source).read_bytes())
                        return dest
                    return self.save_text_call(
                        "draft_" + art, "draft", {"chapter": row, "sources": sources,
                        "research": self.path(research).read_text(), "plan": self.path(plan).read_text(),
                        "already_completed": {a: self.path(p).read_text() for a, p in chapters.items()},
                        "task": "Write the complete readable chapter in Markdown, not a plan or audit."},
                        dest, manuscript=True)
                path = self.stage("draft_" + art, draft)
                reviewed = self.stage("close_" + art,
                                      lambda art=art, path=path: self.review_cycle(art, {art: path}))
                chapters.update(reviewed)
            chapters = self.stage("cross_close", lambda: self.review_cycle("cross", dict(chapters)))
            self.stage("historical_findings", lambda: self.check_historical_findings(chapters))
            front = self.stage("front", lambda: self.save_text_call(
                "front", "front_matter", {"chapters": {a: self.path(p).read_text() for a,p in chapters.items()},
                "task": "Write a short honest preface in Markdown; do not oversell evidence."},
                "front.md", manuscript=True))
            tail = self.stage("tail", lambda: self.save_text_call(
                "tail", "afterword", {"chapters": {a: self.path(p).read_text() for a,p in chapters.items()},
                "task": "Write a short afterword in Markdown; no claim of human acceptance or validation."},
                "tail.md", manuscript=True))
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
            receipt = self.checkpoint_now()
            return {"status": self.state["status"], "tokens": self.state["tokens"],
                    "book_sha256": self.state["files"]["book.md"], "checkpoint": receipt,
                    "quality": "UNVERIFIED", "fair_B0_B1": "UNVERIFIED"}
        except Paused:
            self.state["status"] = "PAUSED"
            receipt = self.checkpoint_now()
            return {"status": "PAUSED", "checkpoint": receipt}
        except (Blocked, OSError, ValueError, KeyError, TypeError, SystemExit) as error:
            self.state["status"] = "BLOCKED"
            self.state["failure"] = {"type": type(error).__name__, "message": redact(str(error))[:600]}
            self.save_state()
            return {"status": "BLOCKED", "failure": self.state["failure"],
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
    args = parser.parse_args()
    try:
        cfg = json.loads(args.config.read_text(encoding="utf-8"))
        result = WritingLoop(args.root, cfg, expected_state_sha=args.expected_state_sha256,
                             stop_after=args.stop_after).run()
    except Exception as error:
        result = {"status": "BLOCKED", "error_type": type(error).__name__, "message": redact(str(error))[:600]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in ("CANDIDATE_PENDING_HUMAN", "PAUSED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
