#!/usr/bin/env python3
"""Resolve the committed DeepWrite release identity; never infer it from chat memory.

The resolver checks declared runtime bytes and Git identity. It does not authenticate
human approval or establish manuscript quality. The repository's protected release
workflow supplies authorization. No project manuscript or CURRENT is written here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

HEX40 = re.compile(r"[a-f0-9]{40}\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
ACTIVE_ENGINE = "ACTIVE_ENGINE_IDENTITY_VERIFIED_QUALITY_NOT_IMPLIED"
ACTIVE_RUNNER = "ACTIVE_RUNNER_BYTES_VERIFIED_CONTENT_QUALITY_NOT_IMPLIED"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_root(root: Path) -> Path:
    root = Path(root).absolute()
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("SYMLINK_REPOSITORY_ROOT")
    return root.resolve()


def safe_relative(root: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or not relative or "\\" in relative or
            relative.startswith(("/", "~")) or
            any(part in ("", ".", "..") for part in relative.split("/")) or
            PurePosixPath(relative).as_posix() != relative):
        raise ValueError("UNSAFE_RELATIVE_PATH")
    root = checked_root(root)
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("SYMLINK_RELEASE_FILE")
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("RELEASE_FILE_MISSING_OR_OUTSIDE_REPO")
    return path


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(root), *args],
                            capture_output=True, timeout=30, check=False)
    if result.returncode:
        raise ValueError("RELEASE_GIT_IDENTITY_UNAVAILABLE")
    return result.stdout


def verify_git_file(root: Path, commit: str, relative: str, actual: bytes) -> None:
    if git(root, "show", commit + ":" + relative) != actual:
        raise ValueError("RELEASE_GIT_FILE_BYTES_MISMATCH:" + relative)


def read_current(root: Path) -> dict:
    data = json.loads(safe_relative(root, "deepwrite/CURRENT.json").read_text(encoding="utf-8"))
    if data.get("schema") != "deepwrite/current/v1":
        raise ValueError("UNKNOWN_CURRENT_SCHEMA")
    return data


def bound_file(root: Path, commit: str, item: dict, label: str) -> tuple[str, str]:
    if not isinstance(item, dict):
        raise ValueError(label + "_IDENTITY_REQUIRED")
    relative, expected = item.get("path"), item.get("sha256")
    path = safe_relative(root, relative)
    actual = path.read_bytes()
    if not isinstance(expected, str) or not HEX64.fullmatch(expected) or sha256(actual) != expected:
        raise ValueError(label + "_BYTES_MISMATCH")
    verify_git_file(root, commit, relative, actual)
    return relative, expected


def module_identities(value: object) -> list:
    if not isinstance(value, list):
        raise ValueError("RELEASE_MODULE_IDENTITIES_REQUIRED")
    seen = set()
    for item in value:
        if (not isinstance(item, dict) or not isinstance(item.get("id"), str) or
                not item["id"] or item["id"] in seen or
                not isinstance(item.get("commit"), str) or not HEX40.fullmatch(item["commit"]) or
                ("sha256" in item and (not isinstance(item["sha256"], str) or
                                      not HEX64.fullmatch(item["sha256"])))):
            raise ValueError("INVALID_RELEASE_MODULE_IDENTITY")
        seen.add(item["id"])
    return sorted(value, key=lambda item: item["id"])


def project_alignment(output: dict, project_state: Path | None, complete: bool, root: Path | None = None) -> None:
    if project_state is None:
        return
    project = json.loads(project_state.read_text("utf-8"))
    lock = project.get("engine_lock", project)
    if not isinstance(lock, dict):
        raise ValueError("EXISTING_PROJECT_REQUIRES_EXPLICIT_VERSION_PIN")
    pin = lock.get("resolved_deepwrite_version") or lock.get("deepwrite_version")
    if not pin:
        raise ValueError("EXISTING_PROJECT_REQUIRES_EXPLICIT_VERSION_PIN")
    output["project_pinned_version"] = pin
    if not complete:
        output["project_alignment"] = ("MATCH" if pin == output["active_version"] else
                                       "PINNED_DIFFERENT_VERSION_REQUIRES_MIGRATION")
        return
    expected = output["project_lock"]
    if any(key not in lock for key in expected):
        raise ValueError("EXISTING_PROJECT_REQUIRES_COMPLETE_ENGINE_LOCK")
    activation_commit = lock["activation_commit"]
    if not isinstance(activation_commit, str) or not HEX40.fullmatch(activation_commit):
        raise ValueError("PROJECT_ACTIVATION_COMMIT_REQUIRED")
    git(root, "merge-base", "--is-ancestor", activation_commit, "HEAD")
    archived_record = git(root, "show", activation_commit + ":" + output["release_record"])
    if sha256(archived_record) != lock["release_record_sha256"]:
        raise ValueError("PROJECT_ACTIVATION_RECORD_MISMATCH")
    archived_current = json.loads(git(root, "show", activation_commit + ":deepwrite/CURRENT.json"))
    archived_engine = archived_current.get("active_engine") or archived_current.get("active_runner") or {}
    if (archived_current.get("active_workbench_version") != lock["resolved_deepwrite_version"] or
            archived_engine.get("implementation_commit") != lock["implementation_commit"] or
            archived_engine.get("release_record_sha256") != lock["release_record_sha256"]):
        raise ValueError("PROJECT_ACTIVATION_POINTER_MISMATCH")
    mismatches = [key for key, value in expected.items()
                  if key != "activation_commit" and lock[key] != value]
    output["project_alignment"] = ("PINNED_DIFFERENT_ENGINE_REQUIRES_MIGRATION" if mismatches else "MATCH")
    output["project_identity_mismatches"] = mismatches


def resolve(root: Path, project_state: Path | None = None) -> dict:
    root = checked_root(root)
    active = read_current(root)
    spec = safe_relative(root, active["active_workbench_spec"])
    wish_path = safe_relative(root, "wish-delivery/CURRENT.json")
    wish = json.loads(wish_path.read_text("utf-8"))
    selected = active["active_workbench_version"]
    output = {
        "schema": "deepwrite/activated-resolution/v1", "active_version": selected,
        "active_spec": active["active_workbench_spec"],
        "active_spec_sha256": sha256(spec.read_bytes()),
        "parent_wish_version": wish.get("active_version"),
        "status": "WORKBENCH_ONLY_NO_LIVE_AUTONOMOUS_RUNNER", "runner": None,
        "project_pin_policy": "NEW_PROJECT_USES_ACTIVE_EXISTING_PROJECT_PIN_PRESERVED",
        "project_alignment": "NEW_PROJECT", "human_approval_verified_by_resolver": False,
        "book_quality_verified_by_resolver": False,
    }
    engine = active.get("active_engine")
    legacy = engine is None
    if legacy:
        engine = active.get("active_runner")
    if engine is None:
        if active.get("capability_status", {}).get("automatic_full_book_generation") not in ("NOT_IMPLEMENTED", "NOT_VERIFIED"):
            raise ValueError("CURRENT_RUNNER_STATUS_CONTRADICTION")
        project_alignment(output, project_state, complete=False)
        return output
    if not isinstance(engine, dict):
        raise ValueError("RUNNER_METADATA_INVALID")
    if not legacy and active.get("active_runner") is not None:
        raise ValueError("AMBIGUOUS_ACTIVE_ENTRYPOINT")
    path = safe_relative(root, engine.get("path"))
    pinned = engine.get("sha256")
    if not isinstance(pinned, str) or not HEX64.fullmatch(pinned) or sha256(path.read_bytes()) != pinned:
        raise ValueError("ACTIVE_RUNNER_BYTES_MISMATCH")
    if engine.get("release_channel") != "STABLE":
        raise ValueError("ACTIVE_RUNNER_MUST_BE_STABLE")
    record_path = safe_relative(root, engine.get("release_record"))
    raw_record = record_path.read_bytes()
    record = json.loads(raw_record)
    version = engine.get("version", selected if legacy else None)
    if (record.get("status") != "ACTIVE_RELEASE" or record.get("version") != version or
            (legacy and record.get("runner_sha256", pinned) != pinned)):
        raise ValueError("ACTIVE_RELEASE_RECORD_MISMATCH")
    if record.get("schema") != "deepwrite/release-record/v1":
        raise ValueError("ACTIVE_RELEASE_RECORD_IDENTITY_SCHEMA_REQUIRED")
    record_sha = sha256(raw_record)
    if engine.get("release_record_sha256") != record_sha:
        raise ValueError("ACTIVE_RELEASE_RECORD_BYTES_MISMATCH")
    commit = engine.get("implementation_commit")
    if (not isinstance(commit, str) or not HEX40.fullmatch(commit) or
            record.get("implementation_commit") != commit):
        raise ValueError("IMPLEMENTATION_COMMIT_REQUIRED_OR_MISMATCH")
    if git(root, "rev-parse", "--show-toplevel").decode().strip() != str(root):
        raise ValueError("RELEASE_REQUIRES_REPOSITORY_ROOT")
    if git(root, "cat-file", "-t", commit).strip() != b"commit":
        raise ValueError("IMPLEMENTATION_OBJECT_NOT_COMMIT")
    git(root, "merge-base", "--is-ancestor", commit, "HEAD")
    verify_git_file(root, "HEAD", "deepwrite/CURRENT.json", (root / "deepwrite/CURRENT.json").read_bytes())
    verify_git_file(root, "HEAD", engine["release_record"], raw_record)
    if record.get("workbench_version") != selected:
        raise ValueError("WORKBENCH_RELEASE_VERSION_MISMATCH")
    declared_spec = record.get("spec")
    if not isinstance(declared_spec, dict) or declared_spec.get("path") != active["active_workbench_spec"]:
        raise ValueError("ACTIVE_SPEC_RELEASE_BINDING_MISMATCH")
    bound_file(root, commit, declared_spec, "ACTIVE_SPEC")
    parent = record.get("parent")
    if (not isinstance(parent, dict) or parent.get("version") != wish.get("active_version") or
            parent.get("current_sha256") != sha256(wish_path.read_bytes())):
        raise ValueError("PARENT_RELEASE_BINDING_MISMATCH")
    verify_git_file(root, commit, "wish-delivery/CURRENT.json", wish_path.read_bytes())
    parent_spec = parent.get("spec")
    if not isinstance(parent_spec, dict) or parent_spec.get("path") != wish.get("active_spec"):
        raise ValueError("PARENT_SPEC_RELEASE_BINDING_MISMATCH")
    _, parent_spec_sha = bound_file(root, commit, parent_spec, "PARENT_SPEC")
    rows = record.get("runtime_files")
    if not isinstance(rows, list) or not rows:
        raise ValueError("RUNTIME_FILE_INVENTORY_REQUIRED")
    inventory = {}
    for row in rows:
        relative, actual_sha = bound_file(root, commit, row, "RUNTIME_FILE")
        if relative in inventory:
            raise ValueError("DUPLICATE_RUNTIME_FILE")
        inventory[relative] = actual_sha
    if inventory.get(engine["path"]) != pinned:
        raise ValueError("ENTRYPOINT_NOT_IN_RUNTIME_INVENTORY")
    modules = module_identities(record.get("module_identities"))
    lock = {"schema": "deepwrite/project-engine-lock/v1", "resolved_deepwrite_version": selected,
            "engine_version": version, "implementation_commit": commit,
            "release_record_sha256": record_sha, "activation_commit": git(root, "rev-parse", "HEAD").decode().strip(),
            "parent": {"version": parent["version"], "current_sha256": parent["current_sha256"],
                       "spec_sha256": parent_spec_sha}, "module_identities": modules}
    output.update(runner=engine["path"], runner_sha256=pinned, engine_version=version,
                  implementation_commit=commit, release_record=engine["release_record"],
                  release_record_sha256=record_sha, runtime_files=inventory, project_lock=lock,
                  module_identities=modules, status=ACTIVE_RUNNER if legacy else ACTIVE_ENGINE,
                  runtime_inventory_scope="DECLARED_FILES_NOT_AUTOMATIC_DEPENDENCY_DISCOVERY")
    project_alignment(output, project_state, complete=True, root=root)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--project-state", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("runner_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        data = resolve(args.root, args.project_state)
        print(json.dumps(data, ensure_ascii=False, indent=2), flush=True)
        if not args.run:
            return 0
        if data["status"] not in (ACTIVE_ENGINE, ACTIVE_RUNNER):
            raise ValueError("NO_VERIFIED_ACTIVE_RUNNER_NOT_CALLING_EXPERIMENT")
        if data["project_alignment"] not in ("NEW_PROJECT", "MATCH"):
            raise ValueError("EXISTING_PROJECT_PIN_CONFLICT")
        runner = safe_relative(args.root, data["runner"])
        runner_args = args.runner_args[1:] if args.runner_args[:1] == ["--"] else args.runner_args
        return subprocess.run([sys.executable, str(runner), *runner_args], check=False).returncode
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print("DEEPWRITE_ACTIVATION_BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
