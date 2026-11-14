#!/usr/bin/env python3
"""Executed public engineering controls. No model, author or human-quality PASS."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from test_writing_loop_experimental import loop, ScriptedModel, config, reader_report, CORRECT


def response(model, text):
    return loop.transport.ModelResult("fixture-quality-" + str(len(model.calls)), "fixture-model", text,
                                    {"input_tokens": 10, "output_tokens": 10}, "scripted_fixture")


class BlackboxExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="deepwrite-quality-fixture-")
        self.base = Path(self.tmp.name)
        self.root = self.base / "project"
        self.cfg = config(self.root)

    def tearDown(self): self.tmp.cleanup()

    def run_model(self, model=None, **kwargs):
        obj = loop.WritingLoop(self.root, self.cfg, model=model or ScriptedModel(clean=True), **kwargs)
        return obj, obj.run()

    def assisted(self, extra=()):
        contract = self.cfg["execution_contract"]
        contract.update(mode="ASSISTED_AUTHOR_GATED", sample_chapters=["alpha"],
                        allowed_unapproved_candidate_chapters=list(extra))
        auth = self.root / contract["authorization"]["path"]
        auth.write_bytes(loop.json_bytes({"schema": "deepwrite/author-project-authorization/v1", "project_id": self.cfg["project_id"],
            "mode": "ASSISTED_AUTHOR_GATED", "chapter_scope": ["alpha", *extra],
            "author_identity_verification": "ENGINEERING_FIXTURE_NOT_REAL_AUTHOR"}))
        contract["authorization"]["sha256"] = loop.digest(auth.read_bytes())
        next(s for s in self.cfg["sources"] if s["path"] == contract["authorization"]["path"])["sha256"] = loop.digest(auth.read_bytes())
        if extra: contract["scope_authorization"] = copy.deepcopy(contract["authorization"])

    def test_missing_mode_does_not_default_to_autonomous(self):
        del self.cfg["execution_contract"]
        with self.assertRaisesRegex(loop.Blocked, "FROZEN_AUTHOR_EXECUTION_MODE"):
            self.run_model()

    def test_other_project_or_mode_cannot_supply_this_books_authorization(self):
        reference = self.cfg["execution_contract"]["authorization"]
        path = self.root / reference["path"]
        original = json.loads(path.read_text())
        for overrides in ({"project_id": "another-book"}, {"mode": "ASSISTED_AUTHOR_GATED"},
                          {"chapter_scope": ["alpha"]}):
            with self.subTest(overrides=overrides):
                envelope = {**original, **overrides}
                path.write_bytes(loop.json_bytes(envelope))
                reference["sha256"] = loop.digest(path.read_bytes())
                next(s for s in self.cfg["sources"] if s["path"] == reference["path"])["sha256"] = reference["sha256"]
                with self.assertRaisesRegex(loop.Blocked, "AUTHOR_AUTHORIZATION_PROJECT_OR_MODE_MISMATCH|AUTHORIZATION_SCOPE_REQUIRED"):
                    self.run_model()

    def test_responses_codex_and_live_fixture_cannot_disable_closeout(self):
        self.cfg["guard"] = "off"
        for adapter in ("responses", "codex"):
            with self.subTest(adapter=adapter):
                self.cfg["adapter"] = adapter
                with self.assertRaisesRegex(loop.Blocked, "REAL_WRITING_CANNOT_BYPASS"):
                    self.run_model()
        self.cfg["adapter"] = "fixture"
        live = ScriptedModel(clean=True)
        live.is_live = True
        with self.assertRaisesRegex(loop.Blocked, "LIVE_WRITING_CANNOT_BYPASS"):
            self.run_model(live)

    def test_actual_source_calls_precede_draft_and_whole_book_is_reread(self):
        model = ScriptedModel(clean=True)
        obj, result = self.run_model(model)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertLess(model.calls.index("source_learning"), model.calls.index("draft"))
        self.assertLess(model.calls.index("source_evidence_review"), model.calls.index("draft"))
        self.assertGreaterEqual(model.calls.count("review"), 3)
        phases = {e["phase"] for e in obj.state["gate_events"]}
        self.assertTrue({"DISCOVERY", "SOURCE_LEARNING", "EVIDENCE", "DRAFT", "ADVERSARIAL_REVIEW",
                         "CHAPTER_CANDIDATE_READY", "BOOKWIDE_REVIEW", "FULL_BOOK_RECHECK"} <= phases)
        self.assertEqual(obj.state["acceptance"]["AUTHOR_ACCEPTANCE"], "NOT_RUN")
        self.assertEqual(obj.state["acceptance"]["HUMAN_BLIND_EVALUATION"], "NOT_RUN")
        request = json.loads((self.root/"calls/full_book_recheck_review.request.json").read_text())
        self.assertEqual(set(request["payload"]["manuscripts"]), {"alpha", loop.FRONT_PART, loop.TAIL_PART})
        self.assertIn("engineering fixture", request["payload"]["manuscripts"][loop.FRONT_PART])
        self.assertIn("No human", request["payload"]["manuscripts"][loop.TAIL_PART])

    def test_front_matter_major_is_rewritten_before_final_assembly(self):
        class FrontFailure(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt); role, payload = req["role"], req["payload"]
                if role == "front_matter":
                    self.calls.append(role)
                    return response(self, "# Preface\n\nINVALID_FRONT_CLAIM: this fixture has been accepted by real readers.\n")
                if role == "review" and payload.get("review_scope") == "full_book_recheck":
                    rows = []
                    for art, text in payload["manuscripts"].items():
                        if art == loop.FRONT_PART:
                            rows.append({"id": "front_accuracy", "artifact_id": art, "kind": "model_review",
                                "severity": "MAJOR", "status": "OPEN", "issue": "Unsupported reader acceptance",
                                "evidence": "The preface asserts a human reading that never occurred.", "paragraph": 2})
                        else:
                            rows.append({"id": "keep_"+art, "artifact_id": art, "kind": "computable",
                                "severity": "NOTE", "status": "KEEP", "issue": "Keep correct text", "paragraph": 2,
                                "evidence": "No error marker present.", "reason": "Preserve sound prose.",
                                "assertion": {"op": "not_contains", "value": "ERROR"}})
                    self.calls.append(role)
                    return response(self, json.dumps({"findings": rows}))
                if role == "revise" and any(f["id"] == "front_accuracy" for f in payload["frozen_findings"]):
                    self.calls.append(role)
                    return response(self, "# Preface\n\nThis is an engineering fixture with no human quality acceptance.\n")
                if role == "recheck" and any(f["id"] == "front_accuracy" for f in payload["frozen_findings"]):
                    self.calls.append(role)
                    return response(self, json.dumps({"findings": [{"id": f["id"], "paragraph": 2,
                        "status": "CLOSED" if f["id"] == "front_accuracy" else "KEEP",
                        "evidence": "Actual revised preface no longer invents acceptance; correct text retained.",
                        "reason": "Preserve correct original."} for f in payload["frozen_findings"]]}))
                return super().generate(instructions, prompt, max_output_tokens)
        _, result = self.run_model(FrontFailure(clean=True))
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertIn("INVALID_FRONT_CLAIM", (self.root/"front.md").read_text())
        self.assertNotIn("INVALID_FRONT_CLAIM", (self.root/"book.md").read_text())
        self.assertIn("no human quality acceptance", (self.root/"book.md").read_text())
        manifest = json.loads((self.root/"manifest.json").read_text())
        self.assertNotEqual(manifest["front"]["relative_path"], "front.md")

    def test_unapproved_sample_blocks_next_chapter_and_packaging(self):
        self.assisted()
        self.cfg["chapters"].append({"artifact_id": "beta", "title": "Later decision"})
        obj, result = self.run_model()
        self.assertEqual(result["status"], "AWAIT_AUTHOR_REVIEW", result)
        self.assertTrue((self.root/"chapters/alpha.draft.md").exists())
        self.assertFalse((self.root/"chapters/beta.draft.md").exists())
        self.assertFalse((self.root/"book.md").exists())
        self.assertEqual(obj.state["execution_mode"], "ASSISTED_AUTHOR_GATED")

    def test_one_chapter_author_exception_does_not_approve_bulk_or_sample(self):
        self.assisted(extra=["beta"])
        self.cfg["chapters"] += [{"artifact_id": a, "title": a} for a in ("beta", "gamma")]
        obj, result = self.run_model()
        self.assertEqual(result["status"], "AWAIT_AUTHOR_REVIEW", result)
        self.assertTrue((self.root/"chapters/beta.draft.md").exists())
        self.assertFalse((self.root/"chapters/gamma.draft.md").exists())
        self.assertEqual(obj.state["acceptance"]["AUTHOR_ACCEPTANCE"], "NOT_RUN")
        self.assertEqual(obj.state["execution_mode"], "ASSISTED_AUTHOR_GATED")

    def test_resume_cannot_silently_change_project_authorization_mode(self):
        self.assisted()
        self.cfg["chapters"].append({"artifact_id": "beta", "title": "Later"})
        _, paused = self.run_model()
        self.cfg["execution_contract"]["mode"] = "AUTONOMOUS_FULL_DRAFT"
        with self.assertRaisesRegex(loop.Blocked, "FROZEN_CONFIG_MISMATCH|AUTHOR_AUTHORIZATION_PROJECT_OR_MODE_MISMATCH"):
            self.run_model(expected_state_sha=paused["checkpoint"]["state_sha256"])

    def test_restored_project_cannot_lose_reader_or_mode_gate(self):
        _, paused = self.run_model(stop_after=1)
        cp = paused["checkpoint"]
        for missing in ("reader_contract_sha256", "execution_contract_sha256", "execution_mode"):
            with self.subTest(missing=missing):
                restored = self.base / ("restored-" + missing)
                loop.restore_project(cp["path"], restored, cp["manifest_sha256"],
                                     cp["requirements"], cp["requirements_sha256"])
                state_file = restored / "run_state.json"
                state = json.loads(state_file.read_text()); del state[missing]
                state_file.write_bytes(loop.json_bytes(state))
                before = state_file.read_bytes()
                model = ScriptedModel(clean=True)
                with self.assertRaisesRegex(loop.Blocked, "RESUME_LOST_FROZEN_QUALITY_CONTRACT"):
                    loop.WritingLoop(restored, self.cfg, model=model, expected_state_sha=loop.digest(before))
                self.assertEqual(model.calls, [])
                self.assertEqual(state_file.read_bytes(), before)

    def test_model_generated_approval_is_not_author_acceptance(self):
        self.assisted()
        self.cfg["chapters"].append({"artifact_id": "beta", "title": "Later"})
        obj, paused = self.run_model()
        receipt = {"schema": "deepwrite/external-author-sample-approval/v1", "project_id": self.cfg["project_id"],
            "execution_contract_sha256": obj.contract_sha, "status": "APPROVED",
            "approved_artifacts": {"alpha": loop.digest((self.root/"chapters/alpha.draft.md").read_bytes())},
            "verification": {"method": "MODEL_SELF_APPROVAL", "evidence_reference": "fake", "model_generated": True}}
        path = self.base / "fake-approval.json"; path.write_bytes(loop.json_bytes(receipt))
        _, again = self.run_model(expected_state_sha=paused["checkpoint"]["state_sha256"],
            author_approval_receipt=path, expected_author_approval_sha=loop.digest(path.read_bytes()))
        self.assertEqual(again["status"], "AWAIT_AUTHOR_REVIEW", again)
        self.assertFalse((self.root/"chapters/beta.draft.md").exists())

    def test_source_domain_error_stops_before_target_draft(self):
        class SourceFailure(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt)
                if req["role"] == "source_evidence_review":
                    self.calls.append(req["role"])
                    report = reader_report(req["payload"])
                    report["source_correctness"] = {"verdict": "RESEARCH_MORE", "rationale": "Source rule remains disputed."}
                    return response(self, json.dumps(report))
                return super().generate(instructions, prompt, max_output_tokens)
        model = SourceFailure(clean=True)
        _, result = self.run_model(model)
        self.assertEqual(result["status"], "BLOCKED_QUALITY_UNRESOLVED", result)
        self.assertIn("source_learning_revise", model.calls)
        self.assertNotIn("draft", model.calls)
        self.assertFalse((self.root/"book.md").exists())

    def test_source_major_cannot_disappear_by_rereviewing_unchanged_learning(self):
        class SourceClaim(ScriptedModel):
            source_reviews = 0
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt)
                if req["role"] == "source_evidence_review":
                    self.source_reviews += 1; self.calls.append(req["role"])
                    report = reader_report(req["payload"])
                    if self.source_reviews == 1:
                        report["source_correctness"] = {"verdict": "RESEARCH_MORE", "rationale": "Actual source rule remains wrong."}
                    return response(self, json.dumps(report))
                return super().generate(instructions, prompt, max_output_tokens)
        model = SourceClaim(clean=True)
        _, result = self.run_model(model)
        self.assertEqual(result["status"], "BLOCKED_QUALITY_UNRESOLVED", result)
        self.assertIn("SOURCE_REPAIR_WITHOUT_SUBSTANTIVE_CHANGE", result["failure"]["message"])
        self.assertEqual(model.source_reviews, 1)
        self.assertNotIn("draft", model.calls)

    def test_new_reader_major_cannot_be_downgraded_to_a_previous_note(self):
        self.cfg["chapters"].append({"artifact_id": "beta", "title": "Another chapter"})
        class NewReaderMajor(ScriptedModel):
            beta_reads = 0
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt); role, payload = req["role"], req["payload"]
                if role == "reader_source_review":
                    report = reader_report(payload)
                    if payload["chapter_id"] == "beta":
                        self.beta_reads += 1
                        if self.beta_reads == 2:
                            report["findings"] = [{"code": "READER_PREREQUISITE_ASSUMED", "severity": "MAJOR",
                                "status": "OPEN", "paragraph": 2, "quote": payload["manuscript"].split("\n\n")[1],
                                "reason": "A newly exposed prerequisite has no explanation."}]
                            report["reader_checks"][0].update(verdict="REWORK", rationale="Unexplained prerequisite.")
                    self.calls.append(role); return response(self, json.dumps(report))
                if role == "review":
                    self.calls.append(role)
                    return response(self, json.dumps({"findings": [
                        {"id": "alpha_major", "artifact_id": "alpha", "kind": "model_review", "severity": "MAJOR",
                         "status": "OPEN", "issue": "Add a causal mechanism", "evidence": "The process is missing.", "paragraph": 2},
                        {"id": "beta_note", "artifact_id": "beta", "kind": "computable", "severity": "NOTE",
                         "status": "KEEP", "issue": "Keep valid arithmetic", "evidence": "Correct calculation.",
                         "reason": "Preserve sound text.", "paragraph": 2, "assertion": {"op": "not_contains", "value": "ERROR"}}
                    ]}))
                if role == "revise":
                    self.calls.append(role)
                    return response(self, CORRECT + "\nCount each disjoint pair once; this is the independent causal mechanism.\n")
                if role == "recheck":
                    self.calls.append(role)
                    return response(self, json.dumps({"findings": [
                        {"id": "alpha_major", "status": "CLOSED", "paragraph": 2, "evidence": "Mechanism added."},
                        {"id": "beta_note", "status": "KEEP", "paragraph": 2, "evidence": "Still correct.", "reason": "Retain."}
                    ]}))
                return super().generate(instructions, prompt, max_output_tokens)
        model = NewReaderMajor(clean=True)
        obj = loop.WritingLoop(self.root, self.cfg, model=model)
        obj.write("chapters/alpha.md", CORRECT); obj.write("chapters/beta.md", CORRECT)
        with self.assertRaisesRegex(loop.Blocked, "BLOCKED_QUALITY_UNRESOLVED_NEW_READER_MAJOR_beta"):
            obj.review_cycle("cross", {"alpha": "chapters/alpha.md", "beta": "chapters/beta.md"})
        saved = json.loads((self.root/"reviews/cross.new_reader_findings.1.beta.json").read_text())
        self.assertTrue(any(f["severity"] == "MAJOR" and f["status"] == "OPEN" for f in saved))
        self.assertFalse((self.root/"book.md").exists())

    def test_failed_reviewer_call_is_never_empty_automatic_success(self):
        class MissingReviewer(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                if json.loads(prompt)["role"] == "reader_source_review":
                    raise RuntimeError("fixture review endpoint failed")
                return super().generate(instructions, prompt, max_output_tokens)
        _, result = self.run_model(MissingReviewer(clean=True))
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertFalse((self.root/"book.md").exists())

    def reader_failure_model(self, repair):
        class ReaderFailure(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt); p = req["payload"]
                if req["role"] == "reader_source_review":
                    self.calls.append(req["role"])
                    report = reader_report(p)
                    report["findings"] = [{"code": "READER_PREREQUISITE_ASSUMED", "severity": "MAJOR", "status": "OPEN",
                        "paragraph": 2, "quote": p["manuscript"].split("\n\n")[1],
                        "reason": "Fixture reader cannot reconstruct the actors and choices."}]
                    return response(self, json.dumps(report))
                if req["role"] == "revise":
                    self.calls.append(req["role"])
                    return response(self, p["chapter"].replace(".", "!") if repair == "punctuation" else p["chapter"])
                return super().generate(instructions, prompt, max_output_tokens)
        return ReaderFailure(clean=True)

    def test_reader_major_unchanged_body_is_blocked(self):
        _, result = self.run_model(self.reader_failure_model("unchanged"))
        self.assertEqual(result["status"], "BLOCKED_QUALITY_UNRESOLVED", result)
        self.assertFalse((self.root/"book.md").exists())

    def test_reader_major_punctuation_only_is_not_real_rework(self):
        _, result = self.run_model(self.reader_failure_model("punctuation"))
        self.assertEqual(result["status"], "BLOCKED_QUALITY_UNRESOLVED", result)
        self.assertIn("PUNCTUATION_ONLY", result["failure"]["message"])

    def test_unknown_module_or_unexecuted_e23_is_not_reported_active(self):
        self.cfg["modules"]["invented_policy"] = True
        with self.assertRaisesRegex(loop.Blocked, "UNSUPPORTED_MODULE"):
            self.run_model()
        del self.cfg["modules"]["invented_policy"]
        self.cfg["modules"]["e23"] = True
        with self.assertRaisesRegex(loop.Blocked, "E23_REQUESTED_BUT_PREPROCESS"):
            self.run_model()

    def test_correct_template_free_chapter_passes_without_rewrite(self):
        model = ScriptedModel(clean=True)
        _, result = self.run_model(model)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertNotIn("revise", model.calls)
        self.assertNotIn("source_learning_revise", model.calls)
        self.assertNotIn("restore_independent_value", model.calls)

    def test_shortening_independent_loss_calls_real_body_restoration(self):
        unique = "The two actors use different baskets, so equal totals alone do not establish interchangeable choices. " * 8
        original = CORRECT.replace("2 + 2 = 4,", "2 + 2 = 4, ERROR") + "\n" + unique + "\n"
        class Loss(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt); p = req["payload"]
                if req["role"] == "draft": self.calls.append("draft"); return response(self, original)
                if req["role"] == "content_loss_review":
                    self.calls.append("content_loss_review")
                    missing = unique.strip() not in p["candidate"]
                    return response(self, json.dumps({"units": [{"baseline_quote": unique.strip(),
                        "classification": "INDEPENDENT_VALUE_LOST" if missing else "MOVED_WITH_EVIDENCE",
                        "candidate_quote": unique.strip() if not missing else "",
                        "rationale": "Fixture tracks an independent counterexample's actual words."}]}))
                if req["role"] == "restore_independent_value":
                    self.calls.append("restore_independent_value")
                    return response(self, original.replace(" ERROR", ""))
                return super().generate(instructions, prompt, max_output_tokens)
        model = Loss()
        _, result = self.run_model(model)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertIn("restore_independent_value", model.calls)
        self.assertIn(unique.strip(), (self.root/"book.md").read_text())

    def test_stable_channel_requires_real_current_selection_not_a_flag(self):
        self.cfg["channel"] = "STABLE"
        with self.assertRaisesRegex(loop.Blocked, "STABLE_WRITER_(NOT_FORMALLY_SELECTED|PROJECT_PROTOCOL_PIN_MISMATCH)"):
            self.run_model()


if __name__ == "__main__": unittest.main()
