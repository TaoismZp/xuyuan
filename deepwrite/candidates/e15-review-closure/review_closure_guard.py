#!/usr/bin/env python3
"""E15 closeout guard v1: real bytes and bounded assertions; never literary proof.

Caller owns the complete artifact inventory and separately frozen findings.
A self-authored record is not proof that all defects were discovered.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

SCHEMA = "deepwrite/review-closeout/v1"
SHA = re.compile(r"[0-9a-f]{64}")
RANK = {"NOTE": 0, "MINOR": 1, "MAJOR": 2, "CRITICAL": 3}
STATUSES = {"OPEN", "CLOSED", "KEEP"}
KINDS = {"computable", "model_review"}
MAX_BYTES = 8_000_000

def sha(data):
    return hashlib.sha256(data).hexdigest()

def compact(text):
    return "".join(text.split())

def paragraphs(text):
    return [p for p in re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n").replace("\r", "\n")) if p.strip()]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read_artifact(root, item):
    require(isinstance(item, dict), "artifact version must be object")
    name = item.get("path")
    require(isinstance(name, str) and name, "artifact path required")
    rel = PurePosixPath(name)
    require(not rel.is_absolute() and ".." not in rel.parts and "\\" not in name
            and ":" not in name and rel.as_posix() == name and name != ".",
            "artifact path must be canonical relative POSIX")
    p = root.joinpath(*rel.parts)
    require(not any(x.is_symlink() for x in (p, *p.parents)), "symlink rejected")
    require(p.is_file() and p.resolve().is_relative_to(root), "artifact missing or outside root")
    require(p.stat().st_size <= MAX_BYTES, "artifact too large")
    data = p.read_bytes()
    require(isinstance(item.get("sha256"), str) and SHA.fullmatch(item["sha256"]),
            "valid claimed artifact SHA256 required")
    actual = sha(data)
    require(actual == item["sha256"], "actual artifact SHA256 mismatch")
    return data.decode("utf-8"), actual

def locate(text, location):
    require(isinstance(location, dict), "location must be object")
    n = location.get("paragraph")
    require(type(n) is int and n > 0, "1-based paragraph required")
    ps = paragraphs(text)
    require(n <= len(ps), "paragraph outside artifact")
    segment = ps[n - 1]
    require(location.get("sha256") == sha(segment.encode("utf-8")),
            "actual paragraph SHA256 mismatch")
    return segment

def evaluate(assertion, text):
    require(isinstance(assertion, dict), "computable assertion required")
    op, value = assertion.get("op"), assertion.get("value")
    require(op in {"contains", "not_contains", "literal_count"}, "unsupported assertion op")
    require(isinstance(value, str) and compact(value), "nonempty assertion value required")
    content, value = compact(text), compact(value)
    count = content.count(value)
    if op == "literal_count":
        expected = assertion.get("count")
        require(type(expected) is int and expected >= 0, "nonnegative literal count required")
        passed = count == expected
    else:
        passed = count > 0 if op == "contains" else count == 0
    return {"op": op, "observed_count": count, "passed": passed}

def frozen_checks(findings, expected):
    if expected is None:
        return
    require(isinstance(expected, list), "expected_findings must be list")
    by_id = {f["id"]: f for f in findings}
    seen = set()
    for old in expected:
        require(isinstance(old, dict), "frozen finding must be object")
        require(isinstance(old.get("location"), dict), "frozen finding location required")
        ident = old.get("id")
        require(isinstance(ident, str) and ident not in seen, "duplicate/invalid frozen id")
        seen.add(ident)
        require(ident in by_id, "frozen finding omitted: " + ident)
        new = by_id[ident]
        for key in ("artifact_id", "kind", "issue", "assertion"):
            require(old.get(key) == new.get(key), "frozen finding changed: " + ident + "." + key)
        require(old.get("location", {}).get("baseline") == new.get("location", {}).get("baseline"),
                "frozen baseline location changed: " + ident)
        require(old.get("severity") in RANK and RANK[new["severity"]] >= RANK[old["severity"]],
                "frozen severity downgraded: " + ident)

def check(record, root=None, expected_findings=None):
    errors, warnings, results, semantic = [], [], [], []
    actual = {}
    try:
        require(isinstance(record, dict) and record.get("schema") == SCHEMA, "invalid schema; v0 cannot close real work")
        require(root is not None, "explicit artifact root required")
        root = Path(root).absolute()
        require(root.is_dir() and not any(x.is_symlink() for x in (root, *root.parents)),
                "artifact root missing or symlinked")
        root = root.resolve()
        artifacts = record.get("artifacts")
        require(isinstance(artifacts, list) and artifacts, "nonempty artifacts required")
        for artifact in artifacts:
            require(isinstance(artifact, dict), "artifact entry must be object")
            ident = artifact.get("artifact_id")
            require(isinstance(ident, str) and ident and ident not in actual, "missing/duplicate artifact id")
            versions, identities = {}, {}
            for version in ("baseline", "candidate"):
                versions[version], identities[version] = read_artifact(root, artifact.get(version))
            actual[ident] = {"text": versions, "sha256": identities}
        coverage = record.get("coverage")
        require(isinstance(coverage, list) and all(isinstance(x, str) for x in coverage)
                and len(coverage) == len(set(coverage)) and set(coverage) == set(actual),
                "coverage must exactly match caller artifact inventory")
        findings = record.get("findings")
        require(isinstance(findings, list) and findings, "empty findings cannot establish actual review; use evidenced KEEP")
        ids, covered = set(), set()
        for f in findings:
            require(isinstance(f, dict), "finding must be object")
            ident, aid = f.get("id"), f.get("artifact_id")
            require(isinstance(ident, str) and ident and ident not in ids, "missing/duplicate finding id")
            ids.add(ident)
            require(aid in actual, "unknown finding artifact")
            covered.add(aid)
            require(f.get("kind") in KINDS and f.get("severity") in RANK and f.get("status") in STATUSES,
                    "invalid finding kind/severity/status")
            require(isinstance(f.get("issue"), str) and f["issue"].strip(), "finding issue required")
            require(isinstance(f.get("evidence"), str) and f["evidence"].strip(), "located review evidence required")
            loc = f.get("location")
            require(isinstance(loc, dict), "baseline/candidate locations required")
            text = actual[aid]["text"]
            before = locate(text["baseline"], loc.get("baseline"))
            after = locate(text["candidate"], loc.get("candidate"))
            status = f["status"]
            row = {"id": ident, "artifact_id": aid, "kind": f["kind"], "status": status,
                   "baseline_paragraph_sha256": sha(before.encode()), "candidate_paragraph_sha256": sha(after.encode())}
            if status == "OPEN":
                if f["severity"] in {"MAJOR", "CRITICAL"}:
                    errors.append(ident + ": unresolved blocking finding")
                else:
                    warnings.append(ident + ": nonblocking finding remains open")
            if status == "KEEP":
                require(isinstance(f.get("reason"), str) and f["reason"].strip(), "KEEP requires reason")
            if status == "CLOSED":
                require(compact(text["baseline"]) != compact(text["candidate"]),
                        "CLOSED requires non-whitespace artifact change")
                require(compact(before) != compact(after), "CLOSED requires relevant paragraph change")
            if f["kind"] == "computable":
                assertion = f.get("assertion")
                old_result = evaluate(assertion, text["baseline"])
                new_result = evaluate(assertion, text["candidate"])
                row["assertion"] = {"baseline": old_result, "candidate": new_result,
                                    "scope": "ENTIRE_ARTIFACT_WHITESPACE_INSENSITIVE"}
                if status == "CLOSED":
                    require(not old_result["passed"] and new_result["passed"],
                            "CLOSED assertion must fail on baseline and pass on actual candidate")
                    value, op = compact(assertion["value"]), assertion["op"]
                    if op == "not_contains":
                        require(value in compact(before), "baseline location does not contain forbidden literal")
                    elif op == "contains":
                        require(value in compact(after), "candidate location does not contain required literal")
                    else:
                        require(compact(before).count(value) != compact(after).count(value),
                                "located literal count did not change")
                elif status == "KEEP":
                    require(old_result["passed"] and new_result["passed"],
                            "KEEP requires actual assertion to pass on both artifacts")
            elif status in {"CLOSED", "KEEP"}:
                review = f.get("review")
                require(isinstance(review, dict), "semantic result requires artifact-bound model review")
                require(review.get("verdict") == status, "model verdict/status mismatch")
                require(isinstance(review.get("reviewer"), str) and review["reviewer"].strip(),
                        "reviewer identity record required")
                require(isinstance(review.get("rationale"), str) and review["rationale"].strip(),
                        "model review rationale required")
                require(review.get("artifact_sha256") == actual[aid]["sha256"]["candidate"]
                        and review.get("location_sha256") == sha(after.encode()),
                        "model review must bind actual candidate and paragraph")
                semantic.append(ident)
            results.append(row)
        require(covered == set(actual), "every artifact needs a located finding or evidenced KEEP")
        frozen_checks(findings, expected_findings)
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as exc:
        errors.append(str(exc))
    return {"status": "HOLD" if errors else "PASS_STRUCTURAL_ONLY",
            "errors": errors, "warnings": warnings,
            "actual_artifacts": {k: v["sha256"] for k, v in actual.items()},
            "findings": results, "model_review_required": semantic,
            "semantic_status": "MODEL_REVIEW_REQUIRED" if semantic else "NOT_CERTIFIED",
            "human_acceptance": "NOT_ESTABLISHED",
            "unreported_defect_discovery": "NOT_ESTABLISHED"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("closeout_json", type=Path)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--expected-findings", type=Path)
    parser.add_argument("--expected-findings-sha256")
    args = parser.parse_args()
    try:
        record = json.loads(args.closeout_json.read_text(encoding="utf-8"))
        expected = None
        if args.expected_findings:
            data = args.expected_findings.read_bytes()
            require(args.expected_findings_sha256 == sha(data), "external frozen findings SHA256 required and must match")
            expected = json.loads(data)
        result = check(record, args.root, expected)
    except (ValueError, OSError, UnicodeError) as exc:
        result = {"status": "HOLD", "errors": [str(exc)], "warnings": []}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS_STRUCTURAL_ONLY" else 2

if __name__ == "__main__":
    raise SystemExit(main())
