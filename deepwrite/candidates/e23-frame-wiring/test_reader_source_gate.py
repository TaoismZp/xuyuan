#!/usr/bin/env python3
"""Located-review fixtures: engineering STOP controls, never reader-effect proof.

The semantic findings below are deliberately supplied fixture responses. These
tests do not establish that any real model discovers the defects unaided.
"""
import copy
import hashlib
import unittest
from reader_source_gate import (AUDIENCES, CONTRACT_SCHEMA, REVIEW_SCHEMA,
    SOURCE_DIMENSIONS, canonical, evaluate, review_instructions, validate_contract)


def h(text):
    return hashlib.sha256(text.encode()).hexdigest()


def contract():
    return {"schema": CONTRACT_SCHEMA, "known": ["ordinary arithmetic"],
        "unknown": ["the source game's rules and action order"],
        "concepts": [{"id": "action_order", "first_explained_in": "ch1",
                      "first_used_in": "ch1", "prerequisites": []}]}


TEXT = ("# Ada's choice\n\n"
        "Ada can observe Ben's check, choose a free check or bet, but Ben can still answer a bet. "
        "Her options depend on the current street and on whether anyone has opened the betting.\n\n"
        "Waiting does not guarantee accuracy. A public earnings announcement can change the quote "
        "before a later investor acts, so the old price is not an available payoff condition.")
SOURCE = ("# Public rule fixture\n\n"
          "In a multiway hold'em hand the button acts before both blinds preflop. "
          "After the flop the first active seat clockwise from the button acts first; "
          "the button's later position does not prevent a response to its new bet.")


def report(text=TEXT, stage="CHAPTER", prior=None):
    prior = prior or contract()
    paragraphs = text.split("\n\n")
    dimensions = list(SOURCE_DIMENSIONS) + (["target_reconstruction"] if stage != "SOURCE_LEARNING" else [])
    return {"schema": REVIEW_SCHEMA, "artifact_sha256": h(text),
        "contract_sha256": hashlib.sha256(canonical(prior)).hexdigest(),
        "reviewer": "SCRIPTED_FIXTURE_NOT_A_REAL_MODEL_RESPONSE",
        "source_correctness": {"verdict": "SUPPORTED", "rationale": "Fixture reviewer checked the stated rule and its limitations."},
        "source_evidence": [{"concept_id": "action_order", "dimension": dimension,
                             "paragraph": 2, "quote": paragraphs[1]} for dimension in dimensions],
        "source_material_evidence": [{"source_id": "rules.md", "paragraph": 2,
                                     "quote": SOURCE.split("\n\n")[1]}],
        "reader_checks": [{"audience": audience, "verdict": "SUPPORTED",
            "rationale": "Fixture bounded observation of the same narrative; no human was tested.",
            "paragraph": 2, "quote": paragraphs[1]} for audience in AUDIENCES],
        "findings": []}


class ReaderContractTests(unittest.TestCase):
    def test_contract_freezes_actual_unknowns_and_dependency_positions(self):
        value = validate_contract(contract(), [{"artifact_id": "ch1"}, {"artifact_id": "ch2"}])
        self.assertEqual(value["status"], "ENGINEERING_CONTRACT_FROZEN")
        self.assertEqual(value["contract_sha256"], hashlib.sha256(canonical(contract())).hexdigest())
        self.assertEqual(value["semantic_prior_or_dependency_correctness"], "NOT_CERTIFIED")

    def test_changed_reader_prior_changes_frozen_identity(self):
        original = contract(); changed = copy.deepcopy(original)
        changed["known"].append("all poker rules")
        self.assertNotEqual(hashlib.sha256(canonical(original)).hexdigest(), hashlib.sha256(canonical(changed)).hexdigest())

    def test_unknown_reader_priors_cannot_disappear(self):
        prior = contract(); prior["unknown"] = []
        with self.assertRaisesRegex(ValueError, "UNKNOWN_OR_CONTRADICTORY"):
            validate_contract(prior, ["ch1"])

    def test_contradictory_reader_priors_stop(self):
        prior = contract(); prior["known"].append(prior["unknown"][0])
        with self.assertRaisesRegex(ValueError, "CONTRADICTORY"):
            validate_contract(prior, ["ch1"])

    def test_concept_cannot_be_used_in_an_earlier_declared_chapter(self):
        prior = contract(); prior["concepts"][0]["first_explained_in"] = "ch2"
        with self.assertRaisesRegex(ValueError, "USED_BEFORE"):
            validate_contract(prior, ["ch1", "ch2"])

    def test_unknown_prerequisite_stops(self):
        prior = contract(); prior["concepts"][0]["prerequisites"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "UNKNOWN_OR_SELF"):
            validate_contract(prior, ["ch1"])

    def test_cycle_cannot_look_like_a_complete_dependency_map(self):
        prior = contract()
        prior["concepts"][0]["prerequisites"] = ["second"]
        prior["concepts"].append({"id": "second", "first_explained_in": "ch1", "first_used_in": "ch1", "prerequisites": ["action_order"]})
        with self.assertRaisesRegex(ValueError, "CYCLE"):
            validate_contract(prior, ["ch1"])


class LocatedReaderReviewTests(unittest.TestCase):
    def gate(self, value=None, text=TEXT, stage="CHAPTER"):
        return evaluate(contract(), "ch1", text, value if value is not None else report(text, stage),
                        stage=stage, source_texts={"rules.md": SOURCE})

    def failure(self, text, code, stage="CHAPTER"):
        value = report(text, stage)
        value["findings"] = [{"code": code, "severity": "MAJOR", "status": "OPEN",
                              "paragraph": 2, "quote": text.split("\n\n")[1],
                              "reason": "Supplied fixture critique requires source research or actual text repair."}]
        return self.gate(value, text, stage)

    def test_rigorous_narrative_without_template_keywords_is_allowed(self):
        result = self.gate()
        self.assertEqual(result["status"], "MODEL_INTERNAL_REVIEW_RECORDED", result)
        self.assertEqual(result["reader_source_transfer_gate"], "ENGINEERING_ONLY")
        self.assertEqual(result["human_blind_evaluation"], "NOT_RUN")
        self.assertEqual(result["author_acceptance"], "NOT_RUN")
        self.assertFalse(result["published"])
        self.assertEqual(report()["findings"], [])

    def test_source_learning_bound_to_actual_source_paragraphs(self):
        result = self.gate(stage="SOURCE_LEARNING")
        self.assertEqual(result["status"], "MODEL_INTERNAL_REVIEW_RECORDED", result)

    def test_dictionary_only_reader_prerequisites_trigger_rework(self):
        text = "# Short glossary\n\nUTG means first seat, BTN means button. Therefore buy late."
        result = self.failure(text, "READER_PREREQUISITE_ASSUMED")
        self.assertEqual(result["status"], "CONTENT_REWORK", result)

    def test_false_action_order_requires_research_before_transfer(self):
        text = "# Acting last\n\nThe button always acts last on every street, so a late buyer always gets the better price."
        result = self.failure(text, "SOURCE_DOMAIN_RULE_ERROR")
        self.assertEqual(result["status"], "STOP_RESEARCH_MORE", result)

    def test_source_review_that_is_still_incorrect_stops_before_draft(self):
        value = report(stage="SOURCE_LEARNING")
        value["source_correctness"] = {"verdict": "RESEARCH_MORE", "rationale": "The supplied rule has not been established."}
        result = self.gate(value, stage="SOURCE_LEARNING")
        self.assertEqual(result["status"], "STOP_RESEARCH_MORE", result)

    def test_intro_only_with_no_research_contribution_triggers_rework(self):
        text = "# A first lesson\n\nA participant can check, bet, call or fold. That is the end of the explanation."
        result = self.failure(text, "NOVICE_EXPERT_VALUE_COLLAPSE")
        self.assertEqual(result["status"], "CONTENT_REWORK", result)

    def test_forced_three_level_sections_that_repeat_trigger_rework(self):
        text = "# Three audiences\n\nNewcomers: wait for information. Regulars: wait for information. Experts: wait for information."
        result = self.failure(text, "FORCED_READER_TEMPLATE_REPETITION")
        self.assertEqual(result["status"], "CONTENT_REWORK", result)

    def test_later_reuse_of_wrong_prior_is_not_a_new_quality_pass(self):
        text = "# Further deduction\n\nAs established earlier, late action guarantees accuracy, so leverage can now be increased."
        result = self.failure(text, "NEGATIVE_KNOWLEDGE_COMPOUNDING")
        self.assertEqual(result["status"], "STOP_RESEARCH_MORE", result)

    def test_missing_real_reviewer_never_defaults_to_no_problem(self):
        self.assertEqual(self.gate({})["status"], "HOLD_REVIEW_EVIDENCE")

    def test_changed_text_invalidates_old_review(self):
        result = self.gate(report(), TEXT + "\n\nA new unsupported claim.")
        self.assertIn("READER_REVIEW_ARTIFACT_SHA_MISMATCH", result["errors"])
        self.assertEqual(result["status"], "HOLD_REVIEW_EVIDENCE")

    def test_reader_contract_change_invalidates_review(self):
        value = report(); value["contract_sha256"] = "0" * 64
        result = self.gate(value)
        self.assertIn("READER_REVIEW_CONTRACT_SHA_MISMATCH", result["errors"])

    def test_qa_card_without_located_body_evidence_does_not_count(self):
        value = report(); value["source_evidence"] = []
        result = self.gate(value)
        self.assertEqual(result["status"], "HOLD_REVIEW_EVIDENCE")

    def test_report_quote_must_exist_at_the_actual_body_location(self):
        value = report(); value["source_evidence"][0]["quote"] = "this sentence is only in the QA report"
        result = self.gate(value)
        self.assertIn("SOURCE_EVIDENCE_QUOTE_NOT_IN_ACTUAL_PARAGRAPH", result["errors"])

    def test_source_quote_cannot_come_from_an_unread_material(self):
        value = report(stage="SOURCE_LEARNING")
        value["source_material_evidence"][0]["source_id"] = "not-provided.md"
        result = self.gate(value, stage="SOURCE_LEARNING")
        self.assertIn("UNKNOWN_SOURCE_MATERIAL_ID", result["errors"])

    def test_no_readable_source_means_research_evidence_hold(self):
        result = evaluate(contract(), "ch1", TEXT, report(stage="SOURCE_LEARNING"),
                          stage="SOURCE_LEARNING", source_texts={})
        self.assertEqual(result["status"], "HOLD_REVIEW_EVIDENCE")

    def test_model_cannot_self_declare_author_or_human_signoff(self):
        value = report(); value["author_acceptance"] = "PASS"
        value["human_blind_evaluation"] = "PASS"
        result = self.gate(value)
        self.assertIn("READER_REVIEW_CANNOT_AUTHENTICATE_AUTHOR", result["errors"])
        self.assertIn("MODEL_REVIEW_CANNOT_CLAIM_HUMAN_BLIND_EVALUATION", result["errors"])

    def test_unverified_reading_perspective_requires_actual_rework(self):
        value = report(); value["reader_checks"][0]["verdict"] = "UNVERIFIED"
        self.assertEqual(self.gate(value)["status"], "CONTENT_REWORK")

    def test_fake_closed_on_a_new_source_finding_is_not_closeout(self):
        value = report()
        value["findings"] = [{"code": "READER_PREREQUISITE_ASSUMED", "severity": "MAJOR", "status": "CLOSED",
            "paragraph": 2, "quote": TEXT.split("\n\n")[1], "reason": "The QA card says fixed."}]
        result = self.gate(value)
        self.assertEqual(result["status"], "HOLD_REVIEW_EVIDENCE")


    def test_knowledge_compounding_optional_contract_must_include_transfer_goal(self):
        prior = contract()
        prior["knowledge_compounding"] = {"enabled": True}
        with self.assertRaisesRegex(ValueError, "KNOWLEDGE_COMPOUNDING_CONTRACT_INVALID"):
            validate_contract(prior, ["ch1"])

    def test_knowledge_compounding_missing_model_transfer_probe_holds(self):
        prior = contract()
        prior["knowledge_compounding"] = {"enabled": True,
                                         "transfer_goal": "Apply learned action order to a distinct unfamiliar decision."}
        output = evaluate(prior, "ch1", TEXT, report(prior=prior), stage="CHAPTER")
        self.assertEqual(output["status"], "HOLD_REVIEW_EVIDENCE")
        self.assertIn("KNOWLEDGE_COMPOUNDING_TRANSFER_PROBE_REQUIRED", output["errors"])

    def test_knowledge_compounding_unverified_transfer_blocks_actual_chapter(self):
        prior = contract()
        prior["knowledge_compounding"] = {"enabled": True,
                                         "transfer_goal": "Transfer source reasoning to a new action setting."}
        proof = report(prior=prior)
        proof["knowledge_compounding_probe"] = {
            "prerequisite_concept_id": "action_order", "new_situation": "An unfamiliar delayed-action market auction.",
            "expected_inference": "Examine which move remains available when information arrives.",
            "failure_boundary": "A later move cannot be assumed to retain earlier prices.",
            "rationale": "Scripted refusal to claim real reader comprehension.",
            "verdict": "UNVERIFIED", "paragraph": 2, "quote": TEXT.split("\n\n")[1]
        }
        output = evaluate(prior, "ch1", TEXT, proof, stage="CHAPTER")
        self.assertEqual(output["status"], "CONTENT_REWORK", output)
        self.assertEqual(output["blocking_findings"][0]["code"], "KNOWLEDGE_COMPOUNDING_NOT_DEMONSTRATED")

    def test_knowledge_compounding_located_model_pass_never_claims_human_pass(self):
        prior = contract()
        prior["knowledge_compounding"] = {"enabled": True,
                                         "transfer_goal": "Infer a fresh decision boundary using the previously learned mechanism."}
        proof = report(prior=prior)
        proof["knowledge_compounding_probe"] = {
            "prerequisite_concept_id": "action_order", "new_situation": "A previously unseen quote-driven process.",
            "expected_inference": "Infer when optional waiting changes feasible actions.",
            "failure_boundary": "The previous quote is not guaranteed after the news.",
            "rationale": "Scripted model-only test; actual readers not observed.",
            "verdict": "SUPPORTED", "paragraph": 2, "quote": TEXT.split("\n\n")[1]
        }
        output = evaluate(prior, "ch1", TEXT, proof, stage="CHAPTER")
        self.assertEqual(output["status"], "MODEL_INTERNAL_REVIEW_RECORDED", output)
        self.assertEqual(output["human_blind_evaluation"], "NOT_RUN")
        self.assertEqual(output["author_acceptance"], "NOT_RUN")

    def test_instructions_request_actual_review_not_an_audience_template(self):
        task = review_instructions(contract(), "ch1", "CHAPTER")
        self.assertIn("not established truth", task["task"])
        self.assertEqual(task["required_source_concepts"], ["action_order"])
        self.assertIn("target_reconstruction", task["source_dimensions"])


if __name__ == "__main__":
    unittest.main()
