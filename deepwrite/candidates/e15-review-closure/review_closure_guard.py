#!/usr/bin/env python3
"""Candidate DeepWrite G6 closeout preflight. Structural evidence only, not writing-quality certification."""
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[a-f0-9]{64}$")
BLOCKING = {"CRITICAL", "MAJOR"}
SEVERITIES = BLOCKING | {"MINOR", "NOTE"}
STATUSES = {"OPEN", "CLOSED", "WAIVED", "DEFERRED"}


def valid_sha(value):
    return isinstance(value, str) and bool(SHA.fullmatch(value))


def check(record):
    errors, warnings = [], []
    if not isinstance(record, dict) or record.get("schema") != "deepwrite/review-closeout/v0":
        return {"status": "HOLD", "errors": ["invalid schema"], "warnings": []}
    source = record.get("baseline_sha256")
    target = record.get("candidate_sha256")
    if not valid_sha(source) or not valid_sha(target) or source == target:
        errors.append("a distinct, pinned baseline_sha256 and candidate_sha256 are required")
    comparison = record.get("comparison")
    if not isinstance(comparison, dict) or not all((
        comparison.get("baseline_read") is True,
        comparison.get("candidate_read") is True,
        isinstance(comparison.get("reviewed_units"), list),
        bool(comparison.get("reviewed_units")),
        bool(str(comparison.get("comparison_rationale") or "").strip()),
    )):
        errors.append("actual baseline/candidate reading, scope and rationale must be recorded")
    findings = record.get("findings")
    if not isinstance(findings, list):
        return {"status": "HOLD", "errors": errors + ["findings must be a list"], "warnings": warnings}
    ids = set()
    for index, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"finding[{index}] must be an object")
            continue
        ident = f.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            errors.append(f"finding[{index}] missing/duplicate id")
        ids.add(ident)
        severity, status = f.get("severity"), f.get("status")
        if severity not in SEVERITIES or status not in STATUSES:
            errors.append(f"{ident}: invalid severity/status")
            continue
        if not str(f.get("location") or "").strip() or not str(f.get("issue") or "").strip():
            errors.append(f"{ident}: location and issue are required")
        if status == "CLOSED":
            if f.get("revised_sha256") != target or not str(f.get("recheck_evidence") or "").strip():
                errors.append(f"{ident}: closeout must be rechecked against current candidate SHA")
        elif severity in BLOCKING and status in ("OPEN", "DEFERRED"):
            errors.append(f"{ident}: unresolved {severity} finding blocks release")
        elif status == "WAIVED":
            if severity == "CRITICAL":
                errors.append(f"{ident}: CRITICAL finding cannot be waived")
            elif severity == "MAJOR" and (f.get("authority") not in {"AUTHOR", "USER"} or not str(f.get("risk_acceptance") or "").strip()):
                errors.append(f"{ident}: MAJOR waiver requires recorded author/user risk acceptance")
            # A recorded authority field is NOT proof of actual author approval.
        elif status in ("OPEN", "DEFERRED"):
            warnings.append(f"{ident}: nonblocking finding pending")
    return {"status": "HOLD" if errors else "PASS_STRUCTURAL_ONLY", "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("closeout_json", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.closeout_json.read_text(encoding="utf-8"))
        result = check(data)
    except (OSError, ValueError) as exc:
        result = {"status": "HOLD", "errors": [str(exc)], "warnings": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS_STRUCTURAL_ONLY" else 2)


if __name__ == "__main__":
    main()
