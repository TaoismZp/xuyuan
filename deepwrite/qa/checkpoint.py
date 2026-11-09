#!/usr/bin/env python3
"""Opt-in local byte checkpoints; not quality, durable storage, or identity proof.

The external manifest SHA256 must be saved separately. Pins are syntactically
checked, not checked against GitHub or author authority. No CURRENT is changed.
Only new directories are published; source files and failed trials stay intact.
Atomic no-clobber publication requires Linux renameat2 (or Windows rename).
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone

SCHEMA = "deepwrite/checkpoint/v0.1"
RECEIPT = "RESTORE_RECEIPT.json"
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
BYTE_SCOPE = {"project_resume_gate": "NOT_RUN", "complete_project_recovery": "UNVERIFIED"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid_label(value):
    return (isinstance(value, str) and bool(value.strip()) and
            not any(s in value.upper() for s in
                    ("READ_FROM", "FILL_IN", "PIN_ACTUAL", "REPLACE", "SET_ON", "EXAMPLE_ONLY")))


def relative_path(value):
    require(isinstance(value, str) and bool(value), "empty/non-string file path")
    p = PurePosixPath(value)
    require(not p.is_absolute() and ".." not in p.parts and "\\" not in value and
            ":" not in value and p.as_posix() == value and value != ".",
            "file path must be canonical relative POSIX path: " + value)
    require(p.parts[0] != RECEIPT, "reserved restore receipt path")
    return p


def no_symlinks(path):
    p = Path(path).absolute()
    require(not any(x.is_symlink() for x in (p, *p.parents)), "symlink path rejected")
    return p


def read_file(root, name):
    p = no_symlinks(root / relative_path(name))
    require(p.is_file(), "missing/non-regular file: " + name)
    return p.read_bytes()


def json_object(data, label):
    def invalid_constant(value):
        raise ValueError("non-JSON constant: " + value)
    try:
        value = json.loads(data, parse_constant=invalid_constant)
    except (ValueError, UnicodeError) as exc:
        raise ValueError(label + " must be valid JSON") from exc
    require(isinstance(value, dict), label + " must be a JSON object")
    return value


def validate_pins(data, project_id):
    pins = json_object(data, "pins")
    require(pins.get("project_id") == project_id, "pins project_id mismatch")
    protocols = pins.get("protocols")
    require(isinstance(protocols, dict), "pins.protocols missing")
    for name in ("deepwrite", "wish_delivery"):
        pin = protocols.get(name)
        require(isinstance(pin, dict), "missing protocol: " + name)
        require(valid_label(pin.get("version")), "unresolved protocol version: " + name)
        for field in ("commit", "spec_sha"):
            require(isinstance(pin.get(field), str) and HEX40.fullmatch(pin[field]),
                    "protocol " + name + "." + field + " must be 40-hex")
    return pins


def validate_records(manifest):
    require(manifest.get("schema") == SCHEMA, "checkpoint schema mismatch")
    require(valid_label(manifest.get("project_id")), "invalid project_id")
    records = manifest.get("files")
    require(isinstance(records, list) and bool(records), "missing checkpoint files")
    paths, roles = set(), []
    for record in records:
        require(isinstance(record, dict), "invalid file record")
        name = record.get("path")
        relative_path(name)
        require(name not in paths, "duplicate file path")
        require(not any(name.startswith(p + "/") or p.startswith(name + "/") for p in paths),
                "file/directory path conflict")
        paths.add(name)
        role = record.get("role")
        require(role in ("artifact", "pins", "config", "file"), "invalid file role")
        roles.append(role)
        require(isinstance(record.get("sha256"), str) and HEX64.fullmatch(record["sha256"]),
                "invalid object SHA256")
        require(type(record.get("size")) is int and record["size"] >= 0, "invalid object size")
    require(all(roles.count(role) == 1 for role in ("artifact", "pins", "config")),
            "exactly one artifact, pins, and config required")
    return records


def publish_directory(destination, writer):
    """Stage a complete directory, then atomically publish without replacement."""
    dest = no_symlinks(destination)
    require(dest.parent.is_dir(), "destination parent must exist")
    require(not dest.exists(), "destination already exists")
    stage = Path(tempfile.mkdtemp(prefix=".deepwrite-checkpoint-", dir=dest.parent))
    try:
        writer(stage)
        if sys.platform == "win32":
            os.rename(stage, dest)  # Windows rename refuses existing destinations.
        else:
            libc = ctypes.CDLL(None, use_errno=True)
            rename = getattr(libc, "renameat2", None)
            require(rename is not None, "atomic no-clobber renameat2 unavailable")
            rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
            rename.restype = ctypes.c_int
            if rename(-100, os.fsencode(stage), -100, os.fsencode(dest), 1) != 0:
                err = ctypes.get_errno()
                raise OSError(err, os.strerror(err), str(dest))
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def write_files(root, contents):
    for name, data in contents.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def snapshot(root, destination, project_id, artifact, pins, config, files=()):
    require(valid_label(project_id), "invalid project_id")
    root = no_symlinks(root)
    require(root.is_dir(), "source root must be directory")
    records, contents = [], {}
    for role, name in [("artifact", artifact), ("pins", pins), ("config", config)] + [("file", f) for f in files]:
        data = read_file(root, name)
        records.append({"path": name, "role": role, "sha256": digest(data), "size": len(data)})
        contents["files/" + name] = data
    manifest = {"schema": SCHEMA, "project_id": project_id, "files": records}
    validate_records(manifest)
    validate_pins(contents["files/" + pins], project_id)
    json_object(contents["files/" + config], "config")
    manifest_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    contents["manifest.json"] = manifest_data
    publish_directory(destination, lambda stage: write_files(stage, contents))
    return {**BYTE_SCOPE, "status": "PASS_BYTES_ONLY", "manifest_sha256": digest(manifest_data),
            "project_id": project_id, "files": len(records)}


def verified_contents(checkpoint, expected_manifest_sha256):
    require(isinstance(expected_manifest_sha256, str) and HEX64.fullmatch(expected_manifest_sha256),
            "external expected manifest SHA256 required")
    root = no_symlinks(checkpoint)
    manifest_data = read_file(root, "manifest.json")
    require(digest(manifest_data) == expected_manifest_sha256, "manifest SHA256 mismatch")
    manifest = json_object(manifest_data, "manifest")
    records = validate_records(manifest)
    contents = {}
    for record in records:
        data = read_file(root, "files/" + record["path"])
        require(len(data) == record["size"] and digest(data) == record["sha256"],
                "object size/SHA256 mismatch: " + record["path"])
        contents[record["path"]] = data
    for record in records:
        if record["role"] == "pins":
            validate_pins(contents[record["path"]], manifest["project_id"])
        elif record["role"] == "config":
            json_object(contents[record["path"]], "config")
    return manifest, contents


def verify(checkpoint, expected_manifest_sha256):
    manifest, contents = verified_contents(checkpoint, expected_manifest_sha256)
    return {**BYTE_SCOPE, "status": "PASS_BYTES_ONLY", "project_id": manifest["project_id"], "files": len(contents),
            "manifest_sha256": expected_manifest_sha256}


def restore(checkpoint, destination, expected_manifest_sha256):
    manifest, contents = verified_contents(checkpoint, expected_manifest_sha256)
    receipt = {**BYTE_SCOPE, "schema": "deepwrite/restore-receipt/v0.1", "project_id": manifest["project_id"],
               "manifest_sha256": expected_manifest_sha256,
               "restored_at": datetime.now(timezone.utc).isoformat(),
               "status": "PASS_BYTES_ONLY", "existing_files_overwritten": False}
    contents[RECEIPT] = (json.dumps(receipt, indent=2) + "\n").encode("utf-8")
    publish_directory(destination, lambda stage: write_files(stage, contents))
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    snap = subs.add_parser("snapshot")
    snap.add_argument("root", type=Path)
    snap.add_argument("destination", type=Path)
    for field in ("project-id", "artifact", "pins", "config"):
        snap.add_argument("--" + field, required=True)
    snap.add_argument("--file", action="append", default=[])
    for command in ("verify", "restore"):
        sub = subs.add_parser(command)
        sub.add_argument("checkpoint", type=Path)
        if command == "restore":
            sub.add_argument("destination", type=Path)
        sub.add_argument("--expected-manifest-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            result = snapshot(args.root, args.destination, args.project_id, args.artifact, args.pins, args.config, args.file)
        elif args.command == "verify":
            result = verify(args.checkpoint, args.expected_manifest_sha256)
        else:
            result = restore(args.checkpoint, args.destination, args.expected_manifest_sha256)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
