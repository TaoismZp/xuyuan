#!/usr/bin/env python3
"""Evidence-first editorial stopping gate for DeepWrite candidate writing loops.

This is a machine-checkable refusal/identity gate, NOT a machine judge of prose.
Semantic benefit, author acceptance and reader delight remain UNVERIFIED.
"""
from __future__ import annotations

import hashlib
import re

SCHEMA = "deepwrite/editorial-stop-gate/v1"
HARD = {"FACT_OR_MATH_ERROR", "EX_ANTE_CAUSAL_ERROR"}
P2 = {"SOURCE_MECHANISM_MISSING", "READER_CAUSAL_GAP"}
OPTIONAL = {"STYLE_ONLY"}
ALLOWED = HARD | P2 | OPTIONAL
SERIOUS = {"MAJOR", "CRITICAL"}


def paragraphs(text):
    return [p for p in re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n").replace("\r", "\n")) if p.strip()]


def fingerprint(artifact, quote):
    normalized = " ".join(quote.split())
    return hashlib.sha256((artifact + "\n" + normalized).encode("utf-8")).hexdigest()


def substantive(value):
    return isinstance(value, str) and len(value.strip()) >= 12 and len(set(value.strip())) >= 6


def audit_initial(findings, manuscripts, history=None):
    """Return checked proposals, a durable receipt, and newly seen issue identities.

    Only model-origin OPEN MAJOR/CRITICAL findings can authorize automated rewriting.
    Source/reader-specific gates and caller-frozen findings keep their existing contracts.
    Missing evidence must HOLD, not be silently downgraded to KEEP.
    """
    history = history or {}
    checked, rows, new_history, holds = [], [], {}, []
    if not isinstance(findings, list) or not isinstance(manuscripts, dict) or not isinstance(history, dict):
        raise ValueError("INVALID_EDITORIAL_GATE_INPUT")

    for raw in findings:
        if not isinstance(raw, dict):
            raise ValueError("EDITORIAL_FINDING_NOT_OBJECT")
        f = dict(raw)
        art = f.get("artifact_id")
        if art not in manuscripts:
            raise ValueError("EDITORIAL_FINDING_UNKNOWN_ARTIFACT")
        issue_id = f.get("id")
        if f.get("status") != "OPEN" or f.get("severity") not in SERIOUS or f.get("kind", "model_review") != "model_review":
            checked.append(f)
            continue
        if str(issue_id).startswith("reader_"):
            # Explicit other gate; never claim to have evaluated its semantic quality.
            rows.append({"id": issue_id, "artifact_id": art, "decision": "DELEGATED_TO_EXISTING_READER_GATE"})
            checked.append(f)
            continue

        case = f.get("edit_case")
        failure = None
        if not isinstance(case, dict) or case.get("classification") not in ALLOWED:
            failure = "MISSING_CLASSIFIED_EDIT_CASE"
        else:
            quote = case.get("baseline_quote")
            part = f.get("paragraph")
            ps = paragraphs(manuscripts[art])
            if type(part) is not int or not 1 <= part <= len(ps):
                failure = "INVALID_EXACT_BASELINE_PARAGRAPH"
            elif not isinstance(quote, str) or len(quote.strip()) < 8 or quote not in ps[part - 1]:
                failure = "BASELINE_QUOTE_NOT_IN_LOCATED_PARAGRAPH"
            elif not all(substantive(case.get(name)) for name in
                         ("reader_harm", "minimal_remedy", "regression_risk")):
                failure = "UNSUBSTANTIATED_READER_HARM_OR_REMEDY"
        if failure:
            holds.append({"id": issue_id, "artifact_id": art, "reason": failure})
            checked.append(f)
            continue

        kind = case["classification"]
        key = fingerprint(art, case["baseline_quote"])
        if kind in OPTIONAL:
            f["status"] = "KEEP"
            f["reason"] = ("STYLE_ONLY_WITHOUT_VERIFIED_READER_HARM: retain existing prose; "
                           "compare with independent readers before reconsidering.")
            rows.append({"id": issue_id, "artifact_id": art, "decision": "KEEP_STYLE_NO_CHURN",
                         "fingerprint": key, "semantic_quality": "UNVERIFIED"})
        elif key in history or key in new_history:
            holds.append({"id": issue_id, "artifact_id": art,
                          "reason": "REPEATED_BASELINE_DEFECT_WITHOUT_NEW_INDEPENDENT_EVIDENCE",
                          "fingerprint": key})
        else:
            rows.append({"id": issue_id, "artifact_id": art, "decision": "ALLOW_ONE_EVIDENCED_REPAIR",
                         "classification": kind, "fingerprint": key,
                         "semantic_quality": "MODEL_PROPOSAL_UNVERIFIED"})
            new_history[key] = {"id": issue_id, "artifact_id": art, "classification": kind,
                                "baseline_quote": case["baseline_quote"],
                                "semantic_quality": "UNVERIFIED"}
        checked.append(f)

    return {"schema": SCHEMA, "status": "HOLD" if holds else "PASS_PROPOSALS_ONLY",
            "findings": checked, "decisions": rows, "holds": holds, "new_history": new_history,
            "author_acceptance": "PENDING", "independent_reader": "UNVERIFIED",
            "quality_improvement": "UNVERIFIED"}


def verify_edit_result(old_text, new_text):
    """Mechanical no-op detector only. Full prose/reader improvement is not computable."""
    old = "".join(old_text.split())
    new = "".join(new_text.split())
    if old == new:
        return {"status": "HOLD_NO_SUBSTANTIVE_CHANGE", "semantic_quality": "UNVERIFIED"}
    return {"status": "CHANGED_NEEDS_SEMANTIC_RECHECK", "semantic_quality": "UNVERIFIED"}
