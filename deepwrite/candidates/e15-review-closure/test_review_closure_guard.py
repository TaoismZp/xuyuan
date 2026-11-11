"""Real-file regression tests. Synthetic material only; not book quality tests."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

g = module("guard_v1", HERE / "review_closure_guard.py")
legacy = module("legacy_pr13", HERE / "tests/fixtures/review_closure_guard_pr13.py")

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

class Closeout(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before = "# Chapter\n\nThe incorrect color is red.\n\nAn unchanged ending."
        self.after = "# Chapter\n\nThe corrected color is blue.\n\nAn unchanged ending."
        self.make()

    def location(self, text, paragraph=2):
        return {"paragraph": paragraph, "sha256": digest(g.paragraphs(text)[paragraph-1])}

    def make(self):
        (self.root/"before.md").write_text(self.before, encoding="utf-8")
        (self.root/"after.md").write_text(self.after, encoding="utf-8")
        self.record = {
            "schema": g.SCHEMA,
            "artifacts": [{"artifact_id":"ch1",
                          "baseline":{"path":"before.md","sha256":digest(self.before)},
                          "candidate":{"path":"after.md","sha256":digest(self.after)}}],
            "coverage":["ch1"],
            "findings":[{
                "id":"F1","artifact_id":"ch1","kind":"computable","severity":"MAJOR","status":"CLOSED",
                "issue":"The chapter wrongly says red.","evidence":"Actual located text was replaced.",
                "location":{"baseline":self.location(self.before),"candidate":self.location(self.after)},
                "assertion":{"op":"not_contains","value":"red."}}]}

    def check(self, expected=None):
        return g.check(self.record, self.root, expected)

    def assertHold(self):
        self.assertEqual(self.check()["status"], "HOLD")

    def test_legacy_empty_findings_false_pass(self):
        obj={"schema":"deepwrite/review-closeout/v0",
             "baseline_sha256":"a"*64,"candidate_sha256":"b"*64,
             "comparison":{"baseline_read":True,"candidate_read":True,
                           "reviewed_units":["chapter"],"comparison_rationale":"Claim only"},
             "findings":[]}
        self.assertEqual(legacy.check(obj)["status"],"PASS_STRUCTURAL_ONLY")
        self.assertEqual(g.check(obj,self.root)["status"],"HOLD")

    def test_legacy_fake_closed_evidence_false_pass(self):
        obj={"schema":"deepwrite/review-closeout/v0",
             "baseline_sha256":"a"*64,"candidate_sha256":"b"*64,
             "comparison":{"baseline_read":True,"candidate_read":True,
                           "reviewed_units":["chapter"],"comparison_rationale":"Claim only"},
             "findings":[{"id":"bad","severity":"MAJOR","status":"CLOSED",
                          "location":"somewhere","issue":"known defect",
                          "revised_sha256":"b"*64,"recheck_evidence":"I fixed it"}]}
        self.assertEqual(legacy.check(obj)["status"],"PASS_STRUCTURAL_ONLY")
        self.assertEqual(g.check(obj,self.root)["status"],"HOLD")

    def test_real_text_fix_passes(self):
        r=self.check()
        self.assertEqual(r["status"],"PASS_STRUCTURAL_ONLY")
        self.assertFalse(r["findings"][0]["assertion"]["baseline"]["passed"])
        self.assertTrue(r["findings"][0]["assertion"]["candidate"]["passed"])
        self.assertEqual(r["semantic_status"],"NOT_CERTIFIED")
        self.assertEqual(r["human_acceptance"],"NOT_ESTABLISHED")

    def test_forged_artifact_sha(self):
        self.record["artifacts"][0]["candidate"]["sha256"]="f"*64
        self.assertHold()

    def test_forged_baseline_sha(self):
        self.record["artifacts"][0]["baseline"]["sha256"]="f"*64
        self.assertHold()

    def test_missing_file(self):
        (self.root/"after.md").unlink()
        self.assertHold()

    def test_empty_findings(self):
        self.record["findings"]=[]
        self.assertHold()

    def test_coverage_missing(self):
        self.record["coverage"]=[]
        self.assertHold()

    def test_coverage_duplicate(self):
        self.record["coverage"]=["ch1","ch1"]
        self.assertHold()

    def test_coverage_artifact_without_located_review(self):
        self.record["artifacts"].append({"artifact_id":"ch2",**{k:v for k,v in self.record["artifacts"][0].items() if k!="artifact_id"}})
        self.record["coverage"].append("ch2")
        self.assertHold()

    def test_missing_location(self):
        del self.record["findings"][0]["location"]
        self.assertHold()

    def test_fake_paragraph_sha(self):
        self.record["findings"][0]["location"]["candidate"]["sha256"]="a"*64
        self.assertHold()

    def test_no_change_but_claim_closed(self):
        self.after=self.before
        self.make()
        self.assertHold()

    def test_whitespace_only(self):
        self.after=self.before.replace("incorrect color","incorrect\n color")
        self.make()
        self.assertHold()

    def test_newline_and_pointer_move_bypass(self):
        self.after=self.before.replace("red.","r\ned.")
        self.make()
        self.record["findings"][0]["location"]["candidate"]=self.location(self.after,3)
        self.assertHold()

    def test_fixed_other_paragraph_but_defect_remains(self):
        self.after=self.before.replace("An unchanged ending.","A new ending.")
        self.make()
        self.record["findings"][0]["location"]["candidate"]=self.location(self.after,3)
        self.assertHold()

    def test_old_defect_moved_elsewhere(self):
        self.after="# Chapter\n\nCorrected here: blue.\n\nStill red."
        self.make()
        self.assertHold()

    def test_baseline_location_unrelated(self):
        self.record["findings"][0]["location"]["baseline"]=self.location(self.before,3)
        self.assertHold()

    def test_contains_location_must_contain_required_literal(self):
        self.record["findings"][0]["assertion"]={"op":"contains","value":"blue."}
        self.record["findings"][0]["location"]["candidate"]=self.location(self.after,3)
        self.assertHold()

    def test_literal_count(self):
        self.record["findings"][0]["assertion"]={"op":"literal_count","value":"red.","count":0}
        self.assertEqual(self.check()["status"],"PASS_STRUCTURAL_ONLY")

    def test_literal_count_false_positive_boolean(self):
        self.record["findings"][0]["assertion"]={"op":"literal_count","value":"red.","count":False}
        self.assertHold()

    def test_forbidden_eval_op(self):
        self.record["findings"][0]["assertion"]={"op":"eval","value":"print('unsafe')"}
        self.assertHold()

    def test_keep_correct_original_without_forcing_edit(self):
        self.before=self.after="# Chapter\n\nCorrect blue.\n\nEnding."
        self.make()
        f=self.record["findings"][0]
        f.update(status="KEEP",reason="The major allegation is contradicted by actual text.")
        self.assertEqual(self.check()["status"],"PASS_STRUCTURAL_ONLY")

    def test_keep_without_reason(self):
        self.record["findings"][0]["status"]="KEEP"
        self.assertHold()

    def test_keep_wrong_original_is_blocked(self):
        self.record["findings"][0].update(status="KEEP",reason="Ignore contrary text")
        self.assertHold()

    def semantic(self, status="CLOSED"):
        f=self.record["findings"][0]
        f.update(kind="model_review",status=status)
        f.pop("assertion")
        f["review"]={"verdict":status,"reviewer":"model fixture; not a human",
                     "rationale":"Located prose was reread.",
                     "artifact_sha256":digest(self.after),
                     "location_sha256":self.location(self.after)["sha256"]}
        return f

    def test_semantic_record_does_not_certify_semantics(self):
        self.semantic()
        r=self.check()
        self.assertEqual(r["status"],"PASS_STRUCTURAL_ONLY")
        self.assertEqual(r["semantic_status"],"MODEL_REVIEW_REQUIRED")
        self.assertEqual(r["model_review_required"],["F1"])

    def test_semantic_review_must_bind_current_artifact(self):
        f=self.semantic()
        f["review"]["artifact_sha256"]="a"*64
        self.assertHold()

    def test_semantic_no_change_is_not_repair(self):
        self.after=self.before
        self.make()
        self.semantic()
        self.assertHold()

    def test_semantic_keep_does_not_require_rewrite(self):
        self.before=self.after="# Chapter\n\nCorrect statement.\n\nEnding."
        self.make()
        f=self.semantic("KEEP");f["reason"]="The allegation is unsupported; keep original."
        self.assertEqual(self.check()["status"],"PASS_STRUCTURAL_ONLY")

    def test_open_major_blocks(self):
        self.record["findings"][0]["status"]="OPEN"
        self.assertHold()

    def test_frozen_omission(self):
        expected=copy.deepcopy(self.record["findings"])
        expected.append({**expected[0],"id":"F2"})
        self.assertEqual(self.check(expected)["status"],"HOLD")

    def test_frozen_redefinition(self):
        expected=copy.deepcopy(self.record["findings"])
        self.record["findings"][0]["assertion"]["value"]="different"
        self.assertEqual(self.check(expected)["status"],"HOLD")

    def test_frozen_severity_downgrade(self):
        expected=copy.deepcopy(self.record["findings"])
        self.record["findings"][0]["severity"]="NOTE"
        self.assertEqual(self.check(expected)["status"],"HOLD")

    def test_malformed_frozen_location_fails_closed(self):
        expected=copy.deepcopy(self.record["findings"])
        expected[0]["location"]=None
        self.assertEqual(self.check(expected)["status"],"HOLD")

    def test_parent_traversal(self):
        self.record["artifacts"][0]["candidate"]["path"]="../after.md"
        self.assertHold()

    def test_absolute_path(self):
        self.record["artifacts"][0]["candidate"]["path"]=str(self.root/"after.md")
        self.assertHold()

    def test_symlink(self):
        (self.root/"alias.md").symlink_to(self.root/"after.md")
        self.record["artifacts"][0]["candidate"]["path"]="alias.md"
        self.assertHold()

    def test_actual_restored_bytes_rechecked(self):
        good=self.check()
        self.assertEqual(good["status"],"PASS_STRUCTURAL_ONLY")
        (self.root/"restored.md").write_bytes((self.root/"after.md").read_bytes())
        self.record["artifacts"][0]["candidate"]["path"]="restored.md"
        self.assertEqual(self.check()["status"],"PASS_STRUCTURAL_ONLY")
        (self.root/"restored.md").write_text(self.before)
        self.assertHold()

    def test_cli(self):
        p=self.root/"record.json";p.write_text(json.dumps(self.record))
        r=subprocess.run([sys.executable,str(HERE/"review_closure_guard.py"),str(p),"--root",str(self.root)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr+r.stdout)

    def test_cli_frozen_manifest_external_hash(self):
        p=self.root/"record.json";p.write_text(json.dumps(self.record))
        frozen=self.root/"frozen.json";frozen.write_text(json.dumps(self.record["findings"]))
        args=[sys.executable,str(HERE/"review_closure_guard.py"),str(p),"--root",str(self.root),"--expected-findings",str(frozen)]
        r=subprocess.run(args,capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        r=subprocess.run(args+["--expected-findings-sha256",hashlib.sha256(frozen.read_bytes()).hexdigest()],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr+r.stdout)

    def test_invalid_record_type(self):
        self.assertEqual(g.check([],self.root)["status"],"HOLD")

    def test_legacy_source_blob_identity(self):
        b=(HERE/"tests/fixtures/review_closure_guard_pr13.py").read_bytes()
        expected="a086c03a24730df79343763523cca8d3f7a4c8b9"
        self.assertEqual(hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest(),expected)

if __name__=="__main__":
    unittest.main()
