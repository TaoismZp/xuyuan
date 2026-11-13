#!/usr/bin/env python3
"""Bind existing G0/G1/G2/G6 reader/source review to actual text and STOP.

This is an execution check for a model's located review, not a semantic grader.
No keyword, chapter template, numerical quality score or human PASS is inferred.
E15 remains responsible for frozen findings, real revision and closeout.
"""
from __future__ import annotations
import hashlib
import json
import re

CONTRACT_SCHEMA = "deepwrite/reader-prior-contract/v1"
REVIEW_SCHEMA = "deepwrite/reader-source-review/v1"
SOURCE_DIMENSIONS = ("source_scene", "importance", "mechanism", "counterexample",
                     "conditions", "transfer_boundary")
AUDIENCES = ("NOVICE", "PRACTITIONER", "EXPERT")
SOURCE_CODES = {"TRANSFER_BEFORE_SOURCE_MASTERY", "NEGATIVE_KNOWLEDGE_COMPOUNDING",
                "SOURCE_DOMAIN_RULE_ERROR", "SOURCE_INGESTED_BUT_NOT_GOVERNING"}
READER_CODES = {"READER_PREREQUISITE_ASSUMED", "NOVICE_EXPERT_VALUE_COLLAPSE",
                "DEPENDENCY_BEFORE_EXPLANATION", "REPEATED_RETEACHING",
                "FORCED_READER_TEMPLATE_REPETITION"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def paragraphs(text):
    return [part for part in re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n").replace("\r", "\n")) if part.strip()]


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_contract(contract, chapters):
    """Freeze declared prior knowledge and planned dependencies, not their truth."""
    if not isinstance(contract, dict) or contract.get("schema") != CONTRACT_SCHEMA:
        raise ValueError("READER_CONTRACT_SCHEMA_REQUIRED")
    chapter_ids = [c["artifact_id"] if isinstance(c, dict) else c for c in chapters]
    if not chapter_ids or len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("READER_CONTRACT_CHAPTER_ORDER_REQUIRED")
    for key in ("known", "unknown"):
        values = contract.get(key)
        if not isinstance(values, list) or any(not nonempty(v) for v in values) or len(set(values)) != len(values):
            raise ValueError("READER_CONTRACT_" + key.upper() + "_REQUIRED")
    if not contract["unknown"] or set(contract["known"]) & set(contract["unknown"]):
        raise ValueError("READER_CONTRACT_UNKNOWN_OR_CONTRADICTORY_PRIORS")
    concepts = contract.get("concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError("READER_CONCEPT_DEPENDENCY_MAP_REQUIRED")
    table = {}
    order = {chapter: number for number, chapter in enumerate(chapter_ids)}
    for row in concepts:
        if not isinstance(row, dict) or not nonempty(row.get("id")) or row["id"] in table:
            raise ValueError("READER_CONCEPT_ID_INVALID_OR_DUPLICATE")
        if row.get("first_explained_in") not in order or row.get("first_used_in") not in order:
            raise ValueError("READER_CONCEPT_FIRST_LOCATION_REQUIRED")
        if order[row["first_used_in"]] < order[row["first_explained_in"]]:
            raise ValueError("READER_CONCEPT_USED_BEFORE_DECLARED_EXPLANATION")
        deps = row.get("prerequisites")
        if not isinstance(deps, list) or len(set(deps)) != len(deps):
            raise ValueError("READER_PREREQUISITES_REQUIRED")
        table[row["id"]] = row
    for ident, row in table.items():
        for dependency in row["prerequisites"]:
            if dependency not in table or dependency == ident:
                raise ValueError("READER_DEPENDENCY_UNKNOWN_OR_SELF_REFERENCE")
            if order[table[dependency]["first_explained_in"]] > order[row["first_explained_in"]]:
                raise ValueError("READER_DEPENDENCY_DECLARED_AFTER_DEPENDENT")
    visited, pending = set(), set()
    def visit(ident):
        if ident in pending:
            raise ValueError("READER_DEPENDENCY_CYCLE")
        if ident in visited:
            return
        pending.add(ident)
        for dependency in table[ident]["prerequisites"]:
            visit(dependency)
        pending.remove(ident); visited.add(ident)
    for ident in table:
        visit(ident)
    return {"status": "ENGINEERING_CONTRACT_FROZEN", "contract_sha256": digest(canonical(contract)),
            "declared_chapter_order": chapter_ids,
            "semantic_prior_or_dependency_correctness": "NOT_CERTIFIED"}


def _location(text, item, label, errors):
    """Verify an actual paragraph/quote; locating a claim does not prove it."""
    if not isinstance(item, dict):
        errors.append(label + "_LOCATION_REQUIRED"); return False
    parts, number, quote = paragraphs(text), item.get("paragraph"), item.get("quote")
    if type(number) is not int or number < 1 or number > len(parts):
        errors.append(label + "_PARAGRAPH_INVALID"); return False
    if not nonempty(quote) or quote not in parts[number - 1]:
        errors.append(label + "_QUOTE_NOT_IN_ACTUAL_PARAGRAPH"); return False
    if "paragraph_sha256" in item and item["paragraph_sha256"] != digest(parts[number - 1].encode("utf-8")):
        errors.append(label + "_PARAGRAPH_SHA_MISMATCH"); return False
    return True


def evaluate(contract, chapter_id, text, review, stage="SOURCE_LEARNING", source_texts=None):
    """Record a byte-bound model assessment or return a blocking disposition.

    source_texts maps frozen source IDs to their UTF-8 text. The runner owns
    those source identities and the model-call receipt; this function does not
    authenticate a model/provider or decide whether a source is reliable.
    """
    errors, blocking = [], []
    artifact_sha = digest(text.encode("utf-8"))
    contract_sha = digest(canonical(contract))
    base = {"schema": "deepwrite/reader-source-gate-result/v1", "stage": stage,
            "artifact_sha256": artifact_sha, "contract_sha256": contract_sha,
            "reader_source_transfer_gate": "ENGINEERING_ONLY",
            "semantic_quality": "MODEL_INTERNAL_REVIEW_NOT_MACHINE_CERTIFIED",
            "model_call_authenticated_by_helper": False,
            "evidence_origin": "CALLER_SUPPLIED_REVIEW_BOUND_TO_BYTES_NOT_PROVIDER_AUTHENTICATED_HERE",
            "author_acceptance": "NOT_RUN", "human_blind_evaluation": "NOT_RUN",
            "published": False}
    if stage not in ("SOURCE_LEARNING", "CHAPTER", "BOOKWIDE"):
        errors.append("UNKNOWN_READER_REVIEW_STAGE")
    if not isinstance(review, dict):
        return {**base, "status": "HOLD_REVIEW_EVIDENCE", "errors": ["ACTUAL_REVIEW_OBJECT_REQUIRED"], "blocking_findings": []}
    if review.get("schema") != REVIEW_SCHEMA:
        errors.append("READER_REVIEW_SCHEMA_REQUIRED")
    if review.get("artifact_sha256") != artifact_sha:
        errors.append("READER_REVIEW_ARTIFACT_SHA_MISMATCH")
    if review.get("contract_sha256") != contract_sha:
        errors.append("READER_REVIEW_CONTRACT_SHA_MISMATCH")
    if not nonempty(review.get("reviewer")):
        errors.append("ACTUAL_MODEL_REVIEW_IDENTITY_REQUIRED")
    if review.get("author_acceptance", "NOT_RUN") not in ("NOT_RUN", "PENDING"):
        errors.append("READER_REVIEW_CANNOT_AUTHENTICATE_AUTHOR")
    if review.get("human_blind_evaluation", "NOT_RUN") != "NOT_RUN":
        errors.append("MODEL_REVIEW_CANNOT_CLAIM_HUMAN_BLIND_EVALUATION")
    correctness = review.get("source_correctness", {})
    if (not isinstance(correctness, dict) or correctness.get("verdict") not in ("SUPPORTED", "RESEARCH_MORE") or
            not nonempty(correctness.get("rationale"))):
        errors.append("LOCATED_MODEL_SOURCE_CORRECTNESS_REVIEW_REQUIRED")
    elif correctness["verdict"] == "RESEARCH_MORE":
        blocking.append({"code": "SOURCE_DOMAIN_RULE_ERROR", "severity": "MAJOR", "status": "OPEN",
                         "reason": correctness["rationale"], "origin": "MODEL_SOURCE_CORRECTNESS_REVIEW"})
    source_evidence = review.get("source_evidence", [])
    if not isinstance(source_evidence, list):
        source_evidence = []; errors.append("SOURCE_EVIDENCE_NOT_LIST")
    valid_evidence = set()
    concept_ids = {row["id"] for row in contract.get("concepts", [])}
    for item in source_evidence:
        if _location(text, item, "SOURCE_EVIDENCE", errors):
            if item.get("concept_id") not in concept_ids or item.get("dimension") not in SOURCE_DIMENSIONS + ("target_reconstruction",):
                errors.append("SOURCE_EVIDENCE_CONCEPT_OR_DIMENSION_UNKNOWN")
            valid_evidence.add((item.get("concept_id"), item.get("dimension")))
    expected_concepts = [c["id"] for c in contract.get("concepts", [])
                         if stage == "BOOKWIDE" or c.get("first_explained_in") == chapter_id]
    dimensions = SOURCE_DIMENSIONS + (("target_reconstruction",) if stage in ("CHAPTER", "BOOKWIDE") else ())
    for ident in expected_concepts:
        for dimension in dimensions:
            if (ident, dimension) not in valid_evidence:
                errors.append("MISSING_LOCATED_SOURCE_EVIDENCE:" + ident + ":" + dimension)
    if stage == "SOURCE_LEARNING":
        material = review.get("source_material_evidence", [])
        if not isinstance(source_texts, dict) or not source_texts or not isinstance(material, list) or not material:
            errors.append("FROZEN_SOURCE_MATERIAL_LOCATIONS_REQUIRED")
        else:
            for item in material:
                if not isinstance(item, dict) or item.get("source_id") not in source_texts:
                    errors.append("UNKNOWN_SOURCE_MATERIAL_ID")
                else:
                    _location(source_texts[item["source_id"]], item, "SOURCE_MATERIAL", errors)
    if stage in ("CHAPTER", "BOOKWIDE"):
        checks = review.get("reader_checks", [])
        if not isinstance(checks, list):
            checks = []; errors.append("READER_CHECKS_NOT_LIST")
        seen = set()
        for item in checks:
            if not isinstance(item, dict) or item.get("audience") not in AUDIENCES or item.get("audience") in seen:
                errors.append("READER_CHECK_AUDIENCE_INVALID_OR_DUPLICATE"); continue
            seen.add(item["audience"])
            if item.get("verdict") not in ("SUPPORTED", "REWORK", "UNVERIFIED") or not nonempty(item.get("rationale")):
                errors.append("READER_CHECK_REASONS_REQUIRED")
            _location(text, item, "READER_CHECK", errors)
            if item.get("verdict") != "SUPPORTED":
                blocking.append({"code": "NOVICE_EXPERT_VALUE_COLLAPSE", "severity": "MAJOR", "status": "OPEN",
                                 "reason": item.get("rationale"), "audience": item["audience"]})
        if seen != set(AUDIENCES):
            errors.append("ALL_READER_PERSPECTIVES_REQUIRE_LOCATED_INTERNAL_REVIEW")
    findings = review.get("findings")
    if not isinstance(findings, list):
        findings = []; errors.append("ACTUAL_READER_FINDINGS_LIST_REQUIRED")
    for finding in findings:
        if not isinstance(finding, dict):
            errors.append("READER_FINDING_OBJECT_REQUIRED"); continue
        if finding.get("severity") not in ("NOTE", "MINOR", "MAJOR", "CRITICAL") or finding.get("status") not in ("OPEN", "KEEP"):
            errors.append("READER_FINDING_CLASSIFICATION_INVALID")
        if not nonempty(finding.get("code")) or not nonempty(finding.get("reason", finding.get("evidence"))):
            errors.append("READER_FINDING_REASON_REQUIRED")
        _location(text, finding, "READER_FINDING", errors)
        if finding.get("status") == "OPEN" and finding.get("severity") in ("MAJOR", "CRITICAL"):
            blocking.append(finding)
    if errors:
        disposition = "HOLD_REVIEW_EVIDENCE"
    elif blocking and (stage == "SOURCE_LEARNING" or any(f.get("code") in SOURCE_CODES for f in blocking)):
        disposition = "STOP_RESEARCH_MORE"
    elif blocking:
        disposition = "CONTENT_REWORK"
    else:
        disposition = "MODEL_INTERNAL_REVIEW_RECORDED"
    return {**base, "status": disposition, "errors": sorted(set(errors)), "blocking_findings": blocking,
            "unreported_defects_discovered": "NOT_ESTABLISHED",
            "reviewer": review.get("reviewer"), "chapter_id": chapter_id}


def review_instructions(contract, chapter_id, stage="SOURCE_LEARNING"):
    """Output instructions for the existing runner's real reviewer call."""
    return {"schema": REVIEW_SCHEMA, "stage": stage,
            "contract_sha256": digest(canonical(contract)), "chapter_id": chapter_id,
            "required_source_concepts": [c["id"] for c in contract["concepts"]
                if stage == "BOOKWIDE" or c["first_explained_in"] == chapter_id],
            "source_dimensions": list(SOURCE_DIMENSIONS) + (["target_reconstruction"] if stage != "SOURCE_LEARNING" else []),
            "task": "Read the actual text and frozen source material. Return JSON with this schema, artifact_sha256, "
                "contract_sha256, reviewer, source_correctness:{verdict:SUPPORTED or RESEARCH_MORE,rationale}, "
                "source_evidence:[{concept_id,dimension,paragraph:1-based blank-line-delimited,quote}], "
                "source_material_evidence:[{source_id,paragraph,quote}], findings:[{code,severity,status:OPEN or KEEP,paragraph,quote,reason}]. "
                "In CHAPTER/BOOKWIDE also return reader_checks with one located MODEL observation for NOVICE, PRACTITIONER, EXPERT: "
                "{audience,verdict:SUPPORTED/REWORK/UNVERIFIED,rationale,paragraph,quote}. "
                "Do not pretend a human read it. SUPPORTED is your bounded review, not established truth. "
                "No mandatory chapter headings, keywords, six scores or artificial defects. Correct rigorous prose may have findings:[]. "
                "A source-domain error or unsupported source-to-target mapping needs RESEARCH_MORE; reader prerequisite or value collapse needs REWORK. "
                "Locate actual source scenes, actions, rules, importance, causal process, counterexamples, conditions and transfer failure boundary. "
                "A dictionary cannot stand in for a causal scene. Treat disputed interpretation as disputed, not an uncontested classical fact."}
