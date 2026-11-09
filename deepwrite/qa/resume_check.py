#!/usr/bin/env python3
"""Opt-in read-only checks against independently frozen project requirements.

Does not restore, grant authority, resolve Git objects, or certify completeness,
transaction consistency, durable storage, or book quality. Unknown/missing policy
is BLOCKED, never an implicit project PASS. checkpoint.py stays byte-only.
"""
import argparse
import json
from pathlib import Path
import sys

from checkpoint import (HEX40, HEX64, digest, json_object, no_symlinks,
                        relative_path, require, verified_contents)

PASS = "PASS_DECLARED_RESUME_CHECKS_ONLY"


def candidate_commits(value, label):
    require(isinstance(value, dict), label + " must be an object")
    for name, commit in value.items():
        require(isinstance(name, str) and bool(name.strip()), label + " invalid module id")
        require(isinstance(commit, str) and HEX40.fullmatch(commit), label + " needs 40-hex module commit")
    return value


def check(checkpoint, expected_manifest_sha256, requirements_path, expected_requirements_sha256):
    result = {"status": "BLOCKED", "byte_gate": "NOT_RUN", "resume_gate": "BLOCKED",
              "manifest_sha256": expected_manifest_sha256,
              "requirements_sha256": expected_requirements_sha256,
              "complete_project_recovery": "UNVERIFIED", "author_authorization_verified": False,
              "transaction_consistency": "UNVERIFIED", "durable_storage": "UNVERIFIED",
              "content_quality": "UNVERIFIED", "issues": []}
    try:
        require(isinstance(expected_requirements_sha256, str) and
                HEX64.fullmatch(expected_requirements_sha256), "external requirements SHA256 required")
        data = no_symlinks(requirements_path).read_bytes()
        require(digest(data) == expected_requirements_sha256, "requirements SHA256 mismatch")
        policy = json_object(data, "requirements")
        manifest, contents = verified_contents(checkpoint, expected_manifest_sha256)
        result["byte_gate"] = "PASS_BYTES_ONLY"
        require(policy.get("project_id") == manifest["project_id"], "requirements project_id mismatch")
        required = policy.get("required_files")
        require(isinstance(required, list) and bool(required), "required_files must be a nonempty list")
        for name in required:
            relative_path(name)
        require(len(set(required)) == len(required), "duplicate required file")
        missing = sorted(set(required) - set(contents))
        require(not missing, "required files absent: " + ", ".join(missing))
        roles = {r["role"]: r["path"] for r in manifest["files"] if r["role"] != "file"}
        require(set(roles.values()) <= set(required), "requirements must include artifact, pins and config")
        pins = json_object(contents[roles["pins"]], "pins")
        config = json_object(contents[roles["config"]], "config")
        require(isinstance(policy.get("protocols"), dict) and
                pins["protocols"] == policy["protocols"], "protocol pins differ from frozen requirements")
        channel = policy.get("channel")
        require(channel in ("STABLE", "SHADOW", "CANDIDATE_OPT_IN"), "unsupported resume channel")
        require(pins.get("channel") == config.get("channel") == channel,
                "pins/config channel differs from frozen requirements")
        module_policy = policy.get("module_policy")
        require(isinstance(module_policy, dict) and
                all(isinstance(k, str) and bool(k.strip()) and v in ("STABLE", "CANDIDATE")
                    for k, v in module_policy.items()), "module_policy must classify declared module IDs")
        switches = config.get("modules")
        require(isinstance(switches, dict) and all(type(v) is bool for v in switches.values()),
                "config.modules must map IDs to booleans")
        require(set(switches) <= set(module_policy), "config has unclassified modules")
        enabled = {k for k, v in switches.items() if v and module_policy[k] == "CANDIDATE"}
        expected = candidate_commits(policy.get("enabled_candidate_commits"), "requirements candidates")
        require(set(expected) <= set(module_policy) and
                all(module_policy[k] == "CANDIDATE" for k in expected),
                "expected candidate IDs must be classified CANDIDATE")
        require(channel != "STABLE" or not (enabled or expected),
                "STABLE channel cannot enable declared candidate modules")
        require(enabled == set(expected), "enabled candidate IDs differ from frozen requirements")
        rows = pins.get("modules")
        require(isinstance(rows, list), "pins.modules must list candidate IDs and commits")
        pinned = {}
        for row in rows:
            require(isinstance(row, dict) and set(row) == {"id", "commit"},
                    "pins.modules entries require id and commit")
            name = row["id"]
            require(isinstance(name, str) and name not in pinned, "invalid/duplicate pinned module")
            pinned[name] = row["commit"]
        candidate_commits(pinned, "pins candidates")
        configured = candidate_commits(config.get("module_commits", {}), "config candidates")
        require(pinned == configured == expected,
                "candidate commits differ across pins/config/frozen requirements")
        result.update(status=PASS, resume_gate=PASS, project_id=manifest["project_id"],
                      required_files_checked=len(required), protocol_pin_values_match=True,
                      candidate_pin_config_values_match=True)
    except (OSError, ValueError) as exc:
        result["issues"].append(str(exc))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--expected-requirements-sha256", required=True)
    args = parser.parse_args(argv)
    result = check(args.checkpoint, args.expected_manifest_sha256, args.requirements,
                   args.expected_requirements_sha256)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
