"""Synthetic API fixtures and real temporary Git objects; not live approval."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from github_authorization import owner_authorization, runtime_ci, evaluate, enable_auto_merge, protected_configuration, trusted_controller_source
from release_verify import verify_transition


def h(raw): return hashlib.sha256(raw).hexdigest()
def j(obj): return (json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode()


class OwnerAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.sha="a"*40
        self.repository={"full_name":"owner/repo","owner":{"type":"User","login":"owner"}}
        self.pull={"state":"open","draft":False,"base":{"ref":"main"},
            "head":{"sha":self.sha,"repo":{"full_name":"owner/repo"}}}
        self.comment={"id":1,"created_at":"2026-11-12T00:00:00Z",
            "user":{"type":"User","login":"owner"},
            "body":"/deepwrite authorize ENGINEERING_PATCH "+self.sha}
        self.check={"id":1,"name":"activation-and-runtime-regressions","head_sha":self.sha,
            "app":{"id":15368},"status":"completed","conclusion":"success"}

    def auth(self,comments=None,paths=()):
        return owner_authorization(self.repository,self.pull,comments if comments is not None else [self.comment],paths)

    def test_real_owner_fixture_is_authority_not_independent_review(self):
        r=self.auth();self.assertEqual(r["status"],"OWNER_EXACT_HEAD_AUTHORIZED")
        self.assertFalse(r["independent_review"])

    def test_new_head_never_inherits_old_authorization(self):
        self.pull["head"]["sha"]="b"*40
        self.assertEqual(self.auth()["reason"],"NO_OWNER_EXACT_HEAD_AUTHORIZATION")

    def test_same_name_bot_is_not_owner_user(self):
        self.comment["user"]["type"]="Bot"
        self.assertEqual(self.auth()["status"],"BLOCKED")

    def test_nonowner_comment_and_json_claim_do_not_authorize(self):
        self.comment["user"]["login"]="someone"
        self.assertEqual(self.auth()["status"],"BLOCKED")
        self.comment["user"]["login"]="owner";self.comment["body"]='{"approved":true}'
        self.assertEqual(self.auth()["status"],"BLOCKED")

    def test_latest_revocation_blocks(self):
        revoked=copy.deepcopy(self.comment);revoked.update(id=2,body="/deepwrite revoke "+self.sha)
        self.assertEqual(self.auth([self.comment,revoked])["reason"],"OWNER_REVOKED")

    def test_edited_old_comment_uses_actual_updated_time(self):
        old=copy.deepcopy(self.comment);old.update(id=0,body="/deepwrite revoke "+self.sha,
            updated_at="2026-11-12T00:00:01Z")
        self.assertEqual(self.auth([self.comment,old])["reason"],"OWNER_REVOKED")

    def test_governance_change_requires_explicit_bounded_authority(self):
        paths=["deepwrite/release/github_authorization.py"]
        self.assertEqual(self.auth(paths=paths)["reason"],"EXPLICIT_GOVERNANCE_AUTHORIZATION_REQUIRED")
        self.comment["body"]+=" governance"
        self.assertEqual(self.auth(paths=paths)["status"],"OWNER_EXACT_HEAD_AUTHORIZED")

    def test_actual_ci_must_match_head_app_and_latest_attempt(self):
        self.assertEqual(runtime_ci([self.check],self.sha)["status"],"ACTUAL_RUNTIME_CI_SUCCESS")
        self.assertEqual(runtime_ci([self.check],"b"*40)["status"],"BLOCKED")
        fake=copy.deepcopy(self.check);fake["app"]["id"]=99
        self.assertEqual(runtime_ci([fake],self.sha)["status"],"BLOCKED")
        failed=copy.deepcopy(self.check);failed.update(id=2,conclusion="failure")
        self.assertEqual(runtime_ci([self.check,failed],self.sha)["status"],"BLOCKED")

    def test_no_deepwrite_change_does_not_claim_release_authority(self):
        r=evaluate(self.repository,self.pull,[],[{"filename":"other.txt"}],[self.check])
        self.assertEqual(r["status"],"NOT_A_DEEPWRITE_RELEASE")
        self.assertNotIn("authorization",r)

    def test_fork_and_quality_change_are_not_automatically_promoted(self):
        self.pull["head"]["repo"]["full_name"]="someone/fork"
        self.assertEqual(evaluate(self.repository,self.pull,[self.comment],[],[self.check])["status"],"BLOCKED")
        self.pull["head"]["repo"]["full_name"]="owner/repo"
        self.comment["body"]="/deepwrite authorize QUALITY_BEHAVIOR_CHANGE "+self.sha
        r=evaluate(self.repository,self.pull,[self.comment],[{"filename":"deepwrite/CURRENT.json"}],[self.check])
        self.assertEqual(r["reason"],"QUALITY_PROMOTION_REQUIRES_SEPARATE_HUMAN_EVIDENCE_REVIEW")

    def test_automatic_formal_merge_preserves_implementation_ancestry(self):
        class API:
            def request(self,path,method,data):
                self.query=data["query"];return {"data":{}}
        api=API();enable_auto_merge(api,{"node_id":"fixture"})
        self.assertIn("mergeMethod:MERGE",api.query)
        self.assertNotIn("SQUASH",api.query);self.assertNotIn("REBASE",api.query)

    def configuration(self):
        repository={**self.repository,"allow_auto_merge":True,"allow_merge_commit":True,"default_branch":"main"}
        ruleset={"enforcement":"active","target":"branch","bypass_actors":[],
            "conditions":{"ref_name":{"include":["~DEFAULT_BRANCH"],"exclude":[]}},
            "rules":[{"type":"deletion"},{"type":"non_fast_forward"},
                {"type":"pull_request","parameters":{"required_approving_review_count":0}},
                {"type":"required_status_checks","parameters":{"strict_required_status_checks_policy":True,
                    "required_status_checks":[{"context":name,"integration_id":15368} for name in
                        ("activation-and-runtime-regressions","owner-release-authorization")]}}]}
        return repository,ruleset

    def test_real_configuration_requires_both_app_bound_contexts_and_no_bypass(self):
        repo,rule=self.configuration()
        self.assertEqual(protected_configuration(repo,[rule])["status"],"ACTUAL_REPOSITORY_PROTECTION_READY")
        rule["rules"][-1]["parameters"]["required_status_checks"].pop()
        self.assertEqual(protected_configuration(repo,[rule])["status"],"BLOCKED")
        rule["bypass_actors"]=[{"actor_id":1,"bypass_mode":"always"}]
        self.assertIn("MAIN_BYPASS_ACTORS_NOT_ALLOWED",protected_configuration(repo,[rule])["reasons"])

    def test_settings_do_not_pass_as_desired_config_or_single_owner_self_review(self):
        repo,rule=self.configuration();repo["allow_auto_merge"]=False
        rule["rules"][-2]["parameters"]["required_approving_review_count"]=1
        rule["rules"][-1]["parameters"]["strict_required_status_checks_policy"]=False
        result=protected_configuration(repo,[rule])
        self.assertIn("REPOSITORY_AUTO_MERGE_DISABLED",result["reasons"])
        self.assertIn("SINGLE_OWNER_REVIEW_RULE_STILL_BLOCKS",result["reasons"])
        self.assertIn("STRICT_BASE_CI_REQUIRED",result["reasons"])

    def test_disabled_or_non_main_ruleset_cannot_protect_main(self):
        repo,rule=self.configuration();rule["enforcement"]="disabled"
        self.assertIn("NO_ACTIVE_MAIN_RULESET",protected_configuration(repo,[rule])["reasons"])
        rule["enforcement"]="active";rule["conditions"]["ref_name"]["include"]=["refs/heads/experiment/*"]
        self.assertIn("NO_ACTIVE_MAIN_RULESET",protected_configuration(repo,[rule])["reasons"])

    def test_candidate_control_plane_cannot_publish_its_own_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ("github_authorization.py","release_verify.py"): (root/name).write_bytes(b"trusted base\n")
            class API:
                def get(self,path):
                    raw=b"trusted base\n"
                    return {"type":"file","sha":hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()}
            trusted_controller_source(API(),"a"*40,root)
            (root/"github_authorization.py").write_bytes(b"head judge always passes\n")
            with self.assertRaisesRegex(ValueError,"NOT_IDENTICAL_TO_PROTECTED_BASE"):
                trusted_controller_source(API(),"a"*40,root)


class ActualGitTransitionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="deepwrite-release-fixture-")
        self.top=Path(self.tmp.name);self.head=self.top/"repo";self.head.mkdir()
        self.gitcmd("init","-q");self.gitcmd("config","user.name","Engineering fixture")
        self.gitcmd("config","user.email","fixture@example.invalid")
        self.spec={"path":"deepwrite/versions/v0.1.md","sha256":h(b"Original intention\n")}
        self.write(self.spec["path"],b"Original intention\n")
        self.write("wish-delivery/versions/v7.6.md",b"Parent contract\n")
        parent={"active_version":"v7.6","active_spec":"wish-delivery/versions/v7.6.md"}
        self.write("wish-delivery/CURRENT.json",j(parent))
        self.before={"schema":"deepwrite/current/v1","active_workbench_version":"v0.1",
            "active_workbench_spec":self.spec["path"]}
        self.write("deepwrite/CURRENT.json",j(self.before));self.commit("Frozen baseline")
        self.base_sha=self.gitcmd("rev-parse","HEAD").decode().strip()
        self.base=self.top/"base";self.gitcmd("worktree","add","-q","--detach",str(self.base),self.base_sha)
        runtime="deepwrite/release/runtime.py";self.write(runtime,b"# Public engineering fixture only\n")
        self.receipt="deepwrite/releases/fixture-evidence.json"
        self.write(self.receipt,j({"status":"ENGINEERING_FIXTURE_ONLY"}));self.commit("Implementation bytes")
        self.impl=self.gitcmd("rev-parse","HEAD").decode().strip()
        self.record={"schema":"deepwrite/release-record/v1","status":"ACTIVE_RELEASE","version":"e24.1",
            "workbench_version":"v0.1","implementation_commit":self.impl,"spec":self.spec,
            "runtime_files":[{"path":runtime,"sha256":h((self.head/runtime).read_bytes())}],
            "parent":{"version":"v7.6","current_sha256":h((self.head/"wish-delivery/CURRENT.json").read_bytes()),
                "spec":{"path":parent["active_spec"],"sha256":h((self.head/parent["active_spec"]).read_bytes())}},
            "module_identities":[]}
        record_path="deepwrite/releases/e24.1.json";self.write(record_path,j(self.record))
        self.after=copy.deepcopy(self.before);self.after["active_engine"]={"version":"e24.1",
            "implementation_commit":self.impl,"path":runtime,"sha256":h((self.head/runtime).read_bytes()),
            "release_channel":"STABLE","release_record":record_path,"release_record_sha256":h(j(self.record))}
        self.write("deepwrite/CURRENT.json",j(self.after))
        self.request={"schema":"deepwrite/promotion-request/v1","base_version":"v0.1","new_version":"v0.1",
            "engine_version":"e24.1","base_current_sha256":h(j(self.before)),"parent_wish_version":"v7.6",
            "release_channel":"STABLE","change_scope":"ENGINEERING_PATCH","candidate_commit":self.impl,
            "rollback_commit":self.base_sha,"old_artifact_preserved":True,"spec":self.spec,
            "runner":{"path":runtime,"sha256":h((self.head/runtime).read_bytes())},
            "gates":{x:"PASS" for x in ("engineering","rollback_test","non_regression")},
            "evidence":{**{x:"fixture" for x in ("engineering","rollback_test","non_regression")},
                "no_quality_behavior_change_rationale":"Only execution identity changes; no writer policy."},
            "evidence_artifacts":{x:{"path":self.receipt,"sha256":h((self.head/self.receipt).read_bytes())}
                for x in ("engineering","rollback_test","non_regression")},
            "human_authorization_evidence":{"verification":"GITHUB_OWNER_EXACT_HEAD_COMMAND_REQUIRED"}}
        self.manifest="deepwrite/releases/e24.1-promotion.json";self.save_request();self.commit("Activation request")

    def tearDown(self): self.tmp.cleanup()
    def gitcmd(self,*args):
        return subprocess.check_output(["git","-C",str(self.head),*args],stderr=subprocess.DEVNULL)
    def write(self,path,raw):
        target=self.head/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    def commit(self,message): self.gitcmd("add",".");self.gitcmd("commit","-qm",message)
    def save_request(self): self.write(self.manifest,j(self.request))
    def result(self):
        paths=self.gitcmd("diff","--name-only",self.base_sha,"HEAD").decode().splitlines()
        return verify_transition(self.base,self.head,paths)

    def test_engineering_engine_advances_without_claiming_workbench_quality(self):
        r=self.result();self.assertEqual(r["status"],"ACTIVATION_BYTES_READY_NEEDS_LIVE_GITHUB_AUTHORITY",r)
        self.assertFalse(r["author_identity_verified_by_script"])

    def test_actual_evidence_hash_required_not_just_pass_fields(self):
        self.request.pop("evidence_artifacts");self.save_request();self.commit("Missing proof")
        self.assertIn("MISSING_ACTUAL_EVIDENCE_ARTIFACT:engineering",self.result()["reasons"])

    def test_declared_runtime_sha_cannot_hide_implementation_git_mismatch(self):
        self.write("deepwrite/release/runtime.py",b"# silently altered after pin\n");self.commit("Bad bytes")
        self.assertEqual(self.result()["status"],"BLOCKED")

    def test_engineering_cannot_activate_cognitive_module(self):
        self.record["module_identities"]=[{"id":"unvalidated-ideas"}]
        self.write("deepwrite/releases/e24.1.json",j(self.record))
        self.after["active_engine"]["release_record_sha256"]=h(j(self.record))
        self.write("deepwrite/CURRENT.json",j(self.after));self.commit("Unapproved module")
        self.assertIn("ENGINEERING_CANNOT_ACTIVATE_CANDIDATE_MODULES",self.result()["reasons"])

    def test_active_spec_changed_in_place_is_a_release_even_without_current_edit(self):
        self.gitcmd("reset","--hard",self.base_sha)
        self.write(self.spec["path"],b"New cognitive policy\n");self.commit("Unlabelled cognitive release")
        self.assertIn("EXACTLY_ONE_PROMOTION_REQUEST_REQUIRED",str(self.result()["reasons"]))

    def test_squash_loses_implementation_ancestry_and_is_blocked(self):
        # Replace history with a new tree whose implementation_commit exists
        # but is not an ancestor: the real failure caused by squash activation.
        tree=self.gitcmd("rev-parse","HEAD^{tree}").decode().strip()
        new=self.gitcmd("commit-tree",tree,"-p",self.base_sha,"-m","Squashed activation").decode().strip()
        self.gitcmd("reset","--hard",new)
        self.assertEqual(self.result()["status"],"BLOCKED")


if __name__=="__main__": unittest.main()
