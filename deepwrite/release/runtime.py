#!/usr/bin/env python3
"""Released engineering entry: pinned projects, actual-file closeout and recovery.

This entry does not silently run candidate research/writing prompts. Generative
book production is still an explicit experiment until its separate acceptance.
All project output belongs outside this public code checkout.
"""
from __future__ import annotations
import argparse
import contextlib
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    # Execute exactly the source bytes covered by the release inventory. A
    # timestamp-valid __pycache__ must not substitute an unrecorded code object.
    exec(compile(Path(path).read_bytes(), str(path), "exec"), value.__dict__)
    return value


activation = module("deepwrite_runtime_activation", REPO / "deepwrite/release/activation.py")
checkpoint = module("deepwrite_runtime_checkpoint", REPO / "deepwrite/qa/checkpoint.py")
packager = module("deepwrite_runtime_packager", REPO / "deepwrite/tools/book_packager_v0.1.py")
closeout = module("deepwrite_runtime_closeout", REPO / "deepwrite/candidates/e15-review-closure/review_closure_guard.py")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def private_path(path):
    path = Path(path).absolute()
    checkpoint.no_symlinks(path)
    path = path.resolve()
    if path.is_relative_to(REPO.resolve()):
        raise ValueError("PROJECT_MUST_BE_OUTSIDE_PUBLIC_CODE_REPOSITORY")
    return path


def path_in(root, relative):
    path = checkpoint.no_symlinks(root / checkpoint.relative_path(relative))
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("PROJECT_PATH_ESCAPE")
    return path


def identity():
    result = activation.resolve(REPO)
    if result["status"] != "ACTIVE_ENGINE_IDENTITY_VERIFIED_QUALITY_NOT_IMPLIED":
        raise ValueError("NO_RELEASED_ENGINE_NOT_RUNNING_CANDIDATE")
    return result


def atomic_json(path, value):
    temp = path.with_name(path.name + ".tmp")
    with temp.open("xb") as stream:
        stream.write(encoded(value)); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp, path)


def initialize(config_path, destination):
    resolved = identity()
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text("utf-8"))
    project_id = config.get("project_id", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", project_id):
        raise ValueError("EXPLICIT_SAFE_PROJECT_ID_REQUIRED")
    if not isinstance(config.get("wish"), str) or not config["wish"].strip():
        raise ValueError("AUTHOR_WISH_REQUIRED")
    if config.get("guard", "on") != "on":
        raise ValueError("MANDATORY_CLOSEOUT_CANNOT_BE_DISABLED")
    if config.get("channel", "STABLE") != "STABLE" or any(config.get("modules", {}).values()):
        raise ValueError("UNACCEPTED_MODULES_REQUIRE_SEPARATE_EXPERIMENTAL_PROJECT")
    destination = private_path(destination)
    lock = resolved["project_lock"]
    def write(stage):
        frozen = {}
        def save(name, raw):
            target = stage / name; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw); frozen[name] = digest(raw)
        save("PROJECT_LOCK.json", encoded(lock))
        save("config.json", encoded(config))
        pins = {"project_id": project_id,
                "protocols": {"deepwrite": {"version": resolved["active_version"],
                    "commit": lock["activation_commit"], "spec_sha": lock["activation_commit"]},
                    "wish_delivery": {"version": resolved["parent_wish_version"],
                    "commit": lock["activation_commit"], "spec_sha": lock["activation_commit"]}},
                "channel": "STABLE", "modules": []}
        # The byte checkpoint API requires Git SHA syntax. Resolve actual spec
        # blob identities rather than using a convenient placeholder SHA.
        import subprocess
        for key, spec in (("deepwrite", resolved["active_spec"]),
                          ("wish_delivery", json.loads((REPO/"wish-delivery/CURRENT.json").read_text())["active_spec"])):
            pins["protocols"][key]["spec_sha"] = subprocess.check_output(
                ["git", "-C", str(REPO), "rev-parse", "HEAD:" + spec], text=True).strip()
        save("pins.json", encoded(pins))
        for number, source in enumerate(config.get("sources", []), 1):
            source_path = checkpoint.no_symlinks(config_path.parent / checkpoint.relative_path(source["path"]))
            raw = source_path.read_bytes()
            if digest(raw) != source["sha256"]:
                raise ValueError("SOURCE_BYTES_MISMATCH")
            save("sources/" + str(number).zfill(4) + ".md", raw)
        state = {"schema": "deepwrite/engineering-project/v1", "project_id": project_id,
                 "phase": "INITIALIZED", "files": frozen, "events": 0,
                 "mandatory_gates": ["e15_actual_file_closeout"],
                 "automatic_book_generation": "EXPERIMENTAL_NOT_ACTIVATED",
                 "human_acceptance": "NOT_RUN"}
        (stage/"STATE.json").write_bytes(encoded(state))
    checkpoint.publish_directory(destination, write)
    return {"status": "PROJECT_INITIALIZED_WITH_RELEASED_ENGINE",
            "project": str(destination), "identity": lock,
            "state_sha256": digest((destination/"STATE.json").read_bytes()),
            "automatic_book_generation": "EXPERIMENTAL_NOT_ACTIVATED"}


@contextlib.contextmanager
def project(destination, expected_state_sha):
    root = private_path(destination)
    with (root/".engine.lock").open("a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        raw = (root/"STATE.json").read_bytes()
        if digest(raw) != expected_state_sha:
            raise ValueError("EXTERNAL_PROJECT_STATE_SHA_MISMATCH")
        state = json.loads(raw)
        for relative, expected in state["files"].items():
            if digest(path_in(root, relative).read_bytes()) != expected:
                raise ValueError("PROJECT_FILE_BYTES_MISMATCH_" + relative)
        resolved = activation.resolve(REPO, root/"PROJECT_LOCK.json")
        if resolved["project_alignment"] != "MATCH":
            raise ValueError("PROJECT_PINNED_TO_DIFFERENT_ENGINE_CHECK_OUT_ITS_ACTIVATION_COMMIT")
        yield root, state


def assemble(destination, expected_state_sha, manifest_path, review_path, frozen_path, frozen_sha):
    identity()
    with project(destination, expected_state_sha) as (root, state):
        manifest_file, review_file, frozen_file = [path_in(root, p) for p in (manifest_path, review_path, frozen_path)]
        if digest(frozen_file.read_bytes()) != frozen_sha:
            raise ValueError("EXTERNAL_FROZEN_FINDINGS_SHA_MISMATCH")
        manifest, record, frozen = [json.loads(p.read_text("utf-8")) for p in (manifest_file, review_file, frozen_file)]
        source_names = [row["relative_path"] for row in
                        [manifest["front"], *manifest["chapters"], manifest["tail"]]]
        candidates = [row["candidate"]["path"] for row in record.get("artifacts", [])]
        if len(candidates) != len(set(candidates)) or set(candidates) != set(source_names):
            raise ValueError("CLOSEOUT_MUST_COVER_EVERY_PACKAGED_ARTIFACT")
        result = closeout.check(record, root, expected_findings=frozen)
        if result["status"] != "PASS_STRUCTURAL_ONLY":
            return {"status": "HOLD", "gate": result, "state_sha256": expected_state_sha}
        number = state["events"] + 1
        output = path_in(root, "derived/book-" + str(number).zfill(4) + ".md")
        report = output.with_suffix(".json")
        if output.exists() or report.exists():
            raise ValueError("DERIVATIVE_ALREADY_EXISTS_PRESERVE_OLD_ARTIFACT")
        output.parent.mkdir(exist_ok=True)
        packager.assemble(manifest, root, output, report, manifest_file)
        for file in [manifest_file, review_file, frozen_file, output, report,
                     *[path_in(root, name) for name in source_names]]:
            state["files"][file.relative_to(root).as_posix()] = digest(file.read_bytes())
        state.update(phase="ASSEMBLED_PENDING_HUMAN", events=number)
        atomic_json(root/"STATE.json", state)
        return {"status": "ASSEMBLED_PENDING_HUMAN", "artifact": str(output),
                "artifact_sha256": digest(output.read_bytes()), "gate": result,
                "state_sha256": digest((root/"STATE.json").read_bytes()),
                "literary_quality": "NOT_CERTIFIED"}


def snapshot(destination, expected_state_sha, output):
    identity()
    with project(destination, expected_state_sha) as (root, state):
        result = checkpoint.snapshot(root, private_path(output), state["project_id"],
            "STATE.json", "pins.json", "config.json",
            sorted(p for p in state["files"] if p not in ("pins.json", "config.json")))
        return {**result, "state_sha256": expected_state_sha,
                "project_lock_sha256": state["files"]["PROJECT_LOCK.json"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest="command", required=True)
    commands.add_parser("identity")
    new = commands.add_parser("init"); new.add_argument("config", type=Path); new.add_argument("destination", type=Path)
    resume = commands.add_parser("resume"); resume.add_argument("project", type=Path); resume.add_argument("--state-sha256", required=True)
    build = commands.add_parser("assemble"); build.add_argument("project", type=Path)
    for flag in ("state-sha256", "manifest", "review", "frozen-findings", "frozen-sha256"):
        build.add_argument("--" + flag, required=True)
    snap = commands.add_parser("checkpoint"); snap.add_argument("project", type=Path); snap.add_argument("destination", type=Path); snap.add_argument("--state-sha256", required=True)
    restore = commands.add_parser("restore"); restore.add_argument("checkpoint", type=Path); restore.add_argument("destination", type=Path); restore.add_argument("--manifest-sha256", required=True)
    args = p.parse_args()
    try:
        if args.command == "identity": result = identity()
        elif args.command == "init": result = initialize(args.config, args.destination)
        elif args.command == "resume":
            identity()
            with project(args.project, args.state_sha256) as (_, state):
                result = {"status": "PROJECT_LOCK_AND_DECLARED_FILES_VERIFIED", "phase": state["phase"], "state_sha256": args.state_sha256}
        elif args.command == "assemble": result = assemble(args.project, args.state_sha256, args.manifest, args.review, args.frozen_findings, args.frozen_sha256)
        elif args.command == "checkpoint": result = snapshot(args.project, args.state_sha256, args.destination)
        else:
            identity()
            result = checkpoint.restore(args.checkpoint, private_path(args.destination), args.manifest_sha256)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result["status"] in ("HOLD", "BLOCKED") else 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
