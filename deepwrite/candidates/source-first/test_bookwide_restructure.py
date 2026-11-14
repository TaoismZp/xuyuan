#!/usr/bin/env python3
"""Bounded post-book topology tests: no real model quality is certified."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from bookwide_restructure import validate, derive_config, make_private_derived_project, Blocked


BOOK="# Frozen full book\n\nAn earlier claim uses a familiar example as evidence for a decision.\n"
QUOTE="An earlier claim uses a familiar example"
SOURCE=b"Public fixture only: two pairs contain four objects.\n"


def good_config():
    return {
        "run_id":"synthetic-original",
        "chapters":[{"artifact_id":"alpha","title":"Alpha source mechanism"}],
        "execution_contract":{"mode":"AUTONOMOUS_FULL_DRAFT"},
        "reader_prior_knowledge_contract":{"schema":"deepwrite/reader-prior-contract/v1",
            "known":["counting"],"unknown":["dependent examples"],
            "concepts":[{"id":"native_pairs","first_explained_in":"alpha",
                         "first_used_in":"alpha","prerequisites":[]}]},
        "source_first_architecture":{"source_concepts":[{"id":"native_pairs"}],
            "book_design":{"status":"PROVISIONAL",
                           "why_these_chapters_not_source_outline":"One grounded source chapter",
                           "chapter_contributions":[{"chapter_id":"alpha",
                             "source_concept_ids":["native_pairs"],
                             "distinct_reader_change":"Verify original evidence first"}]}},
        "sources":[{"path":"sources/material.md","sha256":hashlib.sha256(SOURCE).hexdigest()}]
    }


def replan():
    return {
        "schema":"deepwrite/bookwide-topology-audit/v1",
        "decision":"REPLAN",
        "reason":"The second question genuinely deserves its own evidence and separate chapter mechanism.",
        "evidence_quote":QUOTE,
        "chapters":[{"artifact_id":"alpha","title":"Alpha source mechanism"},
                    {"artifact_id":"beta","title":"Beta independent problem"}],
        "old_to_new":[{"old_id":"alpha","new_ids":["alpha","beta"],"treatment":"REWRITTEN"}],
        "reader_prior_knowledge_contract":{
            "schema":"deepwrite/reader-prior-contract/v1",
            "known":["counting"],"unknown":["dependent examples"],
            "concepts":[
                {"id":"native_pairs","first_explained_in":"alpha",
                 "first_used_in":"alpha","prerequisites":[]},
                {"id":"new_condition","first_explained_in":"beta",
                 "first_used_in":"beta","prerequisites":["native_pairs"]}]},
        "book_design":{
            "why_these_chapters_not_source_outline":"Separate the source mechanism from the new distinct reader problem.",
            "chapter_contributions":[
                {"chapter_id":"alpha","source_concept_ids":["native_pairs"],
                 "distinct_reader_change":"Ground a conclusion in first principles."},
                {"chapter_id":"beta","source_concept_ids":["native_pairs"],
                 "distinct_reader_change":"Apply first principles to an unseen counterexample."}]}
    }


class BookwideTopologyTests(unittest.TestCase):
    def test_keep_is_legitimate_not_forced_rewrite(self):
        p={"schema":"deepwrite/bookwide-topology-audit/v1","decision":"KEEP",
           "reason":"No structural duplication or source mechanism has been shown to justify restructuring."}
        self.assertEqual(validate(p,good_config(),BOOK)["decision"],"KEEP")

    def test_actual_replan_requires_original_evidence(self):
        p=replan()
        x=validate(p,good_config(),BOOK)
        self.assertEqual(x["decision"],"REPLAN")
        self.assertEqual(x["new_chapters"],2)
        new=derive_config(p,good_config())
        self.assertEqual(len(new["chapters"]),2)
        self.assertEqual(new["run_id"],"synthetic-original-topology-r2")
        self.assertEqual(new["source_first_architecture"]["book_design"]["status"],"PROVISIONAL")

    def test_missing_book_quote_blocks(self):
        p=replan();p["evidence_quote"]="this text has never appeared in the original book"
        with self.assertRaisesRegex(Blocked,"LOCATED_OLD_TEXT_EVIDENCE"):
            validate(p,good_config(),BOOK)

    def test_no_rewrite_for_same_structure(self):
        p=replan()
        p["chapters"]=good_config()["chapters"]
        with self.assertRaisesRegex(Blocked,"NO_ACTUAL_CHANGE"):
            validate(p,good_config(),BOOK)

    def test_every_previous_contribution_must_be_accounted(self):
        p=replan();p["old_to_new"]=[]
        with self.assertRaisesRegex(Blocked,"ALL_ORIGINAL_CHAPTERS"):
            validate(p,good_config(),BOOK)

    def test_no_fake_author_signoff(self):
        p=replan();p["human_acceptance"]="PASS"
        with self.assertRaisesRegex(Blocked,"SELF_CERTIFY"):
            validate(p,good_config(),BOOK)

    def test_original_author_scope_must_be_all_candidacy(self):
        cfg=good_config();cfg["execution_contract"]["mode"]="ASSISTED_AUTHOR_GATED"
        with self.assertRaisesRegex(Blocked,"FULL_DRAFT_AUTHORIZATION"):
            validate(replan(),cfg,BOOK)

    def test_revised_concept_dependencies_must_exist(self):
        p=replan()
        p["reader_prior_knowledge_contract"]["concepts"][1]["prerequisites"]=["NOT_FOUND"]
        with self.assertRaisesRegex(ValueError,"UNKNOWN_OR_SELF"):
            validate(p,good_config(),BOOK)

    def test_derived_project_copies_exact_bytes_without_modifying_original(self):
        with tempfile.TemporaryDirectory(prefix="deepwrite-private-derived-") as td:
            old=Path(td)/"old_project"
            (old/"sources").mkdir(parents=True)
            (old/"sources/material.md").write_bytes(SOURCE)
            (old/"book.md").write_text(BOOK)
            new=Path(td)/"derived_project"
            cfg=good_config()
            snap=make_private_derived_project(old,new,cfg,derive_config(replan(),cfg))
            self.assertEqual(snap["status"],"DERIVED_PROJECT_SOURCE_BYTES_FROZEN")
            self.assertEqual((old/"book.md").read_text(),BOOK)
            self.assertFalse((new/"book.md").exists())
            self.assertEqual((new/"sources/material.md").read_bytes(),SOURCE)
            with self.assertRaisesRegex(Blocked,"ALREADY_EXISTS"):
                make_private_derived_project(old,new,cfg,derive_config(replan(),cfg))

    def test_changed_source_fails_before_use(self):
        with tempfile.TemporaryDirectory(prefix="deepwrite-derivation-tamper-") as td:
            old=Path(td)/"old"
            (old/"sources").mkdir(parents=True)
            (old/"sources/material.md").write_bytes(b"TAMPERED")
            (old/"book.md").write_text(BOOK)
            with self.assertRaisesRegex(Blocked,"SOURCE_BYTES_CHANGED"):
                make_private_derived_project(old,Path(td)/"new",good_config(),good_config())

if __name__=="__main__":
    unittest.main()
