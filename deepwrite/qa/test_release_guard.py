import copy, unittest
from release_guard import evaluate

A="a"*64
C="c"*40


def sample(mode="CANDIDATE_OPT_IN"):
    return {"schema":"deepwrite/release-evidence/v0.1", "requested_channel":mode, "immutable_baseline":True,
      "baseline":{"spec_git_commit":C,"artifact_sha256":A,"evaluation_sha256":A},
      "candidate":{"spec_git_commit":C,"artifact_sha256":A,"evaluation_sha256":A},
      "rollback_plan":{"verified_checkpoint_sha256":A,"preserve_failed_candidate":True},
      "gates":{"engineering":"PASS","content_quality":"PENDING","author_acceptance":"PENDING","external_validation":"NOT_RUN"},
      "per_project_explicit_opt_in":True,"evidence":{},"author_promotion_approval":False}

class ReleaseGateTests(unittest.TestCase):
    def test_malformed_containers_are_blocked(self):
        for x in ([], None, {"baseline":None}, {"rollback_plan":[]}, {"gates":"PASS"}, {"evidence":False}):
            with self.subTest(value=x): self.assertTrue(evaluate(x))
    def test_string_false_is_not_authorization_or_immutability(self):
        for key in ("immutable_baseline", "per_project_explicit_opt_in"):
            x=sample(); x[key]="false"; self.assertTrue(evaluate(x))
    def test_can_opt_in_with_pending_quality_and_label_as_candidate(self): self.assertEqual(evaluate(sample()), [])
    def test_cannot_opt_in_without_user_project_choice(self):
        x=sample(); x["per_project_explicit_opt_in"]=False; self.assertIn("explicit per-project opt-in required",evaluate(x))
    def test_cannot_promote_quality_pending(self):
        self.assertTrue(any("all 4" in i for i in evaluate(sample("PROMOTION_REQUEST"))))
    def test_cannot_promote_just_by_fake_full_gates(self):
        x=sample("PROMOTION_REQUEST");x["gates"]={k:"PASS" for k in x["gates"]};self.assertTrue(evaluate(x))
    def test_promote_structurally_with_all_evidence_still_needs_external_confirmation(self):
        x=sample("PROMOTION_REQUEST");x["gates"]={k:"PASS" for k in x["gates"]};x["evidence"]={"actual_reader_count":2,"independent_topic_count":3,"regression_non_degradation":True};x["author_promotion_approval"]=True;self.assertEqual(evaluate(x),[])
    def test_cannot_rollback_destructively(self):
        x=sample("ROLLBACK");x["rollback_plan"]["preserve_failed_candidate"]=False;self.assertTrue(evaluate(x))
    def test_missing_checkpoint_blocks_even_experiment(self):
        x=sample();x["rollback_plan"]["verified_checkpoint_sha256"]="BAD";self.assertTrue(evaluate(x))
    def test_wrong_git_identity_blocks(self):
        x=sample();x["candidate"]["spec_git_commit"]="main";self.assertTrue(evaluate(x))
    def test_invalid_gate_blocks(self):
        x=sample();x["gates"]["content_quality"]="GREAT";self.assertTrue(evaluate(x))
if __name__ == "__main__": unittest.main()
