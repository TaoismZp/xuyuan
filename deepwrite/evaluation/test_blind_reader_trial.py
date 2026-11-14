#!/usr/bin/env python3
"""External reader experiment packaging tests; no simulated human evidence."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from blind_reader_trial import TrialBlocked, prepare, collect


def h(raw):
    return hashlib.sha256(raw).hexdigest()


class TrialTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="deepwrite-trial-")
        self.root=Path(self.tmp.name)
        self.a=self.root/"version_old.md"
        self.b=self.root/"version_new.md"
        self.a.write_text("Original evidence grounded manuscript. " * 30)
        self.b.write_text("Revised manuscript studies a new mechanism. " * 30)
        self.packet=self.root/"packet"
        self.secret=self.root/"operator_only"
        self.cfg={
            "schema": "deepwrite/paired-reader-trial/v1",
            "project_id": "case-0001-blind-reading",
            "reader_task": "Read both complete manuscripts for understanding and structural depth.",
            "novel_transfer_question": "How does the learned mechanism apply to a different unseen situation?",
            "novel_transfer_expected_mechanism": "Require the respondent to infer a new decision consequence.",
            "novel_transfer_counterexample": "Different conditions can invalidate a previous useful inference.",
            "operator_blinding_seed": "A secret seed that the reviewer never sees 00001",
            "works": {
                "baseline": {"path": str(self.a), "sha256": h(self.a.read_bytes())},
                "candidate": {"path": str(self.b), "sha256": h(self.b.read_bytes())}
            }
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_packet_contains_only_blinded_works_and_no_answer_key(self):
        result=prepare(self.cfg,self.packet,self.secret)
        self.assertEqual(result["status"],"PACKET_PREPARED_READER_ASSESSMENT_NOT_RUN")
        self.assertEqual(result["human_readers"],0)
        self.assertEqual(result["quality_result"],"UNVERIFIED")
        self.assertFalse((self.packet/"MAPPING_PRIVATE.json").exists())
        self.assertTrue((self.secret/"MAPPING_PRIVATE.json").exists())
        self.assertNotEqual((self.packet/"A.md").read_text(),(self.packet/"B.md").read_text())
        self.assertIn("跨情境", (self.packet/"READER_TASK.md").read_text())
        self.assertNotIn("version_old", (self.packet/"READER_TASK.md").read_text())

    def test_tampered_source_blocks_creation(self):
        self.a.write_text("Changed contents and more words. "*10)
        with self.assertRaisesRegex(TrialBlocked,"BYTES_CHANGED"):
            prepare(self.cfg,self.packet,self.secret)
        self.assertFalse(self.packet.exists())

    def test_same_book_not_valid_comparison(self):
        self.cfg["works"]["candidate"]=self.cfg["works"]["baseline"]
        with self.assertRaisesRegex(TrialBlocked,"IDENTICAL_WORKS"):
            prepare(self.cfg,self.packet,self.secret)

    def test_packet_and_key_cannot_share_parent_scope(self):
        with self.assertRaisesRegex(TrialBlocked,"KEY_MUST_BE_OUTSIDE"):
            prepare(self.cfg,self.packet,self.packet/"secret")

    def test_no_human_response_cannot_be_counted_as_quality_result(self):
        prepare(self.cfg,self.packet,self.secret)
        with self.assertRaisesRegex(TrialBlocked,"REAL_READER_RESPONSES_REQUIRED"):
            collect(self.packet,self.secret,[],self.root/"result.json")

    def test_reader_response_must_be_blinded_and_located(self):
        prepare(self.cfg,self.packet,self.secret)
        ans=self.root/"real_reader_input.json"
        data={"reader_id":"reader-01","saw_private_mapping":False,
              "independent_reader_attestation":True,"preference":"B",
              "novice":"The second book was more readable in the new explanation.",
              "practitioner":"The comparison changes how I think about outcomes.",
              "expert":"A crucial failure boundary is explicitly explained.",
              "transfer_answer":"I can apply the source concept under another condition.",
              "negative_findings":"I found a weak citation that must be repaired."}
        ans.write_text(json.dumps(data))
        out=self.root/"result.json"
        result=collect(self.packet,self.secret,[ans],out)
        self.assertEqual(result["recorded_responses"],1)
        self.assertEqual(result["votes"]["B"],1)
        self.assertEqual(result["reader_transfer_success"],"REQUIRES_EXTERNAL_JUDGING_OF_CONTENT")
        self.assertEqual(result["reader_independence"],"SELF_ATTESTED_NOT_AUTHENTICATED")
        self.assertTrue(out.is_file())

    def test_claimed_saw_key_blocks_blind_validity(self):
        prepare(self.cfg,self.packet,self.secret)
        ans=self.root/"input.json"
        ans.write_text(json.dumps({"reader_id":"a","saw_private_mapping":True,
                                   "independent_reader_attestation":True}))
        with self.assertRaisesRegex(TrialBlocked,"NOT_DECLARED_BLIND"):
            collect(self.packet,self.secret,[ans],self.root/"result.json")

    def test_packet_modified_after_release_blocks_scoring(self):
        prepare(self.cfg,self.packet,self.secret)
        (self.packet/"A.md").write_text("tampered")
        with self.assertRaisesRegex(TrialBlocked,"PACKET_CHANGED"):
            collect(self.packet,self.secret,[self.a],self.root/"result.json")

if __name__=="__main__":
    unittest.main()
