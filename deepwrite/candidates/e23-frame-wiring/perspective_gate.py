#!/usr/bin/env python3
"""DeepWrite perspective prewrite guard, experimental only.

This is a provenance and STOP decision aid, never an autonomous creativity judge.
Reads only local files: python perspective_gate.py --manifest manifest.json --output result.json
No network, no OpenAI calls, no publication or update of CURRENT.json.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

FIELDS = ("source_assumption", "counterinterpretation", "source_mechanism",
          "source_falsifier", "target_default", "target_break",
          "decision_before", "decision_after", "target_falsifier",
          "why_book_architecture_changes")
ALLOWED = {"RECOVERED", "REFRAME", "HYPOTHESIS_NEW"}
PRIOR = {"COVERED", "PARTIAL", "NOT_FOUND_UNVERIFIED"}

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def read_locked(spec, root, issues, kind):
    p = (root / spec.get("path", "")).resolve()
    if not p.is_relative_to(root.resolve()) or not p.is_file():
        issues.append(kind + "_INVALID_PATH")
        return None
    data = p.read_bytes()
    if len(data) == 0:
        issues.append(kind + "_EMPTY")
        return None
    digest = sha256(data)
    if digest != spec.get("sha256"):
        issues.append(kind + "_SHA_MISMATCH")
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        issues.append(kind + "_NOT_UTF8")
        return None

def evaluate(manifest, root):
    issues = []
    if manifest.get("schema") != "deepwrite/perspective-inversion/v0.1":
        issues.append("INVALID_SCHEMA")
    prior_specs = manifest.get("prior_drafts", [])
    source_specs = manifest.get("source_materials", [])
    lenses = manifest.get("lenses", [])
    if not prior_specs:
        issues.append("NO_FROZEN_PRIOR_DRAFT")
    if not source_specs:
        issues.append("NO_SOURCE_DOMAIN_EVIDENCE")
    priors = [read_locked(x, root, issues, "PRIOR") for x in prior_specs]
    sources = [read_locked(x, root, issues, "SOURCE") for x in source_specs]
    if len(lenses) < 3:
        issues.append("LESS_THAN_THREE_COMPETING_LENSES")
    lens_results = []
    seen = set()
    for lens in lenses:
        errs = []
        for f in FIELDS:
            if not isinstance(lens.get(f), str) or len(lens[f].strip()) < 12:
                errs.append("MISSING_REASONING_" + f.upper())
        fingerprint = (lens.get("source_assumption","").strip(),
                       lens.get("counterinterpretation","").strip(),
                       lens.get("target_break","").strip())
        if fingerprint in seen:
            errs.append("DUPLICATE_FRAME")
        seen.add(fingerprint)
        claim_type = lens.get("claim_type")
        if claim_type not in ALLOWED:
            errs.append("INVALID_CLAIM_TYPE")
        evidences = lens.get("source_quotes", [])
        if not evidences:
            errs.append("NO_SOURCE_QUOTES")
        for e in evidences:
            ix = e.get("source_index", -1)
            quote = e.get("quote", "")
            if (not isinstance(ix, int) or ix < 0 or ix >= len(sources)
                or sources[ix] is None or len(quote) < 12 or quote not in sources[ix]):
                errs.append("SOURCE_QUOTE_NOT_VERIFIED")
        pchecks = lens.get("prior_checks", [])
        if not pchecks:
            errs.append("NO_PRIOR_ART_COMPARISON")
        inspected = set()
        any_covered = False
        for p in pchecks:
            ix = p.get("prior_index", -1)
            verdict = p.get("verdict")
            quote = p.get("quote", "")
            if (not isinstance(ix, int) or ix < 0 or ix >= len(priors)
                or priors[ix] is None):
                errs.append("INVALID_PRIOR_POINTER")
                continue
            inspected.add(ix)
            if verdict not in PRIOR:
                errs.append("INVALID_PRIOR_VERDICT")
            if verdict in ("COVERED", "PARTIAL"):
                if len(quote) < 12 or quote not in priors[ix]:
                    errs.append("PRIOR_COVERAGE_QUOTE_NOT_VERIFIED")
                if verdict == "COVERED":
                    any_covered = True
            elif quote:
                # A NOT_FOUND claim must not manufacture a quote from the prior draft.
                errs.append("NOT_FOUND_MUST_HAVE_EMPTY_QUOTE")
        if len(inspected) != len(priors):
            errs.append("UNEXAMINED_PRIOR_DRAFT")
        if claim_type == "HYPOTHESIS_NEW" and any_covered:
            errs.append("FALSE_NOVELTY_CONFLICTS_WITH_COVERED_PRIOR")
        if claim_type == "RECOVERED" and not any_covered:
            errs.append("RECOVERED_BUT_NO_COVERED_PRIOR")
        disposition = ("HOLD_STRUCTURAL_DEFECT" if errs else
                       "REJECT_AS_NEW_DISCOVERY" if any_covered else
                       "HOLD_HUMAN_SEMANTIC_AND_ADVERSARIAL_REVIEW")
        lens_results.append({"id": lens.get("id"), "claim_type": claim_type,
                             "errors": sorted(set(errs)), "status": disposition,
                             "prior_status": [p.get("verdict") for p in pchecks]})
    if any(x["errors"] for x in lens_results):
        issues.append("LENS_VALIDATION_FAILURE")
    return {
        "schema": "deepwrite/perspective-prewrite-result/v0.1",
        "evidence_only": True,
        "candidate_runner": "NOT_ACTIVE",
        "quality_or_novelty_auto_pass": False,
        "structural": "FAIL" if issues else "PASS",
        "issues": sorted(set(issues)),
        "lenses": lens_results,
        "prewrite_decision": ("STOP_REPAIR_INPUTS" if issues else
                              "HOLD_PERSPECTIVE_ADJUDICATION_NO_BOOK_REWRITE"),
        "author_quality": "PENDING",
        "independent_blind_review": "NOT_RUN"
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = evaluate(manifest, manifest_path.parent)
    result["manifest_sha256"] = sha256(manifest_path.read_bytes())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(result["structural"], result["prewrite_decision"])
    return 2 if result["structural"] == "FAIL" else 0

if __name__ == "__main__":
    raise SystemExit(main())