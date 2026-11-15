"""Synthetic API fixtures and real temporary Git objects; not live approval."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from github_authorization import owner_authorization, runtime_ci, evaluate, enable_auto_merge, protected_configuration, trusted_controller_source
from release_verify import verify_transition, orchestration_patch_only


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


class ActiveWritingPatchTests(unittest.TestCase):
    """Real Git transition from an already released WRITING inventory.

    These bytes are public fixtures. They prove conservative release scope,
    not writing quality or the authenticity of a GitHub approval.
    """
    ENTRY = (b"REQUEST_SCHEMA = 'frozen-reader-contract'\n"
             b"def prepare():\n    ident = {'formal_engine': {'version': 'v0.3.0'}}\n"
             b"    return {'schema': 'deepwrite/one-call-start/v1', 'policy': 'source-first-policy'}\n"
             b"def run_bounded_bookwide_topology_check():\n    return 'KEEP or REPLAN'\n"
             b"def run():\n    return 'writer-result'\n"
             b"def resume():\n    return 'writer-result'\n"
             b"def status():\n    return 'PAUSED'\n"
             b"def main():\n    return 0\n")

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="deepwrite-writing-patch-")
        self.top=Path(self.tmp.name);self.head=self.top/"repo";self.head.mkdir()
        self.gitcmd("init","-q");self.gitcmd("config","user.name","Engineering fixture")
        self.gitcmd("config","user.email","fixture@example.invalid")
        self.spec={"path":"deepwrite/versions/v0.3.md","sha256":h(b"Frozen writing contract\n")}
        self.write(self.spec["path"],b"Frozen writing contract\n")
        self.write("wish-delivery/versions/v7.6.md",b"Parent contract\n")
        parent={"active_version":"v7.6","active_spec":"wish-delivery/versions/v7.6.md"}
        self.write("wish-delivery/CURRENT.json",j(parent))
        self.entry="deepwrite/deepwrite.py"
        self.cognitive="deepwrite/candidates/source-first/architecture_discovery.py"
        self.doc="deepwrite/DEFAULT_INVOCATION.md"
        self.write(self.entry,self.ENTRY)
        self.write(self.cognitive,b"PROMPT = 'Native source study before transfer'\n")
        self.write(self.doc,b"Read CURRENT and execute the released entry.\n")
        self.commit("Existing writing implementation")
        old_impl=self.gitcmd("rev-parse","HEAD").decode().strip()
        parent_identity={"version":"v7.6","current_sha256":h((self.head/"wish-delivery/CURRENT.json").read_bytes()),
                         "spec":{"path":parent["active_spec"],"sha256":h((self.head/parent["active_spec"]).read_bytes())}}
        self.record={"schema":"deepwrite/release-record/v1","status":"ACTIVE_RELEASE","version":"v0.3.0",
            "workbench_version":"v0.3","implementation_commit":old_impl,"spec":self.spec,
            "runtime_files":[{"path":p,"sha256":h((self.head/p).read_bytes())} for p in (self.entry,self.cognitive,self.doc)],
            "parent":parent_identity,"module_identities":[{"id":"source_first","commit":old_impl}],
            "execution_profile":{"kind":"WRITING","mandatory_gates":["SOURCE_FIRST_ARCHITECTURE","BOOKWIDE_RECHECK"]}}
        self.write("deepwrite/releases/v0.3.0.json",j(self.record))
        self.before={"schema":"deepwrite/current/v1","active_workbench_version":"v0.3",
            "active_workbench_spec":self.spec["path"],"active_engine":{
                "version":"v0.3.0","implementation_commit":old_impl,"path":self.entry,
                "sha256":h(self.ENTRY),"release_channel":"STABLE",
                "release_record":"deepwrite/releases/v0.3.0.json","release_record_sha256":h(j(self.record))}}
        self.write("deepwrite/CURRENT.json",j(self.before));self.commit("Existing stable writing release")
        self.base_sha=self.gitcmd("rev-parse","HEAD").decode().strip()
        self.base=self.top/"base";self.gitcmd("worktree","add","-q","--detach",str(self.base),self.base_sha)
        self.write(self.entry,self.ENTRY+b"\ndef finalize_execution():\n    return 'engineering-receipt'\n")
        self.write(self.doc,b"Use run, status and resume; init is a historical runtime command.\n")
        self.receipt="deepwrite/release/evidence/patch-fixture.json"
        self.write(self.receipt,j({"status":"ENGINEERING_FIXTURE_ONLY"}))
        self.commit("Resume orchestration and invocation corrections")
        self.impl=self.gitcmd("rev-parse","HEAD").decode().strip()
        self.record=copy.deepcopy(self.record)
        self.record.update(version="v0.3.1",implementation_commit=self.impl)
        self.record["runtime_files"]=[{"path":p,"sha256":h((self.head/p).read_bytes())}
                                      for p in (self.entry,self.cognitive,self.doc)]
        self.record_path="deepwrite/releases/v0.3.1.json"
        self.after=copy.deepcopy(self.before)
        self.after["active_engine"].update(version="v0.3.1",implementation_commit=self.impl,
            sha256=h((self.head/self.entry).read_bytes()),release_record=self.record_path)
        self.request={"schema":"deepwrite/promotion-request/v1","base_version":"v0.3","new_version":"v0.3",
            "engine_version":"v0.3.1","base_current_sha256":h(j(self.before)),"parent_wish_version":"v7.6",
            "release_channel":"STABLE","change_scope":"ENGINEERING_PATCH","candidate_commit":self.impl,
            "rollback_commit":self.base_sha,"old_artifact_preserved":True,"spec":self.spec,
            "runner":{"path":self.entry,"sha256":h((self.head/self.entry).read_bytes())},
            "gates":{key:"PASS" for key in ("engineering","rollback_test","non_regression")},
            "evidence":{**{key:"public Git fixture" for key in ("engineering","rollback_test","non_regression")},
                "no_quality_behavior_change_rationale":"Restores an existing final review on resume; frozen research policy and gates."},
            "evidence_artifacts":{key:{"path":self.receipt,"sha256":h((self.head/self.receipt).read_bytes())}
                for key in ("engineering","rollback_test","non_regression")},
            "human_authorization_evidence":{"verification":"GITHUB_OWNER_EXACT_HEAD_COMMAND_REQUIRED"}}
        self.manifest="deepwrite/releases/v0.3.1-promotion.json"
        self.save_activation();self.commit("Engineering patch activation request")

    def tearDown(self): self.tmp.cleanup()
    def gitcmd(self,*args):
        return subprocess.check_output(["git","-C",str(self.head),*args],stderr=subprocess.DEVNULL)
    def write(self,path,raw):
        target=self.head/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    def commit(self,message): self.gitcmd("add",".");self.gitcmd("commit","-qm",message)
    def save_activation(self):
        self.write(self.record_path,j(self.record))
        self.after["active_engine"]["release_record_sha256"]=h(j(self.record))
        self.write("deepwrite/CURRENT.json",j(self.after));self.write(self.manifest,j(self.request))
    def rebind_runtime(self):
        self.commit("Changed implementation bytes")
        self.impl=self.gitcmd("rev-parse","HEAD").decode().strip()
        self.record["implementation_commit"]=self.impl
        for item in self.record["runtime_files"]:item["sha256"]=h((self.head/item["path"]).read_bytes())
        self.after["active_engine"].update(implementation_commit=self.impl,sha256=h((self.head/self.entry).read_bytes()))
        self.request.update(candidate_commit=self.impl,runner={"path":self.entry,"sha256":h((self.head/self.entry).read_bytes())})
        self.save_activation();self.commit("Bind changed implementation")
    def result(self):
        paths=self.gitcmd("diff","--name-only",self.base_sha,"HEAD").decode().splitlines()
        return verify_transition(self.base,self.head,paths)

    def test_existing_writing_dependencies_and_module_identities_are_preserved(self):
        result=self.result()
        self.assertEqual(result["status"],"ACTIVATION_BYTES_READY_NEEDS_LIVE_GITHUB_AUTHORITY",result)
        self.assertFalse(result["semantic_quality_verified_by_script"])
        self.assertFalse(result["author_identity_verified_by_script"])

    def test_changed_cognitive_dependency_is_not_an_engineering_patch(self):
        self.write(self.cognitive,b"PROMPT = 'Skip native learning and write a fixed outline'\n")
        self.rebind_runtime()
        self.assertIn("ENGINEERING_RUNTIME_OUTSIDE_REVIEWED_BOUNDARY:"+self.cognitive,self.result()["reasons"])

    def test_new_cognitive_dependency_is_not_an_engineering_patch(self):
        path="deepwrite/candidates/extra-insight/prompt.py";self.write(path,b"NEW_POLICY = True\n")
        self.record["runtime_files"].append({"path":path,"sha256":h((self.head/path).read_bytes())})
        self.rebind_runtime()
        self.assertIn("ENGINEERING_RUNTIME_OUTSIDE_REVIEWED_BOUNDARY:"+path,self.result()["reasons"])

    def test_existing_runtime_dependency_cannot_disappear_from_inventory(self):
        self.record["runtime_files"]=[item for item in self.record["runtime_files"] if item["path"]!=self.cognitive]
        self.save_activation();self.commit("Drop protected cognitive identity")
        self.assertIn("ENGINEERING_CANNOT_REMOVE_RUNTIME_DEPENDENCY:"+self.cognitive,self.result()["reasons"])

    def test_existing_module_identity_cannot_change(self):
        self.record["module_identities"][0]["commit"]="b"*40
        self.save_activation();self.commit("Replace cognitive module identity")
        self.assertIn("ENGINEERING_CANNOT_CHANGE_MODULE_IDENTITIES",self.result()["reasons"])

    def test_existing_module_identity_cannot_be_removed(self):
        self.record["module_identities"]=[]
        self.save_activation();self.commit("Remove cognitive module identity")
        self.assertIn("ENGINEERING_CANNOT_CHANGE_MODULE_IDENTITIES",self.result()["reasons"])

    def test_mandatory_gate_cannot_be_removed(self):
        self.record["execution_profile"]["mandatory_gates"].remove("BOOKWIDE_RECHECK")
        self.save_activation();self.commit("Remove existing final gate")
        self.assertIn("ENGINEERING_CANNOT_CHANGE_EXECUTION_PROFILE",self.result()["reasons"])

    def test_execution_kind_cannot_change(self):
        self.record["execution_profile"]["kind"]="ENGINEERING"
        self.save_activation();self.commit("Downgrade writing profile")
        self.assertIn("ENGINEERING_CANNOT_CHANGE_EXECUTION_PROFILE",self.result()["reasons"])

    def test_entry_source_policy_cannot_change_under_orchestration_exception(self):
        self.write(self.entry,(self.head/self.entry).read_bytes().replace(b"source-first-policy",b"skip-source-policy"))
        self.rebind_runtime()
        self.assertIn("ENGINEERING_ENTRY_POLICY_AST_CHANGED",self.result()["reasons"])

    def test_new_unreviewed_entry_helper_cannot_change_engineering_boundary(self):
        self.write(self.entry,(self.head/self.entry).read_bytes()+b"\ndef new_discovery_policy():\n    return 'skip sources'\n")
        self.rebind_runtime()
        self.assertIn("ENGINEERING_ENTRY_POLICY_AST_CHANGED",self.result()["reasons"])

    def test_prepare_may_add_exact_engine_lock_without_changing_source_policy(self):
        self.write(self.entry,(self.head/self.entry).read_bytes().replace(
            b"return {'schema':",b"return {'engine_lock': ident['formal_engine'], 'schema':"))
        self.rebind_runtime()
        self.assertEqual(self.result()["status"],"ACTIVATION_BYTES_READY_NEEDS_LIVE_GITHUB_AUTHORITY")

    def test_prepare_engine_lock_exception_cannot_replace_policy_or_lock_value(self):
        for field in (b"'engine_lock': {'version': 'unchecked'}, ",
                      b"'engine_lock': ident['formal_engine'], 'new_policy': 'skip research', "):
            with self.subTest(field=field):
                changed=self.ENTRY.replace(b"return {'schema':",b"return {"+field+b"'schema':")
                self.assertFalse(orchestration_patch_only(self.ENTRY,changed))

    def test_prepare_engine_lock_cannot_be_removed_after_it_was_released(self):
        locked=self.ENTRY.replace(b"return {'schema':",b"return {'engine_lock': ident['formal_engine'], 'schema':")
        self.assertFalse(orchestration_patch_only(locked,self.ENTRY))

    def test_allowed_orchestration_function_cannot_add_an_executable_header(self):
        for change in (b"def resume(value=skip_native_study()):",b"def resume(value: skip_native_study()):"):
            with self.subTest(change=change):
                altered=self.ENTRY.replace(b"def resume():",change)
                self.assertFalse(orchestration_patch_only(self.ENTRY,altered))


if __name__=="__main__": unittest.main()
