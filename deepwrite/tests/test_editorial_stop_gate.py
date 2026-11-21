#!/usr/bin/env python3
"""Deterministic negative tests for the opt-in editorial stop gate.

Engineering checks only. These do not certify literary or reader quality.
"""
import ast
import copy
import importlib.util
from pathlib import Path
import unittest

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

    def test_wrong_paragraph_is_refused(self):
        row = finding()
        row["paragraph"] = 1
        self.assertEqual(self.audit([row])["status"], "HOLD")

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

    def test_distinct_artifact_same_quote_not_false_duplicate(self):
        row = finding(art="ch05")
        result = self.audit([finding(), row], manuscripts={ART: TEXT, "ch05": TEXT})
        self.assertEqual(result["status"], "PASS_PROPOSALS_ONLY")

    def test_generated_reader_major_stays_with_reader_guard(self):
        row = finding(id="reader_ch03_gate")
        result = self.audit([row])
        self.assertEqual(result["decisions"][0]["decision"], "DELEGATED_TO_EXISTING_READER_GATE")

    def test_input_is_not_modified(self):
        rows = [finding("STYLE_ONLY")]
        original = copy.deepcopy(rows)
        self.audit(rows)
        self.assertEqual(rows, original)

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

    def test_author_opt_in_routes_to_frozen_candidate_contract(self):
        source = (ROOT / "deepwrite/deepwrite.py").read_text("utf-8")
        ast.parse(source)
        self.assertIn("experimental_editorial_stop_gate", source)
        self.assertIn('"editorial_stopping": True', source)
        self.assertIn('channel = "CANDIDATE_OPT_IN"', source)
        self.assertIn("DEEPWRITE_EDITORIAL_STOP_REQUIRES_CANDIDATE_BRANCH", source)


if __name__ == "__main__":
    unittest.main()
