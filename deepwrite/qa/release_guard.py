#!/usr/bin/env python3
"""Conservative *structural* release / rollback gate; NOT a judge of book quality.

Usage: python3 release_guard.py <candidate_release.json>
Exit 0 if structurally ready to be *reviewed for promotion*; 1 if blocked.
The tool never writes CURRENT pointers and does not validate human-authorship.
"""
import json
import re
import sys
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
STATUS = {"PASS", "PENDING", "NOT_RUN", "FAIL", "UNVERIFIED"}


def evaluate(d):
    errors = []
    if d.get("schema") != "deepwrite/release-evidence/v0.1": errors.append("schema mismatch")
    for side in ("baseline", "candidate"):
        v = d.get(side, {})
        for field in ("spec_git_commit", "artifact_sha256", "evaluation_sha256"):
            if field == "spec_git_commit":
                if not isinstance(v.get(field), str) or not re.fullmatch(r"[0-9a-f]{40}", v[field]): errors.append(f"{side}.{field}: pin 40-hex commit")
            elif not isinstance(v.get(field), str) or not SHA_RE.fullmatch(v[field]): errors.append(f"{side}.{field}: pin SHA256")
    if d.get("requested_channel") not in ("CANDIDATE_OPT_IN", "PROMOTION_REQUEST", "ROLLBACK"):
        errors.append("unsupported requested_channel")
    if not d.get("immutable_baseline", False): errors.append("immutable_baseline required")
    if not d.get("rollback_plan", {}).get("verified_checkpoint_sha256") or not SHA_RE.fullmatch(str(d["rollback_plan"].get("verified_checkpoint_sha256", ""))):
        errors.append("rollback verified checkpoint required")
    for k in ("engineering", "content_quality", "author_acceptance", "external_validation"):
        status = d.get("gates", {}).get(k)
        if status not in STATUS: errors.append(f"gates.{k} missing/invalid")
    if d.get("requested_channel") == "PROMOTION_REQUEST":
        if any(d.get("gates", {}).get(k) != "PASS" for k in ("engineering", "content_quality", "author_acceptance", "external_validation")):
            errors.append("promotion requires all 4 externalized PASS gates")
        for label in ("actual_reader_count", "independent_topic_count"):
            if not isinstance(d.get("evidence", {}).get(label), int) or d["evidence"][label] < (2 if label == "actual_reader_count" else 3):
                errors.append(f"evidence.{label} below minimum")
        if d.get("evidence", {}).get("regression_non_degradation") is not True:
            errors.append("regression non-degradation unverified")
        if d.get("author_promotion_approval") is not True:
            errors.append("author_promotion_approval absent")
    elif d.get("requested_channel") == "CANDIDATE_OPT_IN":
        if not d.get("per_project_explicit_opt_in", False): errors.append("explicit per-project opt-in required")
    else:
        if d.get("rollback_plan", {}).get("preserve_failed_candidate") is not True:
            errors.append("rollback must preserve old candidate")
    return errors


def main(argv):
    if len(argv) != 2:
        print("Usage: release_guard.py evidence.json", file=sys.stderr); return 2
    try: data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (ValueError, OSError) as e: print(f"BLOCKED: {e}"); return 1
    issues = evaluate(data)
    print(json.dumps({"status":"BLOCKED" if issues else "STRUCTURAL_READY_FOR_REVIEW_NOT_HUMAN_VERIFIED", "issues":issues}, ensure_ascii=False, indent=2))
    return 1 if issues else 0

if __name__ == "__main__": sys.exit(main(sys.argv))
