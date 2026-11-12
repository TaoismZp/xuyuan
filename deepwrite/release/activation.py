#!/usr/bin/env python3
"""Resolve the active DeepWrite implementation from repository files, not chat memory.

This tool never writes project manuscripts, CURRENT.json or secrets. It does not
silently opt existing projects into a new engine version. With --run, forwards
explicit args only to a pin-verified active runner, not to an experimental branch.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def safe_relative(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith(("/", "~")):
        raise ValueError("UNSAFE_RELATIVE_PATH")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("RELEASE_FILE_MISSING_OR_OUTSIDE_REPO")
    return path


def read_current(root: Path) -> dict:
    p = safe_relative(root, "deepwrite/CURRENT.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("schema") != "deepwrite/current/v1":
        raise ValueError("UNKNOWN_CURRENT_SCHEMA")
    return data


def resolve(root: Path, project_state: Path | None = None) -> dict:
    root = root.resolve()
    active = read_current(root)
    spec = safe_relative(root, active["active_workbench_spec"])
    wish = json.loads(safe_relative(root, "wish-delivery/CURRENT.json").read_text("utf-8"))
    selected = active["active_workbench_version"]
    output = {
        "schema": "deepwrite/activated-resolution/v1",
        "active_version": selected,
        "active_spec": active["active_workbench_spec"],
        "active_spec_sha256": sha256(spec.read_bytes()),
        "parent_wish_version": wish.get("active_version"),
        "status": "WORKBENCH_ONLY_NO_LIVE_AUTONOMOUS_RUNNER",
        "runner": None,
        "project_pin_policy": "NEW_PROJECT_USES_ACTIVE_EXISTING_PROJECT_PIN_PRESERVED",
        "project_alignment": "NEW_PROJECT",
    }
    if project_state is not None:
        project = json.loads(project_state.read_text("utf-8"))
        pin = project.get("resolved_deepwrite_version") or project.get("deepwrite_version")
        if not pin:
            raise ValueError("EXISTING_PROJECT_REQUIRES_EXPLICIT_VERSION_PIN")
        output["project_alignment"] = "MATCH" if pin == selected else "PINNED_DIFFERENT_VERSION_REQUIRES_MIGRATION"
        output["project_pinned_version"] = pin
    runner = active.get("active_runner")
    if runner is None:
        if active.get("capability_status", {}).get("automatic_full_book_generation") not in ("NOT_IMPLEMENTED", "NOT_VERIFIED"):
            raise ValueError("CURRENT_RUNNER_STATUS_CONTRADICTION")
        return output
    if not isinstance(runner, dict):
        raise ValueError("RUNNER_METADATA_INVALID")
    path = safe_relative(root, runner.get("path"))
    pinned = runner.get("sha256")
    if not isinstance(pinned, str) or sha256(path.read_bytes()) != pinned:
        raise ValueError("ACTIVE_RUNNER_BYTES_MISMATCH")
    if runner.get("release_channel") != "STABLE":
        raise ValueError("ACTIVE_RUNNER_MUST_BE_STABLE")
    # Final authority comes only from a merged release record, not an arbitrary
    # candidate module or model-supplied "approved" prose.
    record_path = safe_relative(root, runner.get("release_record"))
    record = json.loads(record_path.read_text("utf-8"))
    if (record.get("status") != "ACTIVE_RELEASE" or
        record.get("version") != selected or
        record.get("runner_sha256") != pinned):
        raise ValueError("ACTIVE_RELEASE_RECORD_MISMATCH")
    output["runner"] = runner["path"]
    output["runner_sha256"] = pinned
    output["status"] = "ACTIVE_RUNNER_BYTES_VERIFIED_CONTENT_QUALITY_NOT_IMPLIED"
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--project-state", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("runner_args", nargs="*")
    args = parser.parse_args()
    try:
        data = resolve(args.root, args.project_state)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        if not args.run:
            return 0
        if data["status"] != "ACTIVE_RUNNER_BYTES_VERIFIED_CONTENT_QUALITY_NOT_IMPLIED":
            raise ValueError("NO_VERIFIED_ACTIVE_RUNNER_NOT_CALLING_EXPERIMENT")
        if data["project_alignment"] == "PINNED_DIFFERENT_VERSION_REQUIRES_MIGRATION":
            raise ValueError("EXISTING_PROJECT_PIN_CONFLICT")
        runner = safe_relative(args.root.resolve(), data["runner"])
        return subprocess.run([sys.executable, str(runner), *args.runner_args], check=False).returncode
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("DEEPWRITE_ACTIVATION_BLOCKED: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
