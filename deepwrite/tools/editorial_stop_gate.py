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
P2 = {"SOURCE_MECHANISM_MISSING", "READER_CAUSAL_GAP", "LITERARY_COMPREHENSION_GAP"}
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


def audit_initial(findings, manuscripts, history=None, *, scope=None):
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
        f.setdefault("status", "OPEN")
        if f["status"] != "OPEN":
            checked.append(f)
            continue
        case = f.get("edit_case")
        kind = case.get("classification") if isinstance(case, dict) else None
        severity = f.get("severity")
        if severity not in SERIOUS and kind not in HARD | P2:
            # A cosmetic note must not ride along when a different finding forces a revision.
            if severity in ("NOTE", "MINOR"):
                f.update(status="KEEP", reason="Optional wording or style observation. Preserve current prose.")
                rows.append({"id": issue_id, "artifact_id": art, "decision": "KEEP_STYLE_NO_CHURN"})
            checked.append(f)
            continue

        failure = None
        if kind not in ALLOWED:
            failure = "MISSING_CLASSIFIED_EDIT_CASE"
        else:
            quote = case.get("baseline_quote")
            part = f.get("paragraph")
            ps = paragraphs(manuscripts[art])
            if kind == "STYLE_ONLY":
                f.update(status="KEEP", reason="Optional stylistic preference. Preserve current prose.")
                rows.append({"id": issue_id, "artifact_id": art, "decision": "KEEP_STYLE_NO_CHURN"})
                checked.append(f)
                continue
            locations = ([i for i, paragraph in enumerate(ps, 1) if quote in paragraph]
                         if isinstance(quote, str) and len(quote.strip()) >= 8 else [])
            if type(part) is not int or part not in locations:
                if len(locations) == 1:
                    f.update(paragraph=locations[0], reported_paragraph=part)
                    part = locations[0]
                else:
                    failure = "BASELINE_QUOTE_NOT_IN_LOCATED_PARAGRAPH"
            if not failure and not all(substantive(case.get(name)) for name in
                         ("reader_harm", "minimal_remedy", "regression_risk")):
                failure = "UNSUBSTANTIATED_READER_HARM_OR_REMEDY"
        if failure:
            holds.append({"id": issue_id, "artifact_id": art, "reason": failure})
            checked.append(f)
            continue

        quote = case["baseline_quote"]
        paragraph = ps[part - 1]
        position = paragraph.find(quote)
        paragraph_sha = hashlib.sha256(paragraph.encode()).hexdigest()
        key = fingerprint(art, quote)
        related = None
        for prior_key, prior in {**history, **new_history}.items():
            if prior_key == key:
                related = prior_key
                break
            if (isinstance(prior, dict) and prior.get("artifact_id") == art
                    and prior.get("paragraph_sha256") == paragraph_sha
                    and prior["quote_start"] < position + len(quote)
                    and position < prior["quote_end"]):
                related = prior_key
                break
        if related in new_history:
            holds.append({"id": issue_id, "artifact_id": art,
                          "reason": "DUPLICATE_DEFECT_IN_SAME_REVIEW",
                          "fingerprint": key})
        elif related in history:
            prior = history[related]
            baseline_sha = hashlib.sha256(manuscripts[art].encode("utf-8")).hexdigest()
            if (scope is not None and isinstance(prior, dict) and
                    prior.get("scope") == scope and prior.get("id") == issue_id and
                    prior.get("baseline_sha256") == baseline_sha and related == key):
                # A paused stage may re-evaluate the same frozen review on resume.
                # Reusing the exact prior decision is recovery, not a new edit.
                rows.append({"id": issue_id, "artifact_id": art,
                             "decision": "REPLAY_SAME_FROZEN_SCOPE",
                             "fingerprint": key, "semantic_quality": "UNVERIFIED"})
            else:
                holds.append({"id": issue_id, "artifact_id": art,
                              "reason": "REPEATED_BASELINE_DEFECT_WITHOUT_NEW_INDEPENDENT_EVIDENCE",
                              "fingerprint": key})
        else:
            if severity not in SERIOUS:
                f["severity"] = "MAJOR"
            rows.append({"id": issue_id, "artifact_id": art, "decision": "ALLOW_ONE_EVIDENCED_REPAIR",
                         "classification": kind, "fingerprint": key,
                         "semantic_quality": "MODEL_PROPOSAL_UNVERIFIED"})
            new_history[key] = {"id": issue_id, "artifact_id": art, "classification": kind,
                                "baseline_quote": case["baseline_quote"], "scope": scope,
                                "paragraph_sha256": paragraph_sha, "quote_start": position,
                                "quote_end": position + len(quote),
                                "baseline_sha256": hashlib.sha256(manuscripts[art].encode("utf-8")).hexdigest(),
                                "semantic_quality": "UNVERIFIED"}
        checked.append(f)

    return {"schema": SCHEMA, "status": "HOLD" if holds else "PASS_PROPOSALS_ONLY",
            "disposition": ("HOLD_UNVERIFIED" if holds else "PASS_SCOPED"
                            if any(f.get("status") == "OPEN" for f in checked) else "KEEP_NO_CHURN"),
            "findings": checked, "decisions": rows, "holds": holds, "new_history": new_history,
            "author_acceptance": "PENDING", "independent_reader": "UNVERIFIED",
            "quality_improvement": "UNVERIFIED"}


def corroborate(proposal, reply, manuscripts):
    """Check an independent model call's evidence before proposals may drive work."""
    proposals = {f["id"]: f for f in proposal["findings"]
                 if f.get("status") == "OPEN" and isinstance(f.get("edit_case"), dict)}
    rows = reply.get("findings") if isinstance(reply, dict) else None
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("EDITORIAL_CONFIRMATION_RESULT_INVALID")
    if len(rows) != len(proposals) or {row.get("id") for row in rows} != proposals.keys():
        raise ValueError("EDITORIAL_CONFIRMATION_SET_MISMATCH")
    for row in rows:
        issue = proposals[row["id"]]
        verdict, quote = row.get("verdict"), row.get("quote")
        if verdict not in {"CONFIRMED", "PREFERENCE_ONLY", "UNVERIFIED"} or not substantive(row.get("reason")):
            raise ValueError("EDITORIAL_CONFIRMATION_EVIDENCE_MISSING")
        paragraph = paragraphs(manuscripts[issue["artifact_id"]])[issue["paragraph"] - 1]
        if not isinstance(quote, str) or len(quote.strip()) < 8 or quote not in paragraph:
            raise ValueError("EDITORIAL_CONFIRMATION_QUOTE_UNLOCATED")
        if verdict == "PREFERENCE_ONLY" and issue["edit_case"]["classification"] in P2:
            issue.update(status="KEEP", reason="Separate review found no material reader harm: " + row["reason"])
        elif verdict != "CONFIRMED":
            proposal["holds"].append({"id": row["id"], "reason": "EDITORIAL_PROPOSAL_NOT_CORROBORATED"})
    proposal["confirmation"] = rows
    proposal["status"] = "HOLD" if proposal["holds"] else "PASS_PROPOSALS_ONLY"
    proposal["disposition"] = ("HOLD_UNVERIFIED" if proposal["holds"] else "PASS_SCOPED"
                               if any(f.get("status") == "OPEN" for f in proposal["findings"]) else "KEEP_NO_CHURN")


def verify_edit_result(old_text, new_text):
    """Mechanical no-op detector only. Full prose/reader improvement is not computable."""
    old = "".join(old_text.split())
    new = "".join(new_text.split())
    if old == new:
        return {"status": "HOLD_NO_SUBSTANTIVE_CHANGE", "semantic_quality": "UNVERIFIED"}
    return {"status": "CHANGED_NEEDS_SEMANTIC_RECHECK", "semantic_quality": "UNVERIFIED"}
