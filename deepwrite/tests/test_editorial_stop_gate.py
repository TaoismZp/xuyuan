#!/usr/bin/env python3
"""Deterministic negative tests for the opt-in editorial stop gate.

Engineering checks only. These do not certify literary or reader quality.
"""
import ast
import copy
import importlib.util
import json
import tempfile
from types import SimpleNamespace
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = ROOT / "deepwrite/tools/editorial_stop_gate.py"
SPEC = importlib.util.spec_from_file_location("editorial_stop_gate_tested", GUARD_PATH)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

ART = "ch03"
TEXT = "# 章节\n\n股票跌到了七十元，他看到这个价格便立即投入全部现金。\n\n这里是另一段。"


def finding(kind="EX_ANTE_CAUSAL_ERROR", *, id="bad_path", art=ART,
            quote="股票跌到了七十元", status="OPEN", severity="MAJOR"):
    return {
        "id": id, "artifact_id": art, "kind": "model_review",
        "status": status, "severity": severity, "paragraph": 2,
        "issue": "The writer chose a future fill as if already known.",
        "evidence": "At the initial decision, no future price is known.",
        "edit_case": {
            "classification": kind, "baseline_quote": quote,
            "reader_harm": "A first-time reader could mistake hindsight for a permitted earlier decision.",
            "minimal_remedy": "Separate the original commitment from what is known when the price arrives.",
            "regression_risk": "Additional qualification might obscure the chapter's central literary conflict."
        }
    }


class EditorialStopGateTests(unittest.TestCase):
    def audit(self, findings, history=None, manuscripts=None):
        return gate.audit_initial(findings, manuscripts or {ART: TEXT}, history)

    def test_real_ex_ante_defect_is_one_repair_candidate(self):
        output = self.audit([finding()])
        self.assertEqual(output["status"], "PASS_PROPOSALS_ONLY")
        self.assertEqual(output["decisions"][0]["decision"], "ALLOW_ONE_EVIDENCED_REPAIR")
        self.assertEqual(len(output["new_history"]), 1)
        self.assertEqual(output["quality_improvement"], "UNVERIFIED")

    def test_source_domain_causal_gap_can_be_proposed_with_evidence(self):
        output = self.audit([finding("SOURCE_MECHANISM_MISSING")])
        self.assertEqual(output["status"], "PASS_PROPOSALS_ONLY")

    def test_reader_causal_gap_can_be_proposed_with_evidence(self):
        output = self.audit([finding("READER_CAUSAL_GAP")])
        self.assertEqual(output["status"], "PASS_PROPOSALS_ONLY")

    def test_optional_style_cannot_force_rewrite(self):
        result = self.audit([finding("STYLE_ONLY")])
        self.assertEqual(result["status"], "PASS_PROPOSALS_ONLY")
        self.assertEqual(result["findings"][0]["status"], "KEEP")
        self.assertTrue(result["findings"][0]["reason"])
        self.assertEqual(result["new_history"], {})

    def test_no_p0_p1_p2_does_not_force_an_iteration(self):
        row = finding()
        row["severity"], row["status"], row["edit_case"] = "NOTE", "KEEP", None
        result = self.audit([row])
        self.assertEqual(result["status"], "PASS_PROPOSALS_ONLY")
        self.assertEqual(result["new_history"], {})
        self.assertEqual(result["findings"][0]["status"], "KEEP")

    def test_hallucinated_quote_is_refused(self):
        result = self.audit([finding(quote="该段落根本没有的八个字")])
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["holds"][0]["reason"], "BASELINE_QUOTE_NOT_IN_LOCATED_PARAGRAPH")

    def test_unique_original_quote_can_repair_wrong_paragraph_number(self):
        row = finding()
        row["paragraph"] = 1
        result = self.audit([row])
        self.assertEqual(result["status"], "PASS_PROPOSALS_ONLY")
        self.assertEqual(result["findings"][0]["reported_paragraph"], 1)
        self.assertEqual(result["findings"][0]["paragraph"], 2)

    def test_wrong_paragraph_with_nonunique_quote_holds(self):
        row = finding()
        row["paragraph"] = 1
        self.assertEqual(self.audit([row], manuscripts={ART: TEXT + "\n\n股票跌到了七十元"})["status"], "HOLD")

    def test_missing_required_justification_holds_not_keeps(self):
        row = finding()
        del row["edit_case"]
        result = self.audit([row])
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["findings"][0]["status"], "OPEN")

    def test_empty_reader_harm_holds(self):
        row = finding()
        row["edit_case"]["reader_harm"] = "nice"
        self.assertEqual(self.audit([row])["status"], "HOLD")

    def test_unclassified_issue_holds(self):
        self.assertEqual(self.audit([finding("NONSTANDARD_CLASS")])["status"], "HOLD")

    def test_repeat_same_issue_is_not_a_new_discovery(self):
        first = self.audit([finding()])
        result = self.audit([finding(id="renamed_r32")], first["new_history"])
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["holds"][0]["reason"],
                         "REPEATED_BASELINE_DEFECT_WITHOUT_NEW_INDEPENDENT_EVIDENCE")

    def test_duplicate_same_review_is_not_a_second_repair(self):
        result = self.audit([finding(id="first"), finding(id="second")])
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["holds"][0]["reason"], "DUPLICATE_DEFECT_IN_SAME_REVIEW")

    def test_resume_replays_frozen_review_without_false_churn(self):
        earlier = gate.audit_initial([finding()], {ART: TEXT}, scope="ch03")
        later = gate.audit_initial([finding()], {ART: TEXT}, earlier["new_history"], scope="ch03")
        self.assertEqual(later["status"], "PASS_PROPOSALS_ONLY")
        self.assertEqual(later["decisions"][0]["decision"], "REPLAY_SAME_FROZEN_SCOPE")
        self.assertEqual(later["new_history"], {})

    def test_same_defect_in_new_scope_must_not_evade_stopping(self):
        earlier = gate.audit_initial([finding()], {ART: TEXT}, scope="ch03")
        later = gate.audit_initial([finding()], {ART: TEXT}, earlier["new_history"], scope="cross")
        self.assertEqual(later["status"], "HOLD")
        self.assertEqual(later["holds"][0]["reason"],
                         "REPEATED_BASELINE_DEFECT_WITHOUT_NEW_INDEPENDENT_EVIDENCE")

    def test_distinct_artifact_same_quote_not_false_duplicate(self):
        row = finding(art="ch05")
        result = self.audit([finding(), row], manuscripts={ART: TEXT, "ch05": TEXT})
        self.assertEqual(result["status"], "PASS_PROPOSALS_ONLY")

    def test_model_cannot_bypass_gate_with_reader_prefix(self):
        row = finding(id="reader_ch03_gate")
        row.pop("edit_case")
        result = self.audit([row])
        self.assertEqual(result["status"], "HOLD")

    def test_input_is_not_modified(self):
        rows = [finding("STYLE_ONLY")]
        original = copy.deepcopy(rows)
        self.audit(rows)
        self.assertEqual(rows, original)

    def test_changed_quote_length_cannot_reopen_same_passage(self):
        first = self.audit([finding(quote="股票跌到了七十元，他看到这个价格")])
        later = self.audit([finding(id="renamed", quote="他看到这个价格便立即投入")], first["new_history"])
        self.assertEqual(later["status"], "HOLD")
        self.assertEqual(later["holds"][0]["reason"], "REPEATED_BASELINE_DEFECT_WITHOUT_NEW_INDEPENDENT_EVIDENCE")

    def test_optional_minor_does_not_hitchhike_on_hard_rewrite(self):
        cosmetic = finding("STYLE_ONLY", id="wording", severity="MINOR")
        output = self.audit([finding(), cosmetic])
        self.assertEqual([item["status"] for item in output["findings"]], ["OPEN", "KEEP"])

    def test_corroboration_does_not_silently_downgrade_hard_claim(self):
        output = self.audit([finding()])
        gate.corroborate(output, {"findings": [{"id": "bad_path", "verdict": "PREFERENCE_ONLY",
                        "quote": "股票跌到了七十元", "reason": "No defect has been established by this second reading."}]}, {ART: TEXT})
        self.assertEqual(output["disposition"], "HOLD_UNVERIFIED")

    def test_corroborated_style_disagreement_can_keep_supported_prose(self):
        output = self.audit([finding("READER_CAUSAL_GAP")])
        gate.corroborate(output, {"findings": [{"id": "bad_path", "verdict": "PREFERENCE_ONLY",
                        "quote": "股票跌到了七十元", "reason": "An equally readable formulation is just a preference."}]}, {ART: TEXT})
        self.assertEqual(output["disposition"], "KEEP_NO_CHURN")
        self.assertEqual(output["findings"][0]["status"], "KEEP")

    def test_whitespace_only_rewrite_is_not_quality_gain(self):
        self.assertEqual(gate.verify_edit_result("文字 有 证据", "文 字有证据")["status"],
                         "HOLD_NO_SUBSTANTIVE_CHANGE")

    def test_real_changed_text_still_requires_semantic_recheck(self):
        response = gate.verify_edit_result("旧文字", "加入不同经济条件的新段落")
        self.assertEqual(response["status"], "CHANGED_NEEDS_SEMANTIC_RECHECK")
        self.assertEqual(response["semantic_quality"], "UNVERIFIED")

    def test_malformed_findings_fail_closed(self):
        with self.assertRaises(ValueError):
            self.audit({"findings": [finding()]})

    def test_runtime_really_calls_gate_at_review_and_rewrite(self):
        source = (ROOT / "deepwrite/tools/writing_loop_experimental.py").read_text("utf-8")
        ast.parse(source)
        self.assertIn("self.editorial_stop_guard.audit_initial(", source)
        self.assertIn("self.editorial_stop_guard.verify_edit_result(", source)
        self.assertIn("EDITORIAL_STOP_HOLD_UNGROUNDED_OR_REPEATED_PROPOSAL_", source)
        self.assertIn("EDITORIAL_STOP_HOLD_P2_REWRITE_BUDGET_EXHAUSTED_", source)

    def test_author_opt_in_routes_to_frozen_candidate_contract(self):
        source = (ROOT / "deepwrite/deepwrite.py").read_text("utf-8")
        ast.parse(source)
        self.assertIn("experimental_editorial_stop_gate", source)
        self.assertIn('"editorial_stopping": True', source)
        self.assertIn('channel = "CANDIDATE_OPT_IN"', source)
        self.assertIn("DEEPWRITE_EDITORIAL_STOP_REQUIRES_CANDIDATE_BRANCH", source)


    def _live_review_cycle_fixture(self, proposed):
        """Exercise the actual runner review_cycle, not a copy of its gate logic."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        project = Path(tmp.name)
        (project / "chapters").mkdir()
        (project / "chapters/ch03.md").write_text(TEXT, encoding="utf-8")
        path = ROOT / "deepwrite/tools/writing_loop_experimental.py"
        spec = importlib.util.spec_from_file_location("editorial_writer_runtime_under_test", path)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        work = runner.WritingLoop.__new__(runner.WritingLoop)
        work.config = {"max_revision_rounds": 1, "guard": "on",
                       "reader_prior_knowledge_contract": {}}
        work.state = {"editorial_stop_history": {}}
        work.editorial_stop_guard = gate
        work.guard = SimpleNamespace(paragraphs=gate.paragraphs)
        work.path = lambda name: project / name
        work.event = lambda *args, **kwargs: None
        work.save_state = lambda: None
        work.reader_review = lambda *args, **kwargs: ({}, {"status": "MODEL_INTERNAL_REVIEW_RECORDED"})
        work.reader_findings = lambda *args, **kwargs: []
        work.check_record = lambda record, expected: {"status": "PASS_STRUCTURAL_ONLY"}
        def write(relative, raw):
            dest = project / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        work.write = write
        calls = []
        def call(key, role, payload):
            calls.append(role)
            if role != "review":
                self.fail("Unexpected edit/model call occurred before evidence gate")
            return {"text": json.dumps({"findings": [proposed]}, ensure_ascii=False),
                    "provider_kind": "fixture", "model": "fixture", "response_id": "r"}
        work.call = call
        return runner, work, calls, project

    def test_actual_runner_blocks_missing_case_before_any_revise(self):
        proposed = finding()
        proposed.pop("edit_case")
        runner, work, calls, project = self._live_review_cycle_fixture(proposed)
        with self.assertRaisesRegex(runner.Blocked, "EDITORIAL_STOP_HOLD_"):
            work.review_cycle("ch03", {"ch03": "chapters/ch03.md"})
        self.assertEqual(calls, ["review"])
        receipt = json.loads((project / "reviews/ch03.editorial_stop.json").read_text())
        self.assertEqual(receipt["status"], "HOLD")
        self.assertEqual(list((project / "chapters").iterdir())[0].name, "ch03.md")

    def test_actual_runner_style_only_keep_has_no_revision_call(self):
        runner, work, calls, project = self._live_review_cycle_fixture(finding("STYLE_ONLY"))
        result = work.review_cycle("ch03", {"ch03": "chapters/ch03.md"})
        self.assertEqual(result, {"ch03": "chapters/ch03.md"})
        self.assertEqual(calls, ["review"])
        receipt = json.loads((project / "reviews/ch03.editorial_stop.json").read_text())
        self.assertEqual(receipt["decisions"][0]["decision"], "KEEP_STYLE_NO_CHURN")
        self.assertEqual(receipt["author_acceptance"], "PENDING")

    def test_actual_runner_counts_soft_budget_across_scopes_before_revise(self):
        proposed = finding("READER_CAUSAL_GAP")
        runner, work, calls, project = self._live_review_cycle_fixture(proposed)
        work.state["editorial_p2_attempts"] = {ART: ["first", "second"]}
        work.config["max_revision_rounds"] = 5
        work.config["chapters"] = []
        original_call = work.call
        def call(key, role, payload):
            if role == "editorial_confirmation":
                calls.append(role)
                return {"text": json.dumps({"findings": [{"id": "bad_path", "verdict": "CONFIRMED",
                        "quote": "股票跌到了七十元", "reason": "An independent read confirms a material gap."}]})}
            return original_call(key, role, payload)
        work.call = call
        with self.assertRaisesRegex(runner.Blocked, "HOLD_P2_REWRITE_BUDGET_EXHAUSTED"):
            work.review_cycle("cross", {ART: "chapters/ch03.md"})
        self.assertEqual(calls, ["review", "editorial_confirmation"])
        self.assertEqual(work.state["editorial_p2_attempts"][ART], ["first", "second"])


def invocation_fixture():
    spec = importlib.util.spec_from_file_location("editorial_one_call_fixture", ROOT / "deepwrite/test_default.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    return fixture


class EditorialInvocationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = invocation_fixture()
        self.request = self.fixture.DefaultInvocationTests()
        # macOS may give tempfile a symlinked default directory. Production
        # continues to refuse such paths; the fixture constructs a real one.
        previous_directory = tempfile.gettempdir()
        with patch.object(tempfile, "tempdir", str(Path(previous_directory).resolve())):
            self.request.setUp()
        self.addCleanup(self.request.tearDown)
        self.request.data["experimental_editorial_stop_gate"] = True
        self.request.save_request()
        self.dw = self.fixture.dw
        git = self.dw.git
        # GitHub pull-request checkout is detached. Exercise actual HEAD and
        # file validation while supplying the explicit opt-in branch label.
        branch = patch.object(self.dw, "git", side_effect=lambda *args:
                            "editorial-test" if args == ("branch", "--show-current") else git(*args))
        branch.start()
        self.addCleanup(branch.stop)

    def test_opt_in_full_book_repairs_and_preserves_original_and_sources(self):
        fixture = self.fixture

        class Model(fixture.writer_test.ScriptedModel):
            def generate(self, instructions, prompt, max_output_tokens=6000):
                request = json.loads(prompt)
                role = request["role"]
                if role == "editorial_confirmation":
                    self.calls.append(role)
                    rows = [{"id": allegation["id"], "verdict": "CONFIRMED",
                             "quote": "2 + 2 = 5", "reason": "Counting two pairs gives four and contradicts five."}
                            for allegation in request["payload"]["allegations"]]
                    return fixture.writer_test.loop.transport.ModelResult(
                        "fixture-confirmation", "fixture-model", json.dumps({"findings": rows}),
                        {"input_tokens": 10, "output_tokens": 10}, "scripted_fixture")
                reply = super().generate(instructions, prompt, max_output_tokens)
                if role != "review":
                    return reply
                value = json.loads(reply.text)
                for row in value["findings"]:
                    if row["status"] == "OPEN":
                        row["edit_case"] = {"classification": "FACT_OR_MATH_ERROR", "baseline_quote": "2 + 2 = 5",
                            "reader_harm": "The calculation supplies an erroneous number of items.",
                            "minimal_remedy": "Count the two groups to obtain four objects.",
                            "regression_risk": "Preserve the distinction between counts and decisions."}
                return fixture.writer_test.loop.transport.ModelResult(
                    reply.response_id, reply.model, json.dumps(value), reply.usage, reply.provider_kind)

        model = Model()
        result = self.dw.run(self.request.request, self.request.destination,
                             research_model=fixture.StudyModel(), writer_model=model)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        project = self.request.destination / "writer_project"
        book = (project / "book.md").read_text()
        self.assertIn("2 + 2 = 4", book)
        self.assertNotIn("2 + 2 = 5", book)
        self.assertIn(fixture.writer_test.DRAFT.strip(), [p.read_text().strip() for p in (project / "chapters").glob("*.md")])
        self.assertEqual((project / "sources/native_001.md").read_text(), fixture.NATIVE)
        self.assertLess(model.calls.index("editorial_confirmation"), model.calls.index("revise"))
        self.assertEqual(model.calls.count("revise"), 1)
        self.assertEqual(self.dw.status(self.request.destination)["engine_alignment"]["status"], "MATCH")

    def test_opt_in_assisted_pause_resume_keeps_author_scope(self):
        self.request.data.update(mode="ASSISTED_AUTHOR_GATED", authorized_scope="FIRST_SAMPLE_AFTER_DISCOVERY")
        self.request.save_request()
        original_model = self.fixture.writer_test.ScriptedModel
        with patch.object(self.fixture.writer_test, "ScriptedModel", lambda: original_model(clean=True)):
            digest = self.request.invoke_paused()
        model = original_model(clean=True)
        result = self.dw.resume(self.request.destination, digest, research_model=self.fixture.StudyModel(), writer_model=model)
        self.assertEqual(result["status"], "AWAIT_AUTHOR_REVIEW", result)
        self.assertFalse((self.request.destination / "writer_project/book.md").exists())
        self.assertNotIn("revise", model.calls)
        self.assertEqual(self.dw.status(self.request.destination)["project_status"], "AWAIT_AUTHOR_REVIEW")
        with self.dw.editorial_execution_lock(self.request.destination, True):
            with self.assertRaisesRegex(self.dw.Blocked, "EDITORIAL_PROJECT_ALREADY_RUNNING"):
                self.dw.resume(self.request.destination, digest, writer_model=model)


if __name__ == "__main__":
    unittest.main()
