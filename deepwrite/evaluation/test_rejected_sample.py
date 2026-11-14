#!/usr/bin/env python3
"""Independent negative controls plus source-first E18 fixture: no human quality claim."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent.parent


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


rewrite=load("deepwrite_rejected_sample",HERE/"rejection_rebuild.py")
fixture=load("deepwrite_rejected_fixture",HERE/"test_default.py")
dw=fixture.dw


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class RejectedSampleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="deepwrite-author-rejected-")
        self.home=Path(self.temp.name)
        self.source=self.home/"native.md"
        self.source.write_text(fixture.NATIVE,encoding="utf-8")
        self.request=self.home/"first_request.json"
        self.original=self.home/"original"
        self.doc={
            "schema":dw.REQUEST_SCHEMA,"project_id":"original-sample",
            "wish":"Explain a truly native source mechanism and then its independent decision consequence.",
            "working_title":"Source first test book",
            "reader_goal":"Explain the native question in plain prose without generic mechanical analogies.",
            "source_files":[str(self.source)],"adapter":"codex",
            "model":"synthetic-study-model",
            "mode":"ASSISTED_AUTHOR_GATED",
            "authorized_scope":"FIRST_SAMPLE_AFTER_DISCOVERY",
            "min_chapters":1,"max_chapters":2,"discovery_token_budget":10000,
            "token_budget":100000,"per_call_output_tokens":1500,
            "max_revision_rounds":2}
        self.request.write_text(json.dumps(self.doc,ensure_ascii=False),encoding="utf-8")
        self.first=dw.run(self.request,self.original,research_model=fixture.StudyModel(),
                          writer_model=fixture.writer_test.ScriptedModel())
        self.assertEqual(self.first["status"],"AWAIT_AUTHOR_REVIEW",self.first)
        self.orig_state_file=self.original/"writer_project/run_state.json"
        self.orig_state_raw=self.orig_state_file.read_bytes()
        self.orig_state=json.loads(self.orig_state_raw)
        self.orig_config=json.loads((self.original/"discovery_evidence/research/writer_config.json").read_bytes())
        self.sample=self.orig_config["execution_contract"]["sample_chapters"][0]
        self.chapter=self.original/"writer_project"/self.orig_state["completed"]["close_"+self.sample][self.sample]
        self.chapter_raw=self.chapter.read_bytes()
        self.receipt_path=self.home/"rejection.json"
        self.newreq=self.home/"second_request.json"
        self.newroot=self.home/"replacement"
        self.receipt={
            "schema":rewrite.REJECTION_SCHEMA,"status":"REJECTED",
            "project_id":self.doc["project_id"],"new_project_id":"sample-second-try",
            "sample_artifact_id":self.sample,
            "sample_artifact_sha256":sha(self.chapter_raw),
            "expected_run_state_sha256":sha(self.orig_state_raw),
            "execution_contract_sha256":self.orig_state["execution_contract_sha256"],
            "reason":"The story lacks a concrete human decision and repeats a familiar explanation without a new reader insight.",
            "verification":{"method":"EXTERNAL_OPERATOR_ATTESTATION",
                            "model_generated":False,
                            "evidence_reference":"synthetic test user comment, not a real author"}
        }
        self.record()

    def tearDown(self):
        self.temp.cleanup()

    def record(self):
        self.receipt_path.write_text(json.dumps(self.receipt,ensure_ascii=False),encoding="utf-8")

    def prepare(self):
        return rewrite.prepare(self.original,self.receipt_path,
            sha(self.receipt_path.read_bytes()),sha(self.orig_state_file.read_bytes()),
            self.newreq,self.newroot)

    def test_frozen_original_sample_rejected_then_research_restart_prepared(self):
        out=self.prepare()
        self.assertEqual(out["status"],"REJECTED_SAMPLE_RESET_PREPARED_MODEL_NOT_RUN")
        self.assertEqual(out["old_chapter_sha256"],sha(self.chapter_raw))
        self.assertFalse(self.newroot.exists())
        request=json.loads(self.newreq.read_text())
        self.assertEqual(request["project_id"],"sample-second-try")
        self.assertEqual(request["source_files"],
                         [str(self.original/"writer_project/sources/native_001.md")])
        self.assertNotIn(self.chapter_raw.decode(),self.newreq.read_text())
        self.assertNotIn(self.orig_config["chapters"][0]["title"],self.newreq.read_text())
        self.assertEqual(self.chapter.read_bytes(),self.chapter_raw)
        self.assertEqual(self.orig_state_file.read_bytes(),self.orig_state_raw)
        receipt=json.loads(Path(out["provenance_file"]).read_text())
        self.assertEqual(receipt["new_model_calls"],"NOT_RUN")
        self.assertEqual(receipt["source_count"],1)

    def test_actual_source_discovery_and_fresh_E18_writer_reexecute_as_fixture(self):
        out=self.prepare()
        new_book=fixture.book()
        new_book["chapters"][0]["title"]="Unexpected independent source mechanism after real evidence"
        result=dw.run(self.newreq,self.newroot,research_model=fixture.StudyModel(prepared=new_book),
                      writer_model=fixture.writer_test.ScriptedModel())
        self.assertEqual(result["status"],"AWAIT_AUTHOR_REVIEW",result)
        checked=rewrite.assess_new_run(out,result)
        self.assertEqual(checked["status"],"ENGINEERING_FIXTURE_ONLY_NOT_LIVE",checked)
        self.assertEqual(checked["human_acceptance"],"PENDING")
        self.assertEqual(checked["quality"],"UNVERIFIED")
        self.assertTrue((self.newroot/"discovery_evidence/research/STATE.json").is_file())
        self.assertTrue((self.newroot/"writer_project/run_state.json").is_file())
        self.assertEqual(self.chapter.read_bytes(),self.chapter_raw)
        self.assertEqual(self.orig_state_file.read_bytes(),self.orig_state_raw)

    def test_new_chapter_exact_same_title_blocks_semantic_promotion(self):
        out=self.prepare()
        result=dw.run(self.newreq,self.newroot,research_model=fixture.StudyModel(),
                      writer_model=fixture.writer_test.ScriptedModel())
        checked=rewrite.assess_new_run(out,result)
        self.assertEqual(checked["status"],"BLOCKED_REJECTED_FIRST_CHAPTER_TITLE_REUSED")

    def test_author_acceptance_or_model_generated_rejection_never_accepted(self):
        self.receipt["status"]="APPROVED"
        self.record()
        with self.assertRaisesRegex(rewrite.Blocked,"NOT_MATCHED"):
            self.prepare()
        self.receipt["status"]="REJECTED"
        self.receipt["verification"]["model_generated"]=True
        self.record()
        with self.assertRaisesRegex(rewrite.Blocked,"NOT_MATCHED"):
            self.prepare()

    def test_other_chapter_or_wrong_mismatched_artifact_must_fail(self):
        self.receipt["sample_artifact_sha256"]="0"*64
        self.record()
        with self.assertRaisesRegex(rewrite.Blocked,"NOT_MATCHED"):
            self.prepare()
        self.receipt["sample_artifact_sha256"]=sha(self.chapter_raw)
        self.receipt["sample_artifact_id"]="different_artifact"
        self.record()
        with self.assertRaisesRegex(rewrite.Blocked,"NOT_MATCHED"):
            self.prepare()

    def test_real_user_brief_rejection_is_accepted_not_forced_to_write_an_essay(self):
        self.receipt["reason"]="写得不好，很普通"
        self.record()
        out=self.prepare()
        self.assertEqual(out["status"],"REJECTED_SAMPLE_RESET_PREPARED_MODEL_NOT_RUN")
        self.assertFalse(self.newroot.exists())

    def test_empty_non_decision_is_not_valid_author_feedback(self):
        self.receipt["reason"]="不"
        self.record()
        with self.assertRaisesRegex(rewrite.Blocked,"SUBSTANTIVE_AUTHOR_FEEDBACK_REQUIRED"):
            self.prepare()

    def test_external_state_sha_and_receipt_hash_must_match(self):
        with self.assertRaisesRegex(rewrite.Blocked,"SHA_MISMATCH_AUTHOR_RECEIPT"):
            rewrite.prepare(self.original,self.receipt_path,"f"*64,
                sha(self.orig_state_raw),self.newreq,self.newroot)
        with self.assertRaisesRegex(rewrite.Blocked,"SHA_MISMATCH_STATE"):
            rewrite.prepare(self.original,self.receipt_path,sha(self.receipt_path.read_bytes()),
                "f"*64,self.newreq,self.newroot)

    def test_manual_chapter_is_not_a_v03_engine_sample(self):
        self.orig_state_file.unlink()
        with self.assertRaisesRegex(rewrite.Blocked,"OLD_ENGINE_RUN_STATE_REQUIRED"):
            self.prepare()
        self.assertFalse(self.newreq.exists())

    def test_source_tamper_fails_without_creating_new_project(self):
        (self.original/"writer_project/sources/native_001.md").write_text("TAMPERED")
        with self.assertRaisesRegex(rewrite.Blocked,"SHA_MISMATCH_SOURCE"):
            self.prepare()
        self.assertFalse(self.newreq.exists())

    def test_old_author_gate_and_project_name_are_invariants(self):
        self.receipt["new_project_id"]=self.doc["project_id"]
        self.record()
        with self.assertRaisesRegex(rewrite.Blocked,"UNIQUE_NEW_PROJECT_ID"):
            self.prepare()
        self.receipt["new_project_id"]="newest-sample"
        self.record()
        self.prepare()
        with self.assertRaisesRegex(rewrite.Blocked,"NO_OVERWRITE"):
            self.prepare()

    def test_no_rejected_run_can_claim_real_model_pass_without_trace(self):
        out=self.prepare()
        checked=rewrite.assess_new_run(out,{"status":"FAKE_LIVE_SUCCESS"})
        self.assertEqual(checked["status"],"NEW_RUN_BLOCKED_OR_UNVERIFIED")
        self.assertEqual(checked["quality"],"UNVERIFIED")


if __name__=="__main__":
    unittest.main()
