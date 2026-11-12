#!/usr/bin/env python3
"""Offline structural controls only: no real model and no quality claims."""
import copy
import hashlib
import unittest

from insight_origin_gate import check_run_config, inspect_proposals, sha256, SCHEMA


SOURCE = "Public elementary source: an actor can wait, but the opportunity to act can also disappear."


def fixture():
    wish = "Study the tradeoffs of making a decision before or after observing a move."
    sources = [{"path": "sources/public.md", "sha256": sha256(SOURCE.encode())}]
    cfg = {"channel": "SHADOW", "run_mode": "fresh", "wish": wish,
           "sources": sources, "insight_origin": {
               "schema": SCHEMA, "mode": "BLIND_PRE_REVEAL",
               "author_thesis_disclosed": False,
               "neutral_wish_sha256": sha256(wish.encode()),
               "experiment_id": "sample_unseen_001",
               "source_roles": [dict(sources[0], role="SOURCE_DOMAIN")]}}
    def lens(i):
        return {
            "id": "L" + str(i),
            "default_question": "What does the familiar rule imply for action " + str(i) + "?",
            "alternative_question": "What changes when actor " + str(i) + " uses a different objective?",
            "decision_before": "Choose the earliest available action under rule " + str(i),
            "decision_after": "Compare the changing opportunity costs of action " + str(i),
            "source_falsifier": "If no actor can change timing, the proposed effect disappears.",
            "source_anchor": {"path": "sources/public.md",
                              "quote": "an actor can wait, but the opportunity to act can also disappear"}
        }
    return cfg, {"origin_status": "MODEL_PROPOSAL_UNVERIFIED",
                 "lenses": [lens(i) for i in range(1, 4)]}


class BlindOriginGuardTests(unittest.TestCase):
    def test_positive_control_is_not_semantic_success(self):
        cfg, candidate = fixture()
        a = check_run_config(cfg)
        b = inspect_proposals(candidate, {"sources/public.md": SOURCE})
        self.assertEqual(a["status"], "PASS_DISCLOSED_INPUT_CONTRACT_ONLY")
        self.assertEqual(b["status"], "PASS_STRUCTURAL_ORIGIN_FROZEN_SEMANTICS_UNVERIFIED")
        self.assertEqual(b["semantic_novelty"], "UNVERIFIED")
        self.assertEqual(b["human_blind_review"], "NOT_RUN")

    def test_declared_author_thesis_fails_before_model(self):
        cfg, _ = fixture()
        cfg["insight_origin"]["source_roles"][0]["role"] = "AUTHOR_THESIS"
        with self.assertRaisesRegex(ValueError, "SOURCE_ROLE_DISALLOWED"):
            check_run_config(cfg)

    def test_non_disclosed_author_state_must_be_explicit(self):
        cfg, _ = fixture()
        del cfg["insight_origin"]["author_thesis_disclosed"]
        with self.assertRaisesRegex(ValueError, "AUTHOR_THESIS_DISCLOSURE"):
            check_run_config(cfg)

    def test_prompt_changed_after_freeze(self):
        cfg, _ = fixture()
        cfg["wish"] += " Surprise, here is the intended answer."
        with self.assertRaisesRegex(ValueError, "NEUTRAL_WISH_SHA"):
            check_run_config(cfg)

    def test_source_sha_fingerprint_tampering(self):
        cfg, _ = fixture()
        cfg["insight_origin"]["source_roles"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "PIN_MISMATCH"):
            check_run_config(cfg)

    def test_not_a_shadow_fresh_test(self):
        cfg, _ = fixture()
        cfg["channel"] = "CANDIDATE_OPT_IN"
        with self.assertRaisesRegex(ValueError, "SHADOW_FRESH"):
            check_run_config(cfg)

    def test_author_hint_as_direct_config_is_blocked(self):
        cfg, _ = fixture()
        cfg["seed_insight"] = "The intended conclusion was supplied by author"
        with self.assertRaisesRegex(ValueError, "CONTAMINATING_INPUT"):
            check_run_config(cfg)

    def test_no_rival_frames_is_not_discovery(self):
        _, c = fixture()
        c["lenses"] = c["lenses"][:1]
        b = inspect_proposals(c, {"sources/public.md": SOURCE})
        self.assertIn("AT_LEAST_THREE_RIVAL_QUESTIONS_REQUIRED", b["errors"])

    def test_copying_same_question_fails_distinctness(self):
        _, c = fixture()
        c["lenses"][2] = copy.deepcopy(c["lenses"][1])
        c["lenses"][2]["id"] = "L3"
        b = inspect_proposals(c, {"sources/public.md": SOURCE})
        self.assertIn("DUPLICATE_CONTRAST_2", b["errors"])

    def test_same_decision_despite_rhetoric_fails(self):
        _, c = fixture()
        c["lenses"][0]["decision_after"] = c["lenses"][0]["decision_before"]
        b = inspect_proposals(c, {"sources/public.md": SOURCE})
        self.assertIn("NO_DECISION_DIFFERENCE_0", b["errors"])

    def test_fabricated_quote_fails(self):
        _, c = fixture()
        c["lenses"][1]["source_anchor"]["quote"] = "Some made-up quotation about a wholly different kind of contest"
        b = inspect_proposals(c, {"sources/public.md": SOURCE})
        self.assertIn("UNVERIFIED_SOURCE_ANCHOR_1", b["errors"])

    def test_model_cannot_claim_author_approval(self):
        _, c = fixture()
        c["human_acceptance"] = "PASS"
        b = inspect_proposals(c, {"sources/public.md": SOURCE})
        self.assertIn("PREMATURE_AUTHOR_AUTHORITY_OR_REVEAL", b["errors"])

    def test_model_must_not_claim_original_discovery(self):
        _, c = fixture()
        c["origin_status"] = "ORIGINAL_DISCOVERY_CONFIRMED"
        b = inspect_proposals(c, {"sources/public.md": SOURCE})
        self.assertIn("ORIGIN_STATUS_MUST_REMAIN_UNVERIFIED", b["errors"])


if __name__ == "__main__":
    unittest.main()
