#!/usr/bin/env python3
"""Engineering fixtures only; no real model, book-quality or human acceptance claim."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e18_loop_tested", TOOLS / "writing_loop_experimental.py")
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)

DRAFT = "# Arithmetic fixture\n\nA calculation claims 2 + 2 = 5. ERROR\n\nA reader needs a justified decision.\n"
CORRECT = "# Arithmetic fixture\n\nA calculation gives 2 + 2 = 4, verified by counting two pairs.\n\nA reader needs a justified decision.\n"


class ScriptedModel:
    is_live = False
    output_limit_enforced = False

    def __init__(self, repair="real", clean=False, usage=None, change_model=False, empty_review=False):
        self.repair, self.clean, self.usage = repair, clean, usage
        self.change_model, self.empty_review = change_model, empty_review
        self.calls = []

    def generate(self, instructions, prompt, max_output_tokens=6000):
        req = json.loads(prompt)
        role, p = req["role"], req["payload"]
        self.calls.append(role)
        if role in ("research", "select_direction"):
            text = "# Engineering fixture\n\nCompare calculation errors against actual prose."
        elif role == "draft":
            text = CORRECT if self.clean else DRAFT
        elif role == "review":
            rows = []
            if not self.empty_review:
                for art, prose in p["manuscripts"].items():
                    bad = "ERROR" in prose
                    rows.append({"id": "f_" + art, "artifact_id": art, "kind": "computable",
                        "severity": "MAJOR" if bad else "NOTE", "status": "OPEN" if bad else "KEEP",
                        "issue": "Remove the literal computational error marker",
                        "evidence": "Paragraph two contains the checked calculation.",
                        "reason": "The actual calculation is correct and should be kept.",
                        "paragraph": 2,
                        "assertion": {"op": "not_contains", "value": "ERROR"}})
            text = json.dumps({"findings": rows})
        elif role == "revise":
            if self.repair == "real":
                text = CORRECT
            elif self.repair == "whitespace":
                text = p["chapter"].replace("2 + 2", "2  +  2") + "\n\n"
            else:
                text = p["chapter"]
        elif role == "recheck":
            text = json.dumps({"findings": [
                {"id": f["id"], "status": "CLOSED", "paragraph": 2,
                 "evidence": "Scripted claim of closure; guard must inspect actual bytes."}
                for f in p["frozen_findings"]]})
        elif role == "front_matter":
            text = "# Preface\n\nThis is an engineering fixture, not a book experiment."
        elif role == "afterword":
            text = "# Afterword\n\nNo human or independent quality review has occurred."
        else:
            raise AssertionError("unexpected role " + role)
        usage = self.usage if self.usage is not None else {"input_tokens": 10, "output_tokens": 10}
        model = "fixture-model-2" if self.change_model and len(self.calls) > 1 else "fixture-model"
        return loop.transport.ModelResult("fixture-" + str(len(self.calls)), model, text,
                                          usage, "scripted_fixture")


def config(root, guard="on"):
    source = root / "sources/material.md"
    source.parent.mkdir(parents=True)
    source.write_text("Public engineering fixture only: two pairs contain four objects.\n", encoding="utf-8")
    protocols = {name: {"version": version, "commit": "1"*40, "spec_sha": "2"*40}
                 for name, version in (("deepwrite", "v0.1"), ("wish_delivery", "v7.6"))}
    return {"project_id": "e18-engineering-fixture", "model": "fixture-model",
        "working_title": "Engineering fixture", "wish": "Explain a verifiable arithmetic decision.",
        "adapter": "fixture", "guard": guard, "token_budget": 10000,
        "per_call_output_tokens": 1000, "max_revision_rounds": 1,
        "chapters": [{"artifact_id": "alpha", "title": "Arithmetic"}],
        "sources": [{"path": "sources/material.md", "sha256": loop.digest(source.read_bytes())}],
        "pins": {"project_id": "e18-engineering-fixture", "protocols": protocols,
            "channel": "CANDIDATE_OPT_IN", "modules": [{"id": "e18_loop", "commit": "3"*40}]},
        "channel": "CANDIDATE_OPT_IN", "module_policy": {"e18_loop": "CANDIDATE"},
        "modules": {"e18_loop": True}, "module_commits": {"e18_loop": "3"*40}}


class WritingLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="e18-engineering-")
        self.base = Path(self.tmp.name)
        self.root = self.base / "project"
        self.cfg = config(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def run_model(self, model=None):
        obj = loop.WritingLoop(self.root, self.cfg, model=model or ScriptedModel())
        result = obj.run()
        return obj, result

    def prepare_blind_fixture(self):
        self.cfg["channel"] = "SHADOW"
        self.cfg["pins"]["channel"] = "SHADOW"
        original = self.cfg["sources"][0]
        self.cfg["insight_origin"] = {
            "schema": "deepwrite/insight-origin-blind/v0.1",
            "mode": "BLIND_PRE_REVEAL",
            "experiment_id": "fixture_no_author_reveal_001",
            "author_thesis_disclosed": False,
            "neutral_wish_sha256": loop.digest(self.cfg["wish"].encode("utf-8")),
            "source_roles": [dict(original, role="SOURCE_DOMAIN")]
        }

    def blind_model(self, faulty=False):
        class Model(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt)
                if req["role"] != "insight_origin":
                    return super().generate(instructions, prompt, max_output_tokens)
                self.calls.append("insight_origin")
                quote = "two pairs contain four objects"
                source = "sources/material.md"
                frames = [{
                    "id": "L" + str(i),
                    "default_question": "How should someone apply the existing arithmetic convention " + str(i),
                    "alternative_question": "How would a different decision sequence change the evaluation " + str(i),
                    "decision_before": "Choose the ordinary calculation procedure for test " + str(i),
                    "decision_after": "Change the procedure after testing assumptions for test " + str(i),
                    "source_falsifier": "A test that yields equal results for all feasible actions under fixed assumptions",
                    "source_anchor": {"path": source, "quote": quote},
                } for i in range(1, 4)]
                if faulty:
                    frames[1]["source_anchor"]["quote"] = "The nonexistent author theory was proven"
                payload = {"origin_status": "MODEL_PROPOSAL_UNVERIFIED", "lenses": frames}
                return loop.transport.ModelResult(
                    "fixture-insight-origin", "fixture-model", json.dumps(payload),
                    {"input_tokens": 10, "output_tokens": 10}, "scripted_fixture")
        return Model(clean=True)

    def test_blind_origin_is_frozen_before_research_and_never_self_certified(self):
        self.prepare_blind_fixture()
        model = self.blind_model()
        _, result = self.run_model(model)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertEqual(model.calls[0], "insight_origin")
        self.assertEqual(model.calls[1], "research")
        self.assertTrue((self.root / "insight/blind_origin_model_proposals.json").exists())
        audit = json.loads((self.root / "insight/blind_origin_structural_audit.json").read_text())
        self.assertEqual(audit["semantic_novelty"], "UNVERIFIED")
        self.assertEqual(audit["human_blind_review"], "NOT_RUN")
        self.assertTrue((self.root / "calls/blind_origin.request.json").exists())
        research = json.loads((self.root / "calls/research.request.json").read_text())
        self.assertIn("blind_origin_frozen", research["payload"])
        self.assertTrue((self.root / "book.md").exists())

    def test_fabricated_blind_candidate_blocks_before_writing(self):
        self.prepare_blind_fixture()
        model = self.blind_model(faulty=True)
        _, result = self.run_model(model)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertIn("BLIND_ORIGIN_INVALID_MODEL_PROPOSALS", result["failure"]["message"])
        self.assertEqual(model.calls, ["insight_origin"])
        self.assertFalse((self.root / "research.md").exists())
        self.assertFalse((self.root / "book.md").exists())
        self.assertTrue((self.root / "insight/blind_origin_model_proposals.json").exists())
        audit = json.loads((self.root / "insight/blind_origin_structural_audit.json").read_text())
        self.assertIn("UNVERIFIED_SOURCE_ANCHOR_1", audit["errors"])

    def test_blind_declared_leak_fails_before_model_initialization(self):
        self.prepare_blind_fixture()
        self.cfg["insight_origin"]["source_roles"][0]["role"] = "AUTHOR_THESIS"
        with self.assertRaisesRegex(ValueError, "BLIND_ORIGIN_SOURCE_ROLE_DISALLOWED"):
            loop.WritingLoop(self.root, self.cfg, model=self.blind_model())

    def test_real_file_rewrite_diff_package_and_checkpoint(self):
        obj, result = self.run_model()
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertIn("ERROR", (self.root/"chapters/alpha.draft.md").read_text())
        self.assertNotIn("ERROR", (self.root/"chapters/alpha.alpha.r1.md").read_text())
        patch = (self.root/"diffs/alpha.alpha.1.patch").read_text()
        self.assertIn("-A calculation claims", patch)
        self.assertIn("+A calculation gives", patch)
        record = json.loads((self.root/"reviews/alpha.1.json").read_text())
        self.assertEqual(record["guard"]["status"], "PASS_STRUCTURAL_ONLY")
        package = json.loads((self.root/"package.json").read_text())
        self.assertEqual(package["sha256"], loop.digest((self.root/"book.md").read_bytes()))
        self.assertEqual(result["book_sha256"], package["sha256"])
        self.assertEqual(result["tokens"], 20 * len(obj.state["calls"]))
        self.assertEqual(result["quality"], "UNVERIFIED")
        self.assertEqual(result["fair_B0_B1"], "UNVERIFIED")
        receipt = result["checkpoint"]
        checked = loop.resume_checker.check(Path(receipt["path"]), receipt["manifest_sha256"],
                        Path(receipt["requirements"]), receipt["requirements_sha256"])
        self.assertEqual(checked["status"], loop.resume_checker.PASS)

    def test_false_closed_unchanged_prose_is_blocked(self):
        _, result = self.run_model(ScriptedModel(repair="unchanged"))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("REVIEW_STILL_OPEN", result["failure"]["message"])
        self.assertFalse((self.root/"book.md").exists())
        self.assertTrue((self.root/"calls/alpha_recheck_1.response.json").exists())
        record = json.loads((self.root/"reviews/alpha.1.json").read_text())
        self.assertEqual(record["guard"]["status"], "HOLD")

    def test_whitespace_only_fake_repair_is_blocked(self):
        _, result = self.run_model(ScriptedModel(repair="whitespace"))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse((self.root/"book.md").exists())
        self.assertNotEqual((self.root/"chapters/alpha.draft.md").read_bytes(),
                            (self.root/"chapters/alpha.alpha.r1.md").read_bytes())

    def test_guard_off_reproduces_false_close_without_claiming_quality(self):
        self.cfg["guard"] = "off"
        _, result = self.run_model(ScriptedModel(repair="unchanged"))
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertIn("ERROR", (self.root/"book.md").read_text())
        self.assertEqual(result["quality"], "UNVERIFIED")
        record = json.loads((self.root/"reviews/alpha.1.json").read_text())
        self.assertEqual(record["guard"]["status"], "BYPASSED_BASELINE_ARM")

    def test_justified_keep_does_not_force_rewrite(self):
        model = ScriptedModel(clean=True)
        _, result = self.run_model(model)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertNotIn("revise", model.calls)
        self.assertNotIn("recheck", model.calls)
        self.assertIn("2 + 2 = 4", (self.root/"book.md").read_text())

    def test_cross_chapter_rewrite_records_model_review_not_machine_semantics(self):
        self.cfg["chapters"].append({"artifact_id": "beta", "title": "Distinct contribution"})
        class CrossModel(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt)
                p = req["payload"]
                if req["role"] == "review" and len(p["manuscripts"]) > 1:
                    self.calls.append("cross_review")
                    text = json.dumps({"findings": [
                        {"id": "cross_alpha", "artifact_id": "alpha", "kind": "model_review",
                         "severity": "NOTE", "status": "KEEP", "issue": "Retain arithmetic chapter",
                         "evidence": "Its paragraph two supplies the calculation.", "paragraph": 2,
                         "reason": "Its contribution remains useful."},
                        {"id": "cross_beta", "artifact_id": "beta", "kind": "model_review",
                         "severity": "MAJOR", "status": "OPEN", "issue": "Duplicate chapter contribution",
                         "evidence": "Its paragraph two repeats alpha without a new decision.", "paragraph": 2}
                    ]})
                elif req["role"] == "revise" and any(f["id"] == "cross_beta" for f in p["frozen_findings"]):
                    self.calls.append("cross_revise")
                    text = "# A separate decision\n\nCheck the assumptions before trusting the calculated answer.\n\nThis chapter adds a different reader action.\n"
                elif req["role"] == "recheck" and any(f["id"].startswith("cross_") for f in p["frozen_findings"]):
                    self.calls.append("cross_recheck")
                    text = json.dumps({"findings": [
                        {"id": "cross_alpha", "status": "KEEP", "paragraph": 2,
                         "evidence": "The original arithmetic evidence is still present.",
                         "reason": "Preserve the correct original."},
                        {"id": "cross_beta", "status": "CLOSED", "paragraph": 2,
                         "evidence": "The revised paragraph gives an assumption-checking action."}
                    ]})
                else:
                    return super().generate(instructions, prompt, max_output_tokens)
                return loop.transport.ModelResult("fixture-special-"+str(len(self.calls)),
                     "fixture-model", text, {"input_tokens":10,"output_tokens":10}, "scripted_fixture")
        _, result = self.run_model(CrossModel(clean=True))
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertTrue((self.root/"chapters/beta.cross.r1.md").exists())
        self.assertIn("Check the assumptions", (self.root/"book.md").read_text())
        record = json.loads((self.root/"reviews/cross.1.json").read_text())
        self.assertEqual(record["guard"]["status"], "PASS_STRUCTURAL_ONLY")
        self.assertEqual(record["guard"]["semantic_status"], "MODEL_REVIEW_REQUIRED")
        self.assertEqual(json.loads((self.root/"run_state.json").read_text())["human_acceptance"], "NOT_RUN")

    def test_frozen_draft_replay_reads_real_baseline_and_preserves_it(self):
        source = self.root/"sources/material.md"
        source.write_text(DRAFT)
        self.cfg["sources"][0]["sha256"] = loop.digest(source.read_bytes())
        self.cfg["run_mode"] = "replay_frozen_drafts"
        self.cfg["replay_drafts"] = {"alpha": "sources/material.md"}
        self.cfg["known_findings"] = [{"id": "known_arithmetic", "artifact_id": "alpha",
            "kind": "computable", "severity": "MAJOR", "status": "OPEN",
            "issue": "Caller-frozen known literal defect", "evidence": "Original paragraph has ERROR.",
            "paragraph": 2, "assertion": {"op": "not_contains", "value": "ERROR"}}]
        model = ScriptedModel()
        obj, result = self.run_model(model)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertEqual(obj.state["draft_origin"], "FROZEN_BASELINE_REPLAY_NOT_FRESH_B0_B1")
        self.assertEqual(source.read_text(), DRAFT)
        self.assertEqual((self.root/"chapters/alpha.draft.md").read_text(), DRAFT)
        self.assertNotIn("ERROR", (self.root/"chapters/alpha.alpha.r1.md").read_text())
        self.assertNotIn("research", model.calls)
        self.assertNotIn("select_direction", model.calls)
        self.assertNotIn("draft", model.calls)
        frozen = json.loads((self.root/"reviews/alpha.frozen.json").read_text())
        self.assertIn("known_arithmetic", {f["id"] for f in frozen})

    def test_fresh_mode_rejects_frozen_draft_replay_inputs(self):
        self.cfg["replay_drafts"] = {"alpha": "sources/material.md"}
        with self.assertRaisesRegex(loop.Blocked, "REPLAY_INPUT_FORBIDDEN"):
            loop.WritingLoop(self.root, self.cfg, model=ScriptedModel())

    def test_recheck_new_major_is_saved_and_blocks_delivery(self):
        class NewMajor(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                result = super().generate(instructions, prompt, max_output_tokens)
                if json.loads(prompt)["role"] != "recheck":
                    return result
                obj = json.loads(result.text)
                obj["new_findings"] = [{"artifact_id": "alpha", "severity": "MAJOR",
                    "issue": "A newly noticed unsupported inference", "evidence": "Paragraph three.",
                    "paragraph": 3}]
                return loop.transport.ModelResult(result.response_id, result.model, json.dumps(obj),
                                                   result.usage, result.provider_kind)
        _, result = self.run_model(NewMajor())
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("NEW_MAJOR_FINDINGS_HOLD", result["failure"]["message"])
        self.assertTrue((self.root/"reviews/alpha.new_findings.1.json").exists())
        self.assertFalse((self.root/"book.md").exists())

    def test_new_minor_is_retained_without_being_misread_as_a_closeout_record(self):
        class NewMinor(ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                result = super().generate(instructions, prompt, max_output_tokens)
                if json.loads(prompt)["role"] != "recheck":
                    return result
                obj = json.loads(result.text)
                obj["new_findings"] = [{"artifact_id": "alpha", "severity": "MINOR",
                    "issue": "Potentially smoother transition", "evidence": "Paragraph three.",
                    "paragraph": 3}]
                return loop.transport.ModelResult(result.response_id, result.model, json.dumps(obj),
                                                   result.usage, result.provider_kind)
        _, result = self.run_model(NewMinor())
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertTrue((self.root/"reviews/alpha.new_findings.1.json").exists())

    def test_dotdot_cannot_hide_project_inside_code_repository(self):
        target = TOOLS.parent/"not_created_e18"/".."/"forbidden_e18_output"
        with self.assertRaisesRegex(loop.Blocked, "OUTSIDE_CODE_REPOSITORY"):
            loop.WritingLoop(target, self.cfg, model=ScriptedModel())
        self.assertFalse((TOOLS.parent/"forbidden_e18_output").exists())

    def test_ancestor_symlink_is_rejected_before_resolving(self):
        actual = self.base/"actual"
        actual.mkdir()
        alias = self.base/"alias"
        alias.symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(loop.Blocked, "SYMLINK_PROJECT_ROOT_OR_ANCESTOR"):
            loop.WritingLoop(alias/"project", self.cfg, model=ScriptedModel())

    def test_crash_after_response_before_transport_cannot_be_cached_as_success(self):
        class PowerLoss(BaseException):
            pass
        first = ScriptedModel()
        obj = loop.WritingLoop(self.root, self.cfg, model=first)
        old_write = obj.write
        def interrupted_write(relative, data):
            old_write(relative, data)
            if relative == "calls/research.response.json":
                raise PowerLoss()
        obj.write = interrupted_write
        with self.assertRaises(PowerLoss):
            obj.run()
        state_sha = loop.digest((self.root/"run_state.json").read_bytes())
        second = ScriptedModel()
        resumed = loop.WritingLoop(self.root, self.cfg, model=second, expected_state_sha=state_sha).run()
        self.assertEqual(resumed["status"], "BLOCKED")
        self.assertIn("INCOMPLETE_CALL_COMMIT", resumed["failure"]["message"])
        self.assertEqual(second.calls, [])
        self.assertFalse((self.root/"book.md").exists())

    def test_cross_revision_cannot_reintroduce_earlier_closed_computable_error(self):
        class Regression(ScriptedModel):
            review_turn = 0
            def generate(self, instructions, prompt, max_output_tokens=6000):
                req = json.loads(prompt)
                if req["role"] == "review":
                    self.review_turn += 1
                    if self.review_turn == 2:
                        self.calls.append("cross_review")
                        text = json.dumps({"findings": [{"id": "cross_change", "artifact_id": "alpha",
                            "kind": "model_review", "severity": "MAJOR", "status": "OPEN",
                            "issue": "Give a different perspective", "evidence": "Paragraph two needs a new action.",
                            "paragraph": 2}]})
                        return loop.transport.ModelResult("cross-review", "fixture-model", text,
                            {"input_tokens":10,"output_tokens":10}, "scripted_fixture")
                if req["role"] == "revise" and any(f["id"] == "cross_change" for f in req["payload"]["frozen_findings"]):
                    self.calls.append("cross_revise")
                    return loop.transport.ModelResult("cross-revision", "fixture-model", DRAFT,
                        {"input_tokens":10,"output_tokens":10}, "scripted_fixture")
                return super().generate(instructions, prompt, max_output_tokens)
        _, result = self.run_model(Regression())
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("HISTORICAL_FINDING_REGRESSION", result["failure"]["message"])
        record = json.loads((self.root/"reviews/final_historical_findings.json").read_text())
        self.assertIn("COMPUTABLE_REGRESSION", {f["reason"] for f in record["failures"]})
        self.assertFalse((self.root/"book.md").exists())

    def test_missing_actual_usage_blocks_retains_response(self):
        obj, result = self.run_model(ScriptedModel(usage={}))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("MISSING_REAL_TOKEN_USAGE", result["failure"]["message"])
        self.assertEqual(obj.state["usage_uncertain_calls"], ["research"])
        self.assertTrue((self.root/"calls/research.response.json").exists())
        self.assertEqual(obj.state["calls"], {})

    def test_budget_overrun_retains_and_accounts_consumption(self):
        self.cfg["token_budget"] = 15
        obj, result = self.run_model()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(obj.state["tokens"], 20)
        self.assertIn("TOKEN_BUDGET_EXCEEDED", result["failure"]["message"])
        self.assertTrue((self.root/"calls/research.response.json").exists())

    def test_model_switch_blocks_after_charging_actual_usage(self):
        obj, result = self.run_model(ScriptedModel(change_model=True))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(obj.state["tokens"], 40)
        self.assertIn("MODEL_CHANGED", result["failure"]["message"])

    def test_resume_restores_old_files_without_repeating_successful_calls(self):
        first = ScriptedModel()
        paused = loop.WritingLoop(self.root, self.cfg, model=first, stop_after=4).run()
        self.assertEqual(paused["status"], "PAUSED", paused)
        receipt = paused["checkpoint"]
        restored = self.base / "restored"
        loop.restore_project(receipt["path"], restored, receipt["manifest_sha256"],
                             receipt["requirements"], receipt["requirements_sha256"])
        second = ScriptedModel()
        result = loop.WritingLoop(restored, self.cfg, model=second,
                                  expected_state_sha=receipt["state_sha256"]).run()
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertNotIn("research", second.calls)
        self.assertNotIn("select_direction", second.calls)
        self.assertNotIn("draft", second.calls)
        self.assertNotIn("revise", second.calls)
        self.assertIn("review", second.calls)
        self.assertEqual((restored/"chapters/alpha.draft.md").read_bytes(),
                         (self.root/"chapters/alpha.draft.md").read_bytes())

    def test_resume_requires_external_state_hash(self):
        loop.WritingLoop(self.root, self.cfg, model=ScriptedModel(), stop_after=1).run()
        with self.assertRaisesRegex(loop.Blocked, "EXTERNAL_STATE_SHA"):
            loop.WritingLoop(self.root, self.cfg, model=ScriptedModel())

    def test_resume_rejects_tampered_actual_file(self):
        paused = loop.WritingLoop(self.root, self.cfg, model=ScriptedModel(), stop_after=3).run()
        (self.root/"chapters/alpha.draft.md").write_text("tamper")
        with self.assertRaisesRegex(loop.Blocked, "RESUME_FILE_SHA_MISMATCH"):
            loop.WritingLoop(self.root, self.cfg, model=ScriptedModel(),
                             expected_state_sha=paused["checkpoint"]["state_sha256"])

    def test_empty_review_is_not_a_closed_book(self):
        _, result = self.run_model(ScriptedModel(empty_review=True))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("EMPTY_REVIEW", result["failure"]["message"])
        self.assertFalse((self.root/"book.md").exists())

    def test_failed_call_not_retried_on_resume(self):
        class Broken(ScriptedModel):
            def generate(self, *args):
                self.calls.append("failed")
                raise RuntimeError("simulated network loss")
        first = Broken()
        obj, result = self.run_model(first)
        self.assertEqual(result["status"], "BLOCKED")
        second = ScriptedModel()
        again = loop.WritingLoop(self.root, self.cfg, model=second,
                                expected_state_sha=result["state_sha256"]).run()
        self.assertEqual(again["status"], "BLOCKED")
        self.assertEqual(second.calls, [])
        self.assertTrue((self.root/"calls/research.failure.json").exists())

    def test_completed_resume_does_not_call_model_or_repackage(self):
        _, result = self.run_model()
        second = ScriptedModel()
        state_sha = result["checkpoint"]["state_sha256"]
        again = loop.WritingLoop(self.root, self.cfg, model=second, expected_state_sha=state_sha).run()
        self.assertEqual(again["resume"], "ALREADY_COMPLETE_NO_MODEL_CALL")
        self.assertEqual(second.calls, [])

    def test_tool_contamination_blocks_and_survives_resume(self):
        class ToolModel(ScriptedModel):
            def generate(self, *args):
                result = super().generate(*args)
                self.last_transport = {"provider_response": {"output": [{"type": "web_search_call"}]}}
                return result
        obj, result = self.run_model(ToolModel())
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(obj.state["tokens"], 20)
        self.assertIn("MODEL_TOOLS_USED", result["failure"]["message"])
        second = ScriptedModel()
        again = loop.WritingLoop(self.root, self.cfg, model=second,
                                expected_state_sha=result["state_sha256"]).run()
        self.assertEqual(again["status"], "BLOCKED")
        self.assertEqual(second.calls, [])
        self.assertIn("MODEL_TOOLS_USED", again["failure"]["message"])

    def test_missing_credentials_is_explicit_auth_block(self):
        class NoAuth(ScriptedModel):
            def generate(self, *args):
                raise loop.transport.MissingCredential("OPENAI_API_KEY is absent")
        _, result = self.run_model(NoAuth())
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["failure"]["message"], "BLOCKED_MODEL_AUTH")
        self.assertTrue((self.root/"calls/research.failure.json").exists())

    def test_output_cap_rejection_is_charged(self):
        self.cfg["per_call_output_tokens"] = 5
        obj, result = self.run_model()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(obj.state["tokens"], 20)
        self.assertIn("OUTPUT_CAP_EXCEEDED", result["failure"]["message"])

    def test_corrupt_restore_source_is_rejected(self):
        paused = loop.WritingLoop(self.root, self.cfg, model=ScriptedModel(), stop_after=3).run()
        receipt = paused["checkpoint"]
        # Corrupt one actual saved file, preserving the external expected manifest SHA.
        target = Path(receipt["path"])/"files/chapters/alpha.draft.md"
        target.write_bytes(b"corrupt")
        with self.assertRaises((loop.Blocked, ValueError)):
            loop.restore_project(receipt["path"], self.base/"badrestore", receipt["manifest_sha256"],
                                 receipt["requirements"], receipt["requirements_sha256"])
        self.assertFalse((self.base/"badrestore").exists())


if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--fixture-output", type=Path)
    args, remaining = parser.parse_known_args()
    if args.fixture_output:
        cfg = config(args.fixture_output)
        result = loop.WritingLoop(args.fixture_output, cfg, model=ScriptedModel()).run()
        receipt = args.fixture_output.parent/(args.fixture_output.name+".fixture-receipt.json")
        receipt.write_bytes(loop.json_bytes(result))
        print(json.dumps({"evidence_kind": "ENGINEERING_FIXTURE_ONLY", "result": result,
                          "receipt_path": str(receipt)}, indent=2))
        raise SystemExit(0 if result["status"] == "ENGINEERING_FIXTURE_ONLY_NOT_LIVE" else 2)
    unittest.main(argv=[sys.argv[0], *remaining])
