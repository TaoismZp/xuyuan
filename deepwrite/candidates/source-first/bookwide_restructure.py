#!/usr/bin/env python3
"""One bounded post-book architecture reconsideration in an immutable derived project.

A proposal can KEEP or produce a *new* book configuration and full writer rerun.
This does not mutate the original, certify a model's argument, or approve quality.
Only full-draft author scope permits unattended topology reconstruction.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
DEEPWRITE=HERE.parent.parent


class Blocked(ValueError):
    pass


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(x):
    return (json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    x=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(x)
    return x


def validate(proposal, config, original_book):
    """Fail closed for structural change, not for an honest KEEP decision."""
    if not isinstance(proposal,dict) or proposal.get("schema")!="deepwrite/bookwide-topology-audit/v1":
        raise Blocked("BOOKWIDE_TOPOLOGY_REVIEW_SCHEMA_REQUIRED")
    if config.get("execution_contract",{}).get("mode")!="AUTONOMOUS_FULL_DRAFT":
        raise Blocked("BOOKWIDE_TOPOLOGY_REPLAN_REQUIRES_FULL_DRAFT_AUTHORIZATION")
    decision=proposal.get("decision")
    if decision not in ("KEEP","REPLAN"):
        raise Blocked("BOOKWIDE_TOPOLOGY_DECISION_REQUIRED")
    if not isinstance(proposal.get("reason"),str) or len(proposal["reason"].strip())<20:
        raise Blocked("BOOKWIDE_REASON_REQUIRED")
    if proposal.get("author_approved") or proposal.get("human_acceptance"):
        raise Blocked("BOOKWIDE_CANNOT_SELF_CERTIFY_AUTHOR_ACCEPTANCE")
    if decision=="KEEP":
        return {"decision":"KEEP","quality":"MODEL_REASONING_UNVERIFIED","author_acceptance":"NOT_RUN"}
    quote=proposal.get("evidence_quote")
    if not isinstance(quote,str) or len(quote)<15 or quote not in original_book:
        raise Blocked("BOOKWIDE_REPLAN_REQUIRES_LOCATED_OLD_TEXT_EVIDENCE")
    changed=proposal.get("chapters")
    if not isinstance(changed,list) or not changed or len(changed)>40:
        raise Blocked("BOOKWIDE_REPLAN_CHAPTER_STRUCTURE_REQUIRED")
    old=config["chapters"]
    old_ids=[x["artifact_id"] for x in old]
    new_ids=[x.get("artifact_id") for x in changed if isinstance(x,dict)]
    if (len(new_ids)!=len(changed) or any(not isinstance(x,str) or not
         re.fullmatch(r"[A-Za-z0-9_-]+",x) for x in new_ids) or len(set(new_ids))!=len(new_ids)):
        raise Blocked("BOOKWIDE_REPLAN_UNSAFE_OR_DUPLICATE_IDS")
    if [(x["artifact_id"],x["title"]) for x in changed]==[(x["artifact_id"],x["title"]) for x in old]:
        raise Blocked("BOOKWIDE_REPLAN_NO_ACTUAL_CHANGE_USE_KEEP")
    lineage=proposal.get("old_to_new")
    if (not isinstance(lineage,list) or
            {r.get("old_id") for r in lineage if isinstance(r,dict)}!=set(old_ids) or
            len(lineage)!=len(old_ids)):
        raise Blocked("BOOKWIDE_ALL_ORIGINAL_CHAPTERS_MUST_BE_ACCOUNTED_FOR")
    for rel in lineage:
        target=rel.get("new_ids")
        if not isinstance(target,list) or not target or not set(target)<=set(new_ids):
            raise Blocked("BOOKWIDE_REPLAN_UNACCOUNTED_ORIGINAL_CONTRIBUTION")
        if not isinstance(rel.get("treatment"),str) or rel["treatment"] not in ("MERGED","REWRITTEN","KEPT","DELETED_WITH_EVIDENCE"):
            raise Blocked("BOOKWIDE_REPLAN_CONTRIBUTION_TREATMENT_REQUIRED")
        if rel["treatment"]=="DELETED_WITH_EVIDENCE" and not rel.get("evidence"):
            raise Blocked("BOOKWIDE_DELETION_JUSTIFICATION_REQUIRED")
    contract=proposal.get("reader_prior_knowledge_contract")
    reviewer=module("deepwrite_topology_reader",DEEPWRITE/"candidates/e23-frame-wiring/reader_source_gate.py")
    reviewer.validate_contract(contract,changed)
    book_design=proposal.get("book_design")
    if not isinstance(book_design,dict):
        raise Blocked("BOOKWIDE_BOOK_DESIGN_REQUIRED")
    reasons=book_design.get("why_these_chapters_not_source_outline")
    contributions=book_design.get("chapter_contributions")
    if (not isinstance(reasons,str) or len(reasons)<20 or not isinstance(contributions,list) or
            {r.get("chapter_id") for r in contributions if isinstance(r,dict)}!=set(new_ids) or
            len(contributions)!=len(new_ids)):
        raise Blocked("BOOKWIDE_NEW_CHAPTERS_NOT_SOURCE_DEPENDENCY_GROUNDED")
    existing_concepts={c["id"] for c in config["source_first_architecture"]["source_concepts"]}
    for r in contributions:
        deps=r.get("source_concept_ids")
        if (not isinstance(deps,list) or not deps or not set(deps)<=existing_concepts or
                not isinstance(r.get("distinct_reader_change"),str) or len(r["distinct_reader_change"])<12):
            raise Blocked("BOOKWIDE_NEW_CHAPTER_SOURCE_OR_READER_CONTRIBUTION_REQUIRED")
    return {"decision":"REPLAN","new_chapters":len(changed),
            "old_chapters":len(old),"quality":"MODEL_REPLAN_NOT_AUTHOR_ACCEPTANCE"}


def derive_config(proposal, old):
    """New project and run ID: original E18 states are never rewritten."""
    if proposal.get("decision")!="REPLAN":
        raise Blocked("BOOKWIDE_NO_REPLAN_NEEDED")
    new=copy.deepcopy(old)
    new["chapters"]=proposal["chapters"]
    new["reader_prior_knowledge_contract"]=proposal["reader_prior_knowledge_contract"]
    new["source_first_architecture"]["book_design"]={
        "status":"PROVISIONAL",
        "why_these_chapters_not_source_outline":proposal["book_design"]["why_these_chapters_not_source_outline"],
        "chapter_contributions":proposal["book_design"]["chapter_contributions"]}
    new["run_id"]+="-topology-r2"
    new["source_study_origin"]="FROZEN_ORIGINAL_STUDY_NO_SECOND_SOURCE_LEARNING_CLAIM"
    return new


def make_private_derived_project(old_root, new_root, old_config, new_config):
    old_root,new_root=Path(old_root).resolve(),Path(new_root).resolve()
    if old_root==new_root or new_root.is_relative_to(old_root) or old_root.is_relative_to(new_root):
        raise Blocked("BOOKWIDE_DERIVED_PROJECT_MUST_NOT_OVERWRITE_ORIGINAL")
    if new_root.exists():
        raise Blocked("BOOKWIDE_DERIVED_PROJECT_ALREADY_EXISTS")
    for x in (old_root,new_root):
        if x.is_relative_to(DEEPWRITE.parent.resolve()):
            raise Blocked("BOOKWIDE_NO_PRIVATE_TEXT_IN_PUBLIC_CODE")
    if not old_root.joinpath("book.md").is_file():
        raise Blocked("BOOKWIDE_ORIGINAL_FULL_BOOK_REQUIRED")
    new_root.mkdir(parents=True)
    (new_root/"sources").mkdir()
    for row in old_config["sources"]:
        rel=row["path"]
        if not isinstance(rel,str) or not rel.startswith("sources/") or ".." in Path(rel).parts:
            raise Blocked("BOOKWIDE_SOURCE_PATH_INVALID")
        source=old_root/rel
        raw=source.read_bytes()
        if digest(raw)!=row["sha256"]:
            raise Blocked("BOOKWIDE_ORIGINAL_FROZEN_SOURCE_BYTES_CHANGED")
        dest=new_root/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(raw)
    # This receipt is for the operator, not an E18 tracked file.
    return {"status":"DERIVED_PROJECT_SOURCE_BYTES_FROZEN",
            "project":str(new_root),"unchanged_source_count":len(old_config["sources"]),
            "new_config_sha256":digest(canonical(new_config)),
            "original_book_sha256":digest((old_root/"book.md").read_bytes()),
            "author_acceptance":"NOT_RUN"}
