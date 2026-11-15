#!/usr/bin/env python3
"""Preflight of a proposed DeepWrite CURRENT promotion; no auto-human-signoff.

All content is local; no write to CURRENT, public GitHub or parent protocol.
The script checks identity/structure only. It never certifies editorial quality,
human approval, or CI authenticity merely from fields in a JSON file.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def safe_path(root, s):
    if not isinstance(s, str) or not s or s.startswith(("/", "~")):
        raise ValueError("INVALID_FILE_PATH")
    if any(part in ("", ".", "..") for part in s.split("/")):
        raise ValueError("NONCANONICAL_FILE_PATH")
    source=root / s
    if any(p.is_symlink() for p in [source,*source.parents] if p!=root.parent):
        raise ValueError("SYMLINK_RELEASE_PATH")
    target = (root / s).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("MISSING_OR_OUTSIDE_FILE")
    return target


def verify(root, manifest, base_root=None):
    reasons=[]
    root = Path(root).resolve()
    base_root = Path(base_root).resolve() if base_root else root
    current_path=base_root / "deepwrite/CURRENT.json"
    try:
        current = json.loads(current_path.read_text("utf-8"))
        parent = json.loads((base_root / "wish-delivery/CURRENT.json").read_text("utf-8"))
    except (OSError, ValueError) as exc:
        return {"status":"BLOCKED","reasons":["CANNOT_READ_ACTIVE_POINTERS: "+str(exc)]}
    if manifest.get("schema") != "deepwrite/promotion-request/v1": reasons.append("BAD_MANIFEST_SCHEMA")
    if manifest.get("base_version") != current.get("active_workbench_version"):
        reasons.append("STALE_ACTIVE_BASE_VERSION")
    if manifest.get("base_current_sha256") != digest(current_path):
        reasons.append("STALE_ACTIVE_CURRENT_BYTES")
    if manifest.get("parent_wish_version") != parent.get("active_version"):
        reasons.append("PARENT_VERSION_CHANGED")
    if manifest.get("release_channel") != "STABLE": reasons.append("INVALID_RELEASE_CHANNEL")
    scope = manifest.get("change_scope")
    if scope not in ("ENGINEERING_PATCH", "QUALITY_BEHAVIOR_CHANGE"):
        reasons.append("INVALID_CHANGE_SCOPE")
    engineering_version = manifest.get("engine_version")
    if (not manifest.get("new_version") or
        (manifest.get("new_version") == manifest.get("base_version") and
         not (scope == "ENGINEERING_PATCH" and isinstance(engineering_version,str) and engineering_version))):
        reasons.append("VERSION_NOT_ADVANCED")
    if not HEX40.fullmatch(str(manifest.get("candidate_commit", ""))):
        reasons.append("CANDIDATE_COMMIT_NOT_PINNED")
    if not HEX40.fullmatch(str(manifest.get("rollback_commit", ""))):
        reasons.append("ROLLBACK_COMMIT_NOT_PINNED")
    for name in ("spec", "runner"):
        obj=manifest.get(name)
        if not isinstance(obj, dict):
            reasons.append("MISSING_"+name.upper())
            continue
        try:
            f=safe_path(root,obj.get("path"))
            if digest(f) != obj.get("sha256") or not HEX64.fullmatch(str(obj.get("sha256", ""))):
                reasons.append(name.upper()+"_HASH_MISMATCH")
        except ValueError:
            reasons.append(name.upper()+"_MISSING_OR_UNSAFE")
    if manifest.get("old_artifact_preserved") is not True:
        reasons.append("OLD_ARTIFACT_NOT_PRESERVED")
    evidence=manifest.get("evidence",{})
    gates=manifest.get("gates",{})
    if not isinstance(evidence,dict) or not isinstance(gates,dict):
        reasons.append("INVALID_EVIDENCE_OR_GATES")
        gates,evidence={},{}
    required = ("engineering", "rollback_test", "non_regression")
    if scope == "QUALITY_BEHAVIOR_CHANGE":
        required += ("content_quality", "author_acceptance", "independent_validation")
    elif scope == "ENGINEERING_PATCH":
        # Patch releases must be scoped to implementation/identity fixes that
        # do not alter cognitive prompts, book selection, or reader outcomes.
        # A GitHub protected reviewer must examine this claim; code cannot.
        if not evidence.get("no_quality_behavior_change_rationale"):
            reasons.append("PATCH_SCOPE_NOT_JUSTIFIED")
        if any(gates.get(k) == "FAIL" for k in ("content_quality", "author_acceptance", "independent_validation")):
            reasons.append("PATCH_CANNOT_BYPASS_KNOWN_CONTENT_FAILURE")
    for key in required:
        if gates.get(key) != "PASS":
            reasons.append("PROMOTION_GATE_NOT_PASS_"+key.upper())
        if not evidence.get(key):
            reasons.append("MISSING_EVIDENCE_"+key.upper())
    if scope == "QUALITY_BEHAVIOR_CHANGE":
        if not isinstance(evidence.get("independent_topic_count"),int) or evidence.get("independent_topic_count",0)<3:
            reasons.append("NOT_ENOUGH_INDEPENDENT_TOPICS")
        if not isinstance(evidence.get("reader_count"),int) or evidence.get("reader_count",0)<2:
            reasons.append("NOT_ENOUGH_INDEPENDENT_READERS")
    # A boolean 'author_approved' in model-generated JSON is NEVER enough.
    if manifest.get("human_authorization_evidence") is None:
        reasons.append("NO_HUMAN_RELEASE_AUTHORITY")
    else:
        auth=manifest["human_authorization_evidence"]
        if not isinstance(auth,dict) or auth.get("verification") not in (
                "GITHUB_PROTECTED_PR_APPROVAL_REQUIRED", "GITHUB_OWNER_EXACT_HEAD_COMMAND_REQUIRED"):
            reasons.append("HUMAN_AUTHORIZATION_MUST_BE_GITHUB_REVIEWED")
    return {"status":"BLOCKED" if reasons else "STRUCTURAL_READY_NEEDS_GITHUB_AUTHENTICATED_REVIEW",
            "reasons":reasons,
            "semantic_quality_verified_by_script":False,
            "author_identity_verified_by_script":False,
            "can_edit_current_without_PR":False}


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)


def orchestration_patch_only(before_raw, after_raw):
    """Bound the existing entry's engineering exception; never execute its code.

    This is a scope check, not proof of program semantics. Exact-head owner
    review and regressions must still assess the changed scheduling functions.
    Native research, request/source policy, imports and protocol constants stay
    frozen. A future cognitive change needs the separate promotion channel.
    """
    allowed={"run", "resume", "status", "main", "archive_execution_evidence",
             "save_execution_evidence", "finalize_execution", "project_engine_lock"}

    def start_dict(tree):
        found=[]
        for function in tree.body:
            if not isinstance(function,ast.FunctionDef) or function.name!="prepare": continue
            for node in ast.walk(function):
                if isinstance(node,ast.Dict) and any(
                        isinstance(key,ast.Constant) and key.value=="schema" and
                        isinstance(value,ast.Constant) and value.value=="deepwrite/one-call-start/v1"
                        for key,value in zip(node.keys,node.values)):
                    found.append(node)
        return found

    def frozen(tree):
        functions=[node for node in tree.body if isinstance(node,ast.FunctionDef)]
        names=[node.name for node in functions]
        if len(names)!=len(set(names)):
            raise ValueError("DUPLICATE_ENTRY_FUNCTION")
        for node in functions:
            if node.name in allowed and (node.decorator_list or any(
                    isinstance(child,ast.Call) for value in (node.args,node.returns)
                    if value is not None for child in ast.walk(value))):
                raise ValueError("ENTRY_PATCH_EXECUTABLE_FUNCTION_HEADER")
        frozen_nodes=[node for node in tree.body
                      if not (isinstance(node,ast.FunctionDef) and node.name in allowed)]
        return ast.dump(ast.Module(body=frozen_nodes,type_ignores=[]),include_attributes=False),set(names)

    try:
        before_tree,after_tree=ast.parse(before_raw),ast.parse(after_raw)
        before_start,after_start=start_dict(before_tree),start_dict(after_tree)
        if len(before_start)==len(after_start)==1:
            old_node,new_node=before_start[0],after_start[0]
            old_keys=[key.value if isinstance(key,ast.Constant) else None for key in old_node.keys]
            new_keys=[key.value if isinstance(key,ast.Constant) else None for key in new_node.keys]
            # Permit only the first addition of the explicit engine lock to the
            # existing START_STATE. Once present, removal/change is frozen too.
            if "engine_lock" not in old_keys and new_keys.count("engine_lock")==1:
                position=new_keys.index("engine_lock")
                expected=ast.parse('ident["formal_engine"]',mode="eval").body
                if ast.dump(new_node.values[position])==ast.dump(expected):
                    del new_node.keys[position];del new_node.values[position]
        old,old_names=frozen(before_tree)
        new,new_names=frozen(after_tree)
    except (SyntaxError,ValueError,TypeError):
        return False
    return old==new and (old_names & allowed)<=new_names


def verify_transition(base_root, head_root, changed_paths, manifest_path=None):
    """Trusted base-code check of candidate data; never imports candidate Python.

    This verifies bytes/Git objects and conservative activation scope. Real CI
    and owner authority are checked separately against GitHub by the controller.
    Existing v1 preflight declarations alone never authorize a merge.
    """
    base_root, head_root = Path(base_root).resolve(), Path(head_root).resolve()
    paths = set(changed_paths)
    reasons = []
    try:
        before_path = safe_path(base_root, "deepwrite/CURRENT.json")
        after_path = safe_path(head_root, "deepwrite/CURRENT.json")
        before, after = json.loads(before_path.read_bytes()), json.loads(after_path.read_bytes())
        old_engine = before.get("active_engine") or {}
        old_record = (json.loads(safe_path(base_root, old_engine["release_record"]).read_bytes())
                      if old_engine else {})
        protected_runtime = {f["path"] for f in old_record.get("runtime_files", [])}
        parent=json.loads(safe_path(base_root,"wish-delivery/CURRENT.json").read_bytes())
        protected_runtime.update({before["active_workbench_spec"],"wish-delivery/CURRENT.json"})
        if parent.get("active_spec"): protected_runtime.add(parent["active_spec"])
        changed = before_path.read_bytes() != after_path.read_bytes() or bool(paths & protected_runtime)
        if not changed:
            return {"status":"NO_ACTIVATION_CHANGE", "reasons":[], "semantic_quality_verified_by_script":False}
        if manifest_path is None:
            choices=[]
            for name in sorted(paths):
                if name.startswith("deepwrite/releases/") and name.endswith(".json"):
                    try:
                        obj=json.loads(safe_path(head_root,name).read_bytes())
                        if obj.get("schema")=="deepwrite/promotion-request/v1": choices.append(name)
                    except (ValueError, OSError): pass
            if len(choices)!=1: raise ValueError("EXACTLY_ONE_PROMOTION_REQUEST_REQUIRED")
            manifest_path=choices[0]
        request=json.loads(safe_path(head_root,manifest_path).read_bytes())
        structural=verify(head_root,request,base_root=base_root)
        reasons.extend(structural["reasons"])
        required_evidence=("engineering","rollback_test","non_regression")
        if request.get("change_scope")=="QUALITY_BEHAVIOR_CHANGE":
            required_evidence+=("content_quality","author_acceptance","independent_validation")
        artifacts=request.get("evidence_artifacts",{})
        for key in required_evidence:
            obj=artifacts.get(key) if isinstance(artifacts,dict) else None
            if not isinstance(obj,dict) or not obj.get("path") or not obj.get("sha256"):
                reasons.append("MISSING_ACTUAL_EVIDENCE_ARTIFACT:"+key)
            elif digest(safe_path(head_root,obj["path"]))!=obj["sha256"]:
                reasons.append("EVIDENCE_ARTIFACT_HASH_MISMATCH:"+key)
        engine=after.get("active_engine")
        if not isinstance(engine,dict): raise ValueError("PROMOTION_REQUIRES_PINNED_ACTIVE_ENGINE")
        record_path=engine["release_record"]
        record_raw=safe_path(head_root,record_path).read_bytes()
        record=json.loads(record_raw)
        scope=request.get("change_scope")
        if record_path not in paths: reasons.append("RELEASE_RECORD_NOT_IN_THIS_PR")
        if (record.get("schema")!="deepwrite/release-record/v1" or record.get("status")!="ACTIVE_RELEASE" or
            record.get("version")!=engine.get("version") or record.get("workbench_version")!=after.get("active_workbench_version") or
            digest(safe_path(head_root,record_path))!=engine.get("release_record_sha256")):
            reasons.append("CURRENT_RELEASE_RECORD_IDENTITY_MISMATCH")
        if request.get("engine_version")!=engine.get("version"):
            reasons.append("REQUEST_ENGINE_VERSION_MISMATCH")
        if engine.get("version")==old_engine.get("version"):
            reasons.append("ENGINE_VERSION_NOT_ADVANCED")
        if request.get("spec")!=record.get("spec"):
            reasons.append("REQUEST_RECORD_SPEC_MISMATCH")
        if record.get("spec",{}).get("path")!=after.get("active_workbench_spec"):
            reasons.append("RECORD_CURRENT_SPEC_PATH_MISMATCH")
        parent_record=record.get("parent",{})
        parent_head=safe_path(head_root,"wish-delivery/CURRENT.json")
        actual_parent=json.loads(parent_head.read_bytes())
        if (parent_record.get("version")!=actual_parent.get("active_version") or
            parent_record.get("current_sha256")!=digest(parent_head) or
            parent_record.get("spec",{}).get("path")!=actual_parent.get("active_spec") or
            parent_record.get("spec",{}).get("sha256")!=digest(safe_path(head_root,actual_parent["active_spec"]))):
            reasons.append("PARENT_RELEASE_IDENTITY_MISMATCH")
        implementation=engine.get("implementation_commit","")
        if (not HEX40.fullmatch(implementation) or implementation!=record.get("implementation_commit") or
            implementation!=request.get("candidate_commit")):
            raise ValueError("IMPLEMENTATION_COMMIT_NOT_BOUND")
        git(head_root,"cat-file","-e",implementation+"^{commit}")
        git(head_root,"merge-base","--is-ancestor",implementation,"HEAD")
        for f in record.get("runtime_files",[]):
            actual=safe_path(head_root,f["path"])
            if actual.is_symlink() or digest(actual)!=f["sha256"]:
                reasons.append("RELEASE_RUNTIME_FILE_MISMATCH:"+f["path"])
            if hashlib.sha256(git(head_root,"show",implementation+":"+f["path"])).hexdigest()!=f["sha256"]:
                reasons.append("IMPLEMENTATION_GIT_BYTES_MISMATCH:"+f["path"])
        if not record.get("runtime_files") or engine.get("path") not in {f["path"] for f in record["runtime_files"]}:
            reasons.append("ACTIVE_ENGINE_NOT_IN_RUNTIME_INVENTORY")
        if (request.get("runner",{}).get("path")!=engine.get("path") or
            request.get("runner",{}).get("sha256")!=engine.get("sha256") or
            digest(safe_path(head_root,engine["path"]))!=engine.get("sha256")):
            reasons.append("REQUEST_RUNNER_IDENTITY_MISMATCH")
        if engine.get("release_channel")!="STABLE": reasons.append("ENGINE_NOT_STABLE")
        rollback=request.get("rollback_commit","")
        git(base_root,"merge-base","--is-ancestor",rollback,"HEAD")
        if hashlib.sha256(git(base_root,"show",rollback+":deepwrite/CURRENT.json")).hexdigest()!=request.get("base_current_sha256"):
            reasons.append("ROLLBACK_CURRENT_IDENTITY_MISMATCH")
        for name in paths:
            if name.startswith("deepwrite/releases/") and (base_root/name).exists() and (head_root/name).read_bytes()!=(base_root/name).read_bytes():
                reasons.append("IMMUTABLE_RELEASE_RECORD_CHANGED:"+name)
        if request.get("change_scope")=="ENGINEERING_PATCH":
            if safe_path(base_root,"wish-delivery/CURRENT.json").read_bytes()!=parent_head.read_bytes():
                reasons.append("ENGINEERING_CANNOT_CHANGE_PARENT_PROTOCOL")
            if (after.get("active_workbench_version")!=before.get("active_workbench_version") or
                after.get("active_workbench_spec")!=before.get("active_workbench_spec") or
                safe_path(head_root,after["active_workbench_spec"]).read_bytes()!=safe_path(base_root,before["active_workbench_spec"]).read_bytes()):
                reasons.append("ENGINEERING_CANNOT_CHANGE_COGNITIVE_SPEC")
            if record.get("module_identities",[])!=old_record.get("module_identities",[]):
                reasons.append("ENGINEERING_CANNOT_CHANGE_MODULE_IDENTITIES")
                if record.get("module_identities"):
                    reasons.append("ENGINEERING_CANNOT_ACTIVATE_CANDIDATE_MODULES")
            if record.get("execution_profile")!=old_record.get("execution_profile"):
                reasons.append("ENGINEERING_CANNOT_CHANGE_EXECUTION_PROFILE")
            # Engineering fast path is deliberately narrow. Prompt/discovery/
            # writer policy changes cannot be relabelled as a hash repair.
            # The old rule rejected every inherited WRITING dependency, even
            # byte-identical ones. Preserve its real base inventory and inspect
            # only changed dependencies; do not silently drop an old identity.
            old_runtime={item["path"]:item["sha256"] for item in old_record.get("runtime_files",[])}
            new_runtime={item["path"]:item["sha256"] for item in record.get("runtime_files",[])}
            for name in old_runtime.keys()-new_runtime.keys():
                reasons.append("ENGINEERING_CANNOT_REMOVE_RUNTIME_DEPENDENCY:"+name)
            allowed=("deepwrite/release/","deepwrite/qa/")
            engineering_tools={"deepwrite/tools/book_packager_v0.1.py",
                "deepwrite/candidates/e15-review-closure/review_closure_guard.py"}
            invocation_docs={"deepwrite/DEFAULT_INVOCATION.md","deepwrite/UNIFIED_RELEASE_CANDIDATE.json"}
            for f in record.get("runtime_files",[]):
                name=f["path"]
                if name in old_runtime:
                    old_file=safe_path(base_root,name)
                    if digest(old_file)!=old_runtime[name]:
                        reasons.append("BASE_RUNTIME_FILE_MISMATCH:"+name)
                    elif old_file.read_bytes()==safe_path(head_root,name).read_bytes():
                        continue
                if name.startswith(allowed) or name in engineering_tools:
                    continue
                if name in invocation_docs and name in old_runtime:
                    # These existing documents route users to the same pinned
                    # engine; their actual diff remains part of owner review.
                    continue
                if (name=="deepwrite/deepwrite.py" and name in old_runtime and
                    old_record.get("execution_profile",{}).get("kind")=="WRITING"):
                    if not orchestration_patch_only(safe_path(base_root,name).read_bytes(),
                                                    safe_path(head_root,name).read_bytes()):
                        reasons.append("ENGINEERING_ENTRY_POLICY_AST_CHANGED")
                    continue
                reasons.append("ENGINEERING_RUNTIME_OUTSIDE_REVIEWED_BOUNDARY:"+name)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        reasons.append("TRANSITION_CHECK_FAILED:"+str(error))
    return {"status":"BLOCKED" if reasons else "ACTIVATION_BYTES_READY_NEEDS_LIVE_GITHUB_AUTHORITY",
            "reasons":reasons,"semantic_quality_verified_by_script":False,
            "author_identity_verified_by_script":False,
            "change_scope":locals().get("scope")}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=verify(a.repo.resolve(),json.loads(a.manifest.read_text("utf-8")))
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output: a.output.write_text(text,encoding="utf-8")
    print(text,end="")
    return 2 if result["status"]=="BLOCKED" else 0

if __name__=="__main__": raise SystemExit(main())
