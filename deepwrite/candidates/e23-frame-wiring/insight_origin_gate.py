#!/usr/bin/env python3
"""Experimental fail-closed blind insight-origination structural guard.

This checks disclosed provenance and inspectable model proposals, NOT creative
quality, genuine novelty, or whether a public source semantically contains an
author's conclusion. No network or author-thesis reveal is performed.
"""
from __future__ import annotations

import hashlib
import re


SCHEMA = "deepwrite/insight-origin-blind/v0.1"
ROLES = {"SOURCE_DOMAIN", "PUBLIC_BACKGROUND"}
REQUIRED = (
    "id", "default_question", "alternative_question", "decision_before",
    "decision_after", "source_falsifier", "source_anchor",
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_run_config(cfg):
    """Raise before model calls if blind pre-reveal input constraints are unmet."""
    spec = cfg.get("insight_origin")
    if not isinstance(spec, dict) or spec.get("schema") != SCHEMA:
        raise ValueError("BLIND_ORIGIN_SCHEMA_REQUIRED")
    if spec.get("mode") != "BLIND_PRE_REVEAL":
        raise ValueError("BLIND_ORIGIN_NOT_PRE_REVEAL")
    if cfg.get("channel") != "SHADOW" or cfg.get("run_mode", "fresh") != "fresh":
        raise ValueError("BLIND_ORIGIN_REQUIRES_SHADOW_FRESH")
    if spec.get("author_thesis_disclosed") is not False:
        raise ValueError("BLIND_ORIGIN_AUTHOR_THESIS_DISCLOSURE_NOT_EXCLUDED")
    if not isinstance(cfg.get("wish"), str) or spec.get("neutral_wish_sha256") != sha256(cfg["wish"].encode("utf-8")):
        raise ValueError("BLIND_ORIGIN_NEUTRAL_WISH_SHA_MISMATCH")
    if not isinstance(spec.get("experiment_id"), str) or not re.fullmatch(
        r"[A-Za-z0-9_-]{4,90}", spec["experiment_id"]
    ):
        raise ValueError("BLIND_ORIGIN_EXPERIMENT_ID_REQUIRED")
    for key in ("author_thesis", "revealed_answer", "seed_insight", "selected_lens_id",
                "replay_drafts", "known_findings"):
        if cfg.get(key) or spec.get(key):
            raise ValueError("BLIND_ORIGIN_CONTAMINATING_INPUT_" + key)
    declared = spec.get("source_roles")
    actual = cfg.get("sources")
    if not isinstance(actual, list) or not actual or not isinstance(declared, list):
        raise ValueError("BLIND_ORIGIN_SOURCE_ROLES_REQUIRED")
    if len(declared) != len(actual):
        raise ValueError("BLIND_ORIGIN_SOURCE_INVENTORY_MISMATCH")
    seen = set()
    for row, pinned in zip(declared, actual):
        if not isinstance(row, dict) or not isinstance(pinned, dict):
            raise ValueError("BLIND_ORIGIN_INVALID_SOURCE")
        if row.get("role") not in ROLES:
            raise ValueError("BLIND_ORIGIN_SOURCE_ROLE_DISALLOWED")
        if (not isinstance(row.get("path"), str) or not row["path"] or
            not isinstance(row.get("sha256"), str) or
            row.get("path") != pinned.get("path") or row.get("sha256") != pinned.get("sha256")):
            raise ValueError("BLIND_ORIGIN_PIN_MISMATCH")
        if row["path"] in seen:
            raise ValueError("BLIND_ORIGIN_DUPLICATE_SOURCE")
        seen.add(row["path"])
    return {
        "status": "PASS_DISCLOSED_INPUT_CONTRACT_ONLY",
        "semantic_input_cleanliness": "UNVERIFIED",
        "author_conclusion_hidden": "SELF_DECLARED_NOT_ATTESTED",
        "insight_quality": "UNVERIFIED",
    }


def inspect_proposals(candidate, source_text):
    """Validate model-created rival questions before any author conclusion reveal.

    Structural PASS does not select a winner or attest independent discovery.
    source_text must be the exact hash-pinned source map from the E18 runner.
    """
    errors = []
    if not isinstance(candidate, dict):
        return {"status": "STOP_INVALID_MODEL_FRAME", "errors": ["NOT_OBJECT"],
                "semantic_novelty": "UNVERIFIED"}
    if candidate.get("origin_status") != "MODEL_PROPOSAL_UNVERIFIED":
        errors.append("ORIGIN_STATUS_MUST_REMAIN_UNVERIFIED")
    if any(key in candidate for key in ("author_thesis", "author_approved",
                                         "human_acceptance", "reveal_answer")):
        errors.append("PREMATURE_AUTHOR_AUTHORITY_OR_REVEAL")
    lenses = candidate.get("lenses")
    if not isinstance(lenses, list) or len(lenses) < 3:
        errors.append("AT_LEAST_THREE_RIVAL_QUESTIONS_REQUIRED")
        lenses = lenses if isinstance(lenses, list) else []
    ids, distinctions = set(), set()
    for ix, lens in enumerate(lenses):
        if not isinstance(lens, dict):
            errors.append("INVALID_LENS_" + str(ix))
            continue
        for field in REQUIRED:
            value = lens.get(field)
            if field == "source_anchor":
                continue
            if not isinstance(value, str) or len(value.strip()) < 20:
                errors.append("MISSING_" + field.upper() + "_" + str(ix))
        ident = lens.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", ident):
            errors.append("INVALID_ID_" + str(ix))
        elif ident in ids:
            errors.append("DUPLICATE_ID_" + str(ix))
        else:
            ids.add(ident)
        contrast = tuple(str(lens.get(k)) for k in (
            "alternative_question", "decision_before", "decision_after"))
        if contrast in distinctions:
            errors.append("DUPLICATE_CONTRAST_" + str(ix))
        distinctions.add(contrast)
        if (isinstance(lens.get("decision_before"), str) and
            isinstance(lens.get("decision_after"), str) and
            lens["decision_before"].strip() == lens["decision_after"].strip()):
            errors.append("NO_DECISION_DIFFERENCE_" + str(ix))
        anchor = lens.get("source_anchor")
        if (not isinstance(anchor, dict) or
            not isinstance(anchor.get("path"), str) or
            not isinstance(anchor.get("quote"), str) or
            len(anchor["quote"].strip()) < 12 or
            anchor["path"] not in source_text or
            anchor["quote"] not in source_text[anchor["path"]]):
            errors.append("UNVERIFIED_SOURCE_ANCHOR_" + str(ix))
    return {
        "status": ("STOP_INVALID_MODEL_FRAME" if errors else
                   "PASS_STRUCTURAL_ORIGIN_FROZEN_SEMANTICS_UNVERIFIED"),
        "errors": sorted(set(errors)),
        "candidate_count": len(lenses),
        "semantic_novelty": "UNVERIFIED",
        "author_acceptance": "NOT_RUN",
        "human_blind_review": "NOT_RUN",
        "source_cleanliness": "DECLARATIVE_ONLY_NOT_PROVEN",
    }
