#!/usr/bin/env python3
"""Source-domain-first chapter architecture gate for an opt-in DeepWrite project.

This check enforces real source-byte identity and declared source-to-book
dependencies before E18 can write. It cannot prove research happened earlier,
discover literary quality, authenticate author approval, or decide chapter count.
When evidence is absent, fail CLOSED instead of silently guessing a template.
"""
from __future__ import annotations

import hashlib
import re

SCHEMA = "deepwrite/source-first-architecture/v1"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def text(value):
    return isinstance(value, str) and len(value.strip()) >= 8


def validate(config: dict, read_bytes) -> dict:
    """read_bytes(relative_path) returns actual project file bytes; never trust a path alone.

    Caller must separately verify project-source authorization. All evidence is
    structural, not a semantic or chronological "research was good" certificate.
    """
    if not isinstance(config, dict):
        raise ValueError("SOURCE_FIRST_CONFIG_REQUIRED")
    arch = config.get("source_first_architecture")
    if not isinstance(arch, dict) or arch.get("schema") != SCHEMA:
        raise ValueError("SOURCE_FIRST_ARCHITECTURE_REQUIRED")
    if arch.get("project_id") != config.get("project_id"):
        raise ValueError("SOURCE_FIRST_WRONG_PROJECT")
    if arch.get("status") != "PROVISIONAL_NOT_AUTHOR_APPROVED":
        raise ValueError("SOURCE_FIRST_CANNOT_AUTHENTICATE_AUTHOR_APPROVAL")
    sources = {row["path"]: row["sha256"] for row in config.get("sources", [])
               if isinstance(row, dict) and isinstance(row.get("path"), str)
               and isinstance(row.get("sha256"), str)}
    study = arch.get("source_study")
    if (not isinstance(study, dict) or study.get("path") not in sources or
            study.get("sha256") != sources.get(study.get("path")) or
            not isinstance(study["sha256"], str) or
            not HEX64.fullmatch(study["sha256"])):
        raise ValueError("SOURCE_FIRST_FROZEN_STUDY_SOURCE_REQUIRED")
    if digest(read_bytes(study["path"])) != study["sha256"]:
        raise ValueError("SOURCE_FIRST_STUDY_BYTES_MISMATCH")
    chapters = config.get("chapters", [])
    ids = [c["artifact_id"] for c in chapters if isinstance(c, dict) and "artifact_id" in c]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("SOURCE_FIRST_CHAPTERS_REQUIRED")
    concepts = arch.get("source_concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError("SOURCE_FIRST_NATIVE_CONCEPTS_REQUIRED")
    concept_ids = set()
    for concept in concepts:
        if not isinstance(concept, dict) or not text(concept.get("id")):
            raise ValueError("SOURCE_FIRST_CONCEPT_ID_REQUIRED")
        if concept["id"] in concept_ids:
            raise ValueError("SOURCE_FIRST_DUPLICATE_CONCEPT")
        concept_ids.add(concept["id"])
        p = concept.get("source_path")
        if p not in sources or p == study["path"]:
            raise ValueError("SOURCE_FIRST_ORIGINAL_SOURCE_REFERENCE_REQUIRED")
        raw = read_bytes(p)
        if digest(raw) != sources[p]:
            raise ValueError("SOURCE_FIRST_ORIGINAL_SOURCE_BYTES_MISMATCH")
        anchor = concept.get("quote")
        if not text(anchor) or anchor not in raw.decode("utf-8"):
            raise ValueError("SOURCE_FIRST_CLAIM_NOT_LOCATED_IN_ORIGINAL_SOURCE")
        for k in ("causal_mechanism", "counterinterpretation", "transfer_limit"):
            if not text(concept.get(k)):
                raise ValueError("SOURCE_FIRST_NATIVE_MECHANISM_OR_BOUNDARY_REQUIRED")
    rivals = arch.get("rival_directions")
    if not isinstance(rivals, list) or len(rivals) < 2:
        raise ValueError("SOURCE_FIRST_RIVAL_DIRECTIONS_REQUIRED")
    directions = set()
    for r in rivals:
        if not isinstance(r, dict) or not text(r.get("id")) or r["id"] in directions:
            raise ValueError("SOURCE_FIRST_RIVAL_ID_INVALID_OR_DUPLICATE")
        directions.add(r["id"])
        for k in ("source_question", "reader_problem", "tradeoff"):
            if not text(r.get(k)):
                raise ValueError("SOURCE_FIRST_RIVAL_JUSTIFICATION_REQUIRED")
    if arch.get("selected_direction_id") not in directions:
        raise ValueError("SOURCE_FIRST_SELECTED_RIVAL_REQUIRED")
    if not text(arch.get("why_selected_over_rivals")):
        raise ValueError("SOURCE_FIRST_SELECTION_REASON_REQUIRED")
    book = arch.get("book_design")
    if not isinstance(book, dict) or book.get("status") != "PROVISIONAL":
        raise ValueError("SOURCE_FIRST_BOOK_BLUEPRINT_MUST_BE_PROVISIONAL")
    if not text(book.get("why_these_chapters_not_source_outline")):
        raise ValueError("SOURCE_FIRST_CHAPTER_TOPOLOGY_RATIONALE_REQUIRED")
    allocations = book.get("chapter_contributions")
    if not isinstance(allocations, list) or len(allocations) != len(ids):
        raise ValueError("SOURCE_FIRST_CHAPTER_CONTRIBUTIONS_REQUIRED")
    if {c.get("chapter_id") for c in allocations if isinstance(c, dict)} != set(ids):
        raise ValueError("SOURCE_FIRST_CHAPTER_COVERAGE_MISMATCH")
    for c in allocations:
        deps = c.get("source_concept_ids")
        if not isinstance(deps, list) or not deps or not set(deps) <= concept_ids:
            raise ValueError("SOURCE_FIRST_CHAPTER_NATIVE_SOURCE_DEPENDENCY_REQUIRED")
        if not text(c.get("distinct_reader_change")):
            raise ValueError("SOURCE_FIRST_CHAPTER_READER_CHANGE_REQUIRED")
    return {
        "status": "PASS_ENGINEERING_ONLY_PROVISIONAL_SOURCE_ARCHITECTURE",
        "project_id": config["project_id"],
        "study_path": study["path"], "study_sha256": study["sha256"],
        "source_concepts": sorted(concept_ids),
        "rival_directions": sorted(directions),
        "chapter_ids": ids,
        "chronology_independently_verified": False,
        "source_semantic_correctness": "UNVERIFIED",
        "three_level_reader_value": "UNVERIFIED",
        "knowledge_compounding": "UNVERIFIED",
        "chapter_number_author_approval": "PENDING",
        "authorization_and_model_identity": "REQUIRE_SEPARATE_PROOF"
    }
