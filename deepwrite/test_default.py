#!/usr/bin/env python3
"""One-command DeepWrite integration; synthetic data/fixture models only."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("deepwrite_default_candidate", Path(__file__).with_name("deepwrite.py"))
dw = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dw)

WRITER_PATH = Path(__file__).parent / "tools/tests/test_writing_loop_experimental.py"
WRITER_SPEC = importlib.util.spec_from_file_location("deepwrite_fixture_writer", WRITER_PATH)
writer_test = importlib.util.module_from_spec(WRITER_SPEC)
WRITER_SPEC.loader.exec_module(writer_test)

NATIVE = "Public engineering fixture only: two pairs contain four objects.\nAn extra object must not be counted twice.\n"
ANCHOR = "two pairs contain four objects"


def study():
    return {
        "study_markdown": "# Native source understanding\n\nTwo groups of two must be counted without duplicating objects.",
        "source_concepts": [{
            "id": "native_pairs", "source_path": "sources/native_001.md",
            "quote": ANCHOR,
            "causal_mechanism": "Counting two separate groups of two creates four objects.",
            "counterinterpretation": "An overlapping member makes the usual sum misleading.",
            "transfer_limit": "Counting mathematical objects cannot establish a trading law."
        }],
        "rival_directions": [
            {"id": "count_first", "source_question": "How do we know two plus two makes four?",
             "reader_problem": "The reader might accept a number without a source mechanism.",
             "tradeoff": "A simple case risks becoming a school lesson."},
            {"id": "overlap_first", "source_question": "How can double counting produce a misleading total?",
             "reader_problem": "The reader may confuse overlapping groups with disjoint groups.",
             "tradeoff": "This concept can distract from a simpler first explanation."}
        ],
        "origin_status": "MODEL_PROPOSAL_UNVERIFIED",
        "lenses": [
            {"id": f"L{n}", "default_question": f"What does adding disjoint sets mean in situation {n}?",
             "alternative_question": f"What if the same objects recur across the two groups in case {n}?",
             "decision_before": f"Assume two groups are independent and report four objects for sample {n}.",
             "decision_after": f"Check for overlapping identities before combining the group in sample {n}.",
             "source_falsifier": "If there were no actual objects, the counting example would not be evidence.",
             "source_anchor": {"path": "sources/native_001.md", "quote": ANCHOR}} for n in range(1,4)
        ]
    }


def book():
    return {
        "chapters": [{"artifact_id": "alpha", "title": "How counted evidence becomes a claim"}],
        "selected_direction_id": "count_first",
        "why_selected_over_rivals": "This direction first teaches the novice what is being counted.",
        "book_design": {
            "why_these_chapters_not_source_outline": "One chapter teaches a grounded mechanism, not one chapter per source.",
            "chapter_contributions": [{
                "chapter_id": "alpha", "source_concept_ids": ["native_pairs"],
                "distinct_reader_change": "Check the relevant objects before believing a computed result."
            }]
        },
        "reader_prior_knowledge_contract": {
            "schema": "deepwrite/reader-prior-contract/v1",
            "known": ["Elementary arithmetic is familiar."],
            "unknown": ["When two groups overlap, they cannot be counted twice."],
            "concepts": [{
                "id": "native_pairs", "first_explained_in": "alpha",
                "first_used_in": "alpha", "prerequisites": []}],
            "knowledge_compounding": {
                "enabled": True,
                "transfer_goal": "Apply the prior counting principle to a genuinely new kind of claim."
            }
        }
    }


class StudyModel:
    is_live = False

    def __init__(self, prepared=None, force_replan=False):
        self.roles=[]
        self.prepared=prepared
        self.force_replan=force_replan

    def generate(self, instructions, prompt, max_output_tokens=5000):
        req=json.loads(prompt)
        self.roles.append(req["role"])
        result=study() if req["role"] == "source_domain_study" else book()
        if req["role"] == "bookwide_topology_recheck":
            if self.force_replan:
                result={
                    "schema":"deepwrite/bookwide-topology-audit/v1","decision":"REPLAN",
                    "reason":"The actual book contains one neglected source issue that warrants a separate chapter.",
                    "evidence_quote":req["payload"]["book_manuscript"][:50],
                    "chapters":[{"artifact_id":"alpha","title":"First grounded mechanism"},
                                {"artifact_id":"beta","title":"Independent source-boundary problem"}],
                    "old_to_new":[{"old_id":"alpha","new_ids":["alpha","beta"],"treatment":"REWRITTEN"}],
                    "reader_prior_knowledge_contract":{
                        "schema":"deepwrite/reader-prior-contract/v1",
                        "known":["Elementary arithmetic is familiar."],
                        "unknown":["When two groups overlap, they cannot be counted twice."],
                        "concepts":[
                            {"id":"native_pairs","first_explained_in":"alpha","first_used_in":"alpha","prerequisites":[]},
                            {"id":"new_boundaries","first_explained_in":"beta","first_used_in":"beta","prerequisites":["native_pairs"]}],
                        "knowledge_compounding":{"enabled":True,
                            "transfer_goal":"Apply learned source counting to a genuinely new decision problem."}
                    },
                    "book_design":{
                        "why_these_chapters_not_source_outline":"Source dependencies require an independent examination of the new counterexample.",
                        "chapter_contributions":[
                            {"chapter_id":"alpha","source_concept_ids":["native_pairs"],
                             "distinct_reader_change":"Construct a count from source evidence."},
                            {"chapter_id":"beta","source_concept_ids":["native_pairs"],
                             "distinct_reader_change":"Detect invalid extrapolation on a new example."}]
                    }
                }
            else:
                result={"schema":"deepwrite/bookwide-topology-audit/v1", "decision":"KEEP",
                        "reason":"No independently evidenced need to change chapter topology after full book review."}
        elif self.prepared is not None and req["role"] == "book_architecture_discovery":
            result=self.prepared
        return SimpleNamespace(model="synthetic-study-model", provider_kind="fixture",
                               response_id="demo-" + str(len(self.roles)),
                               text=json.dumps(result,ensure_ascii=False),
                               usage={"input_tokens": 50, "output_tokens": 50})


class DefaultInvocationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="deepwrite-one-call-")
        self.base=Path(self.tmp.name)
        self.src=self.base/"source.md"
        self.src.write_text(NATIVE,encoding="utf-8")
        self.request=self.base/"author_request.json"
        self.destination=self.base/"one_project"
        self.data={
            "schema": dw.REQUEST_SCHEMA, "project_id": "one-call-test",
            "wish": "Explore the source's native reasoning and build an original grounded chapter.",
            "working_title": "One-call synthetic case study",
            "reader_goal": "Newcomers understand source meaning; experienced readers question assumptions.",
            "source_files": [str(self.src)],
            "adapter": "codex", "model": "synthetic-study-model",
            "mode": "AUTONOMOUS_FULL_DRAFT", "authorized_scope": "ALL_CANDIDATE_CHAPTERS",
            "min_chapters": 1, "max_chapters": 3, "discovery_token_budget": 10000,
            "token_budget": 100000, "per_call_output_tokens": 1500, "max_revision_rounds": 2
        }
        self.save_request()

    def tearDown(self):
        self.tmp.cleanup()

    def save_request(self):
        self.request.write_text(json.dumps(self.data,ensure_ascii=False),encoding="utf-8")

    def invoke(self):
        study_model=StudyModel()
        result=dw.run(self.request,self.destination,research_model=study_model,
                      writer_model=writer_test.ScriptedModel())
        return result,study_model

    def test_one_command_autoselects_all_gates_to_actual_book(self):
        result,model=self.invoke()
        self.assertEqual(result["status"],"ENGINEERING_FIXTURE_ONLY_NOT_LIVE",result)
        self.assertEqual(model.roles,["source_domain_study","book_architecture_discovery","bookwide_topology_recheck"])
        self.assertEqual(result["chapter_count_proposed"],1)
        self.assertFalse(result["chapter_count_author_approved"])
        self.assertFalse(result["default_formal_main_pointer_changed"])
        self.assertEqual(result["bookwide_topology_recheck"]["status"],"STRUCTURE_KEPT_MODEL_INTERNAL_ONLY")
        self.assertEqual(result["independent_reader_quality"],"NOT_RUN")
        self.assertTrue((self.destination/"writer_project/book.md").is_file())
        config=json.loads((self.destination/"discovery_evidence/research/writer_config.json").read_text())
        self.assertEqual(config["chapters"][0]["artifact_id"],"alpha")
        self.assertTrue(config["modules"]["source_first_architecture"])
        self.assertTrue(config["modules"]["e18_loop"])
        state=json.loads((self.destination/"writer_project/run_state.json").read_text())
        self.assertEqual(state["source_first_intake"]["status"],
                         "PASS_ENGINEERING_ONLY_PROVISIONAL_SOURCE_ARCHITECTURE")
        provenance=json.loads((self.destination/"discovery_evidence/research/STATE.json").read_text())
        self.assertEqual(provenance["insight_origin_provenance"]["human_quality"],"NOT_RUN")
        self.assertEqual(provenance["insight_origin_provenance"]["candidate_count"],3)


    def test_bookwide_replan_creates_new_complete_book_and_preserves_original(self):
        reviewer=StudyModel(force_replan=True)
        result=dw.run(self.request,self.destination,research_model=reviewer,
                      writer_model=writer_test.ScriptedModel())
        self.assertEqual(result["status"],"ENGINEERING_FIXTURE_ONLY_NOT_LIVE",result)
        self.assertEqual(result["bookwide_topology_recheck"]["status"],"REPLAN_DERIVATION_PENDING_HUMAN",result)
        original=self.destination/"writer_project/book.md"
        derived=self.destination/"writer_project_topology_r2/book.md"
        self.assertTrue(original.is_file())
        self.assertTrue(derived.is_file())
        frozen=(self.destination/"discovery_evidence/research/writer_config.json").read_bytes()
        self.assertEqual(len(json.loads(frozen)["chapters"]),1)
        self.assertEqual(len(json.loads((self.destination/"discovery_evidence/topology_r2_writer_config.json").read_text())["chapters"]),2)
        self.assertEqual(result["bookwide_topology_recheck"]["original_book_sha256"],dw.sha(original.read_bytes()))
        self.assertEqual(result["bookwide_topology_recheck"]["derived_book_sha256"],dw.sha(derived.read_bytes()))
        self.assertNotEqual(dw.sha(original.read_bytes()),dw.sha(derived.read_bytes()))
        self.assertEqual(result["independent_reader_quality"],"NOT_RUN")

    def test_assisted_mode_writes_first_sample_then_waits_for_actual_author(self):
        self.data["mode"]="ASSISTED_AUTHOR_GATED"
        self.data["authorized_scope"]="FIRST_SAMPLE_AFTER_DISCOVERY"
        self.save_request()
        result,_=self.invoke()
        self.assertEqual(result["status"],"AWAIT_AUTHOR_REVIEW",result)
        writer=self.destination/"writer_project"
        self.assertTrue((writer/"run_state.json").is_file())
        self.assertFalse((writer/"book.md").exists())
        self.assertEqual(result["author_acceptance"],"NOT_RUN")
        cfg=json.loads((self.destination/"discovery_evidence/research/writer_config.json").read_text())
        self.assertEqual(cfg["execution_contract"]["sample_chapters"],["alpha"])
        self.assertEqual(cfg["execution_contract"]["allowed_unapproved_candidate_chapters"],[])

    def test_author_guidance_is_attributed_not_called_blind(self):
        self.data["author_guidance_source_index"]=0
        self.save_request()
        result,_=self.invoke()
        self.assertEqual(result["status"],"ENGINEERING_FIXTURE_ONLY_NOT_LIVE",result)
        cfg=json.loads((self.destination/"discovery_evidence/research/writer_config.json").read_text())
        self.assertEqual(cfg["author_guidance"]["origin"],"USER_SUPPLIED_PERSPECTIVE")
        receipt=json.loads((self.destination/"discovery_evidence/research/STATE.json").read_text())
        self.assertEqual(receipt["insight_origin_provenance"]["mode"],"AUTHOR_GUIDED")
        self.assertEqual(receipt["insight_origin_provenance"]["true_blind_origin_claim"],"NOT_VERIFIED")

    def test_request_without_author_scope_fails_before_copying_sources(self):
        del self.data["authorized_scope"]
        self.save_request()
        with self.assertRaisesRegex(dw.Blocked,"SCOPE_REQUIRED"):
            dw.prepare(self.request,self.destination)
        self.assertFalse(self.destination.exists())

    def test_fixed_outline_or_manual_modules_is_rejected(self):
        self.data["chapter_titles"]=["a","b"]
        self.save_request()
        with self.assertRaisesRegex(dw.Blocked,"NO_PRESET_OUTLINE"):
            dw.prepare(self.request,self.destination)
        self.assertFalse(self.destination.exists())

    def test_project_cannot_silently_restart_and_overwrite(self):
        self.invoke()
        with self.assertRaisesRegex(dw.Blocked,"PROJECT_ALREADY_EXISTS"):
            dw.prepare(self.request,self.destination)

    def test_request_source_must_be_outside_public_repo(self):
        self.data["source_files"]=[str(dw.DEEPWRITE/"CURRENT.json")]
        self.save_request()
        with self.assertRaisesRegex(dw.Blocked,"INSIDE_PUBLIC_CODE"):
            dw.prepare(self.request,self.destination)

    def test_no_api_key_ever_looks_like_real_model_success(self):
        result,_=self.invoke()
        self.assertEqual(result["real_model_verified"],False)
        self.assertEqual(dw.status(self.destination)["project_status"],"ENGINEERING_FIXTURE_ONLY_NOT_LIVE")

if __name__ == "__main__":
    unittest.main()
