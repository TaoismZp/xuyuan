#!/usr/bin/env python3
"""Preflight of a proposed DeepWrite CURRENT promotion; no auto-human-signoff.

All content is local; no write to CURRENT, public GitHub or parent protocol.
The script checks identity/structure only. It never certifies editorial quality,
human approval, or CI authenticity merely from fields in a JSON file.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

HEX40 = re.compile(r"^[a-f0-9]{40}$")
HEX64 = re.compile(r"^[a-f0-9]{64}$")


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def safe_path(root, s):
    if not isinstance(s, str) or not s or s.startswith(("/", "~")):
        raise ValueError("INVALID_FILE_PATH")
    target = (root / s).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("MISSING_OR_OUTSIDE_FILE")
    return target


def verify(root, manifest):
    reasons=[]
    current_path=root / "deepwrite/CURRENT.json"
    try:
        current = json.loads(current_path.read_text("utf-8"))
        parent = json.loads((root / "wish-delivery/CURRENT.json").read_text("utf-8"))
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
    if not manifest.get("new_version") or manifest.get("new_version") == manifest.get("base_version"):
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
        if not isinstance(auth,dict) or auth.get("verification") != "GITHUB_PROTECTED_PR_APPROVAL_REQUIRED":
            reasons.append("HUMAN_AUTHORIZATION_MUST_BE_GITHUB_REVIEWED")
    return {"status":"BLOCKED" if reasons else "STRUCTURAL_READY_NEEDS_GITHUB_AUTHENTICATED_REVIEW",
            "reasons":reasons,
            "semantic_quality_verified_by_script":False,
            "author_identity_verified_by_script":False,
            "can_edit_current_without_PR":False}


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
