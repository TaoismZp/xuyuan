#!/usr/bin/env python3
"""Synthetic two-stage discovery regressions; never a real provider or reader result."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import architecture_discovery as discovery


def h(raw):
    return hashlib.sha256(raw).hexdigest()


NATIVE = b"Public engineering fixture only: two pairs contain four objects.\n"
STUDY = {
    "study_markdown": "# Native arithmetic study\n\nTwo distinct groups of two contain four objects; the rule is context sensitive.",
    "source_concepts": [{
        "id": "native_pairs", "source_path": "sources/material.md",
        "quote": "two pairs contain four objects",
        "causal_mechanism": "Counting both disjoint groups creates a total of four objects.",
        "counterinterpretation": "Double counting an object can create a different apparent sum.",
        "transfer_limit": "Counting objects alone does not license claims about market outcomes."
    }],
    "rival_directions": [
        {"id": "count_first", "source_question": "How does two plus two become four?",
         "reader_problem": "The reader might confuse a total with an unsupported assertion.",
         "tradeoff": "This starts from a very simple calculation and must deepen later."},
        {"id": "compare_first", "source_question": "When do repeated objects invalidate the calculation?",
         "reader_problem": "The reader might miscount when categories overlap.",
         "tradeoff": "This rival starts with set theory before the reader is ready."}
    ]
}
BOOK = {
    "chapters": [{"artifact_id": "alpha", "title": "From a claim to actual arithmetic reasoning"}],
    "selected_direction_id": "count_first",
    "why_selected_over_rivals": "Study the source decision before a larger and more elaborate analogy.",
    "book_design": {
        "why_these_chapters_not_source_outline": "One chapter here serves the reader's actual problem, not a course lesson count.",
        "chapter_contributions": [{"chapter_id": "alpha",
            "source_concept_ids": ["native_pairs"],
            "distinct_reader_change": "Reconstruct the original groups before transferring a claim."}]
    },
    "reader_prior_knowledge_contract": {
        "schema": "deepwrite/reader-prior-contract/v1",
        "known": ["elementary arithmetic"],
        "unknown": ["when source claims lack evidence"],
        "concepts": [{"id": "native_pairs", "first_explained_in": "alpha",
                      "first_used_in": "alpha", "prerequisites": []}],
        "knowledge_compounding": {
            "enabled": True,
            "transfer_goal": "Check if a similar rule applies to different objects without repeating the example."}
    }
}


class ScriptedDiscovery:
    is_live = False

    def __init__(self, source=None, book=None, cost=8):
        self.source = source if source is not None else STUDY
        self.book = book if book is not None else BOOK
        self.cost = cost
        self.roles = []
        self.previews = []

    def generate(self, instructions, prompt, max_output_tokens=6000):
        req = json.loads(prompt)
        self.roles.append(req["role"])
        self.previews.append(req)
        if req["role"] == "source_domain_study":
            response = self.source
        elif req["role"] == "book_architecture_discovery":
            response = self.book
        else:
            raise AssertionError("unexpected generator role " + req["role"])
        return SimpleNamespace(model="fixture-planner", provider_kind="fixture",
            response_id="fixture-stage-" + str(len(self.roles)),
            text=json.dumps(response, ensure_ascii=False),
            usage={"input_tokens": self.cost // 2, "output_tokens": self.cost // 2})


class TwoPhaseDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="deepwrite-two-phase-fixture-")
        base = Path(self.tmp.name)
        self.project = base / "writer_project"
        self.sources = self.project / "sources"
        self.sources.mkdir(parents=True)
        self.out = base / "discovery_receipts"
        (self.sources / "material.md").write_bytes(NATIVE)
        auth = {
            "schema": "deepwrite/author-project-authorization/v1",
            "project_id": "two-phase-fixture",
            "mode": "AUTONOMOUS_FULL_DRAFT",
            "chapter_scope": "ALL_CANDIDATE_CHAPTERS",
            "author_identity_verification": "ENGINEERING_FIXTURE_NOT_REAL_AUTHOR"
        }
        auth_bytes = discovery.encoded(auth)
        (self.sources / "author-contract.txt").write_bytes(auth_bytes)
        self.cfg = {
            "project_id": "two-phase-fixture", "run_id": "two-phase-synthetic-run",
            "adapter": "fixture", "allow_fixture": True,
            "model": "fixture-planner", "channel": "CANDIDATE_OPT_IN",
            "working_title": "Synthetic arithmetic source research",
            "wish": "Build one research-grounded chapter teaching how to verify a numerical claim.",
            "guard": "on", "token_budget": 10000, "per_call_output_tokens": 1000, "max_revision_rounds": 1,
            "discovery_token_budget": 200, "discovery_output_cap": 1000,
            "min_chapters": 1, "max_chapters": 3,
            "modules": {"e18_loop": True, "source_first_architecture": True},
            "module_policy": {"e18_loop": "CANDIDATE", "source_first_architecture": "CANDIDATE"},
            "module_commits": {"e18_loop": "3"*40, "source_first_architecture": "4"*40},
            "pins": {"project_id": "two-phase-fixture", "channel": "CANDIDATE_OPT_IN",
                "modules": [{"id": "e18_loop", "commit": "3"*40},
                            {"id": "source_first_architecture", "commit": "4"*40}],
                "protocols": {
                    "deepwrite": {"version": "v0.1", "commit": "1"*40, "spec_sha": "2"*40},
                    "wish_delivery": {"version": "v7.6", "commit": "1"*40, "spec_sha": "2"*40}}},
            "sources": [
                {"path": "sources/material.md", "sha256": h(NATIVE)},
                {"path": "sources/author-contract.txt", "sha256": h(auth_bytes)}],
            "execution_contract": {"mode": "AUTONOMOUS_FULL_DRAFT",
                "authorization": {"path": "sources/author-contract.txt", "sha256": h(auth_bytes),
                                  "provenance": "EXPLICIT_ENGINEERING_FIXTURE_NOT_REAL_AUTHORIZATION"}}
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_discovery_stages_are_actual_order_not_preset_chapters(self):
        model = ScriptedDiscovery()
        receipt = discovery.discover(self.cfg, self.project, self.out, model=model)
        self.assertEqual(model.roles, ["source_domain_study", "book_architecture_discovery"])
        self.assertNotIn("chapters", model.previews[0]["payload"])
        self.assertNotIn("chapters", self.cfg)
        self.assertEqual(receipt["chapter_count"], 1)
        self.assertEqual(receipt["actual_writer_run"], "NOT_RUN")
        self.assertEqual(receipt["human_blind_evaluation"], "NOT_RUN")
        conf = json.loads((self.out/"writer_config.json").read_text())
        self.assertEqual(conf["chapters"][0]["artifact_id"], "alpha")
        self.assertEqual(conf["source_first_architecture"]["status"], "PROVISIONAL_NOT_AUTHOR_APPROVED")
        self.assertTrue((self.project/"sources/discovery_native_study.md").is_file())
        self.assertTrue((self.out/"source_domain_study.response.json").is_file())
        self.assertTrue((self.out/"book_architecture_discovery.response.json").is_file())
        self.assertIn("sources/material.md", [r["path"] for r in conf["sources"]])


    def test_chapter_count_can_change_from_one_to_two_without_preset_outline(self):
        alternative = copy.deepcopy(BOOK)
        alternative["chapters"].append({"artifact_id": "beta",
                                         "title": "When counted categories overlap"})
        alternative["book_design"]["chapter_contributions"].append({
            "chapter_id": "beta", "source_concept_ids": ["native_pairs"],
            "distinct_reader_change": "Recheck what appeared independent before combining evidence."})
        alternative["reader_prior_knowledge_contract"]["concepts"].append({
            "id": "overlapping_sets", "first_explained_in": "beta",
            "first_used_in": "beta", "prerequisites": ["native_pairs"]})
        model = ScriptedDiscovery(book=alternative)
        receipt = discovery.discover(self.cfg, self.project, self.out, model=model)
        self.assertEqual(receipt["chapter_count"], 2)
        self.assertEqual(receipt["chapters"], ["alpha", "beta"])
        self.assertEqual(model.roles, ["source_domain_study", "book_architecture_discovery"])
        planned = json.loads((self.out / "writer_config.json").read_text())
        self.assertEqual(len(planned["chapters"]), 2)
        self.assertEqual(
            planned["reader_prior_knowledge_contract"]["concepts"][1]["prerequisites"],
            ["native_pairs"])
        self.assertEqual(receipt["author_acceptance"], "NOT_RUN")

    def test_missing_budget_fails_before_model_call(self):
        del self.cfg["discovery_token_budget"]
        model = ScriptedDiscovery()
        with self.assertRaisesRegex(discovery.Blocked, "BUDGET"):
            discovery.discover(self.cfg, self.project, self.out, model=model)
        self.assertEqual(model.roles, [])

    def test_cannot_reuse_predefined_chapter_count(self):
        self.cfg["chapters"] = [{"artifact_id": "ch1", "title": "Already decided"}]
        model = ScriptedDiscovery()
        with self.assertRaisesRegex(discovery.Blocked, "PRESET_CHAPTERS"):
            discovery.discover(self.cfg, self.project, self.out, model=model)
        self.assertEqual(model.roles, [])

    def test_only_opt_in_and_author_full_draft_allowed(self):
        self.cfg["channel"] = "STABLE"
        with self.assertRaisesRegex(discovery.Blocked, "STABLE_ONLY_FOR_ACTIVATED"):
            discovery.discover(self.cfg, self.project, self.out, model=ScriptedDiscovery())
        self.cfg["channel"] = "CANDIDATE_OPT_IN"
        self.cfg["execution_contract"]["mode"] = "ASSISTED_AUTHOR_GATED"
        with self.assertRaisesRegex(discovery.Blocked, "AUTHOR_PROJECT_SCOPE_INVALID"):
            discovery.discover(self.cfg, self.project, self.out, model=ScriptedDiscovery())

    def test_source_sha_tamper_stops_before_invocation(self):
        (self.sources/"material.md").write_bytes(b"CHANGED")
        model = ScriptedDiscovery()
        with self.assertRaisesRegex(discovery.Blocked, "SOURCE_SHA_MISMATCH"):
            discovery.discover(self.cfg, self.project, self.out, model=model)
        self.assertEqual(model.roles, [])

    def test_false_source_quote_stops_after_stage_one(self):
        payload = copy.deepcopy(STUDY)
        payload["source_concepts"][0]["quote"] = "this quotation is not found in source material"
        model = ScriptedDiscovery(source=payload)
        with self.assertRaisesRegex(discovery.Blocked, "QUOTE_NOT_IN_BYTES"):
            discovery.discover(self.cfg, self.project, self.out, model=model)
        self.assertEqual(model.roles, ["source_domain_study"])
        self.assertFalse((self.project/"sources/discovery_native_study.md").exists())
        self.assertEqual(json.loads((self.out/"STATE.json").read_text())["status"], "BLOCKED")

    def test_multiple_rivals_are_mandatory(self):
        payload = copy.deepcopy(STUDY)
        payload["rival_directions"] = payload["rival_directions"][:1]
        with self.assertRaisesRegex(discovery.Blocked, "RIVALS_REQUIRED"):
            discovery.discover(self.cfg, self.project, self.out, model=ScriptedDiscovery(source=payload))

    def test_wrong_book_count_is_not_written_or_self_approved(self):
        book = copy.deepcopy(BOOK)
        book["chapters"] = book["chapters"] * 4
        with self.assertRaisesRegex(discovery.Blocked, "CHAPTER_COUNT_OR_ID"):
            discovery.discover(self.cfg, self.project, self.out, model=ScriptedDiscovery(book=book))
        self.assertFalse((self.out/"writer_config.json").exists())

    def test_unknown_compounding_contract_is_blocked(self):
        book = copy.deepcopy(BOOK)
        book["reader_prior_knowledge_contract"]["knowledge_compounding"]["enabled"] = False
        with self.assertRaisesRegex(discovery.Blocked, "COMPOUNDING_CONTRACT_REQUIRED"):
            discovery.discover(self.cfg, self.project, self.out, model=ScriptedDiscovery(book=book))

    def test_budget_exceeded_preserves_failure_checkpoint(self):
        model = ScriptedDiscovery(cost=300)
        with self.assertRaisesRegex(discovery.Blocked, "TOKEN_BUDGET_EXCEEDED"):
            discovery.discover(self.cfg, self.project, self.out, model=model)
        self.assertEqual(json.loads((self.out/"STATE.json").read_text())["status"], "BLOCKED")

    def test_successful_discovery_can_feed_actual_e18_scripted_writer(self):
        discovery.discover(self.cfg, self.project, self.out, model=ScriptedDiscovery())
        candidate = json.loads((self.out/"writer_config.json").read_text())
        spec = importlib.util.spec_from_file_location(
            "deepwrite_two_phase_test_writer",
            discovery.DEEPWRITE / "tools/tests/test_writing_loop_experimental.py")
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        obj = fixture.loop.WritingLoop(self.project, candidate, model=fixture.ScriptedModel())
        result = obj.run()
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertTrue((self.project/"book.md").exists())
        self.assertEqual(obj.state["source_first_intake"]["status"],
                         "PASS_ENGINEERING_ONLY_PROVISIONAL_SOURCE_ARCHITECTURE")
        self.assertEqual(obj.state["acceptance"]["AUTHOR_ACCEPTANCE"], "NOT_RUN")
        self.assertEqual(obj.state["acceptance"]["HUMAN_BLIND_EVALUATION"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
