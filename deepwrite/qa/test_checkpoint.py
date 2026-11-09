import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from checkpoint import RECEIPT, publish_directory, restore, snapshot, verify


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        self.pins = {"schema": "deepwrite/project-pins/v0.1", "project_id": "public-fixture",
                     "protocols": {name: {"version": version, "commit": "c" * 40, "spec_sha": "d" * 40}
                                   for name, version in (("deepwrite", "v0.1"), ("wish_delivery", "v7.6"))},
                     "modules": [], "channel": "STABLE"}
        self.originals = {"book.md": "合成公开小稿：保留条件与反例。\n".encode(),
                          "pins.json": json.dumps(self.pins).encode(),
                          "config.json": b'{"discovery_gate": false}\n',
                          "notes/source.txt": b"public fixture only\n"}
        for name, data in self.originals.items():
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        self.checkpoint = self.base / "checkpoint"
        self.destination = self.base / "restored"

    def save(self, **kwargs):
        options = {"project_id": "public-fixture", "artifact": "book.md", "pins": "pins.json",
                   "config": "config.json", "files": ["notes/source.txt"]}
        options.update(kwargs)
        return snapshot(self.root, self.checkpoint, **options)["manifest_sha256"]

    def test_restores_artifact_protocols_and_config_retaining_failed_candidate(self):
        expected = self.save()
        (self.root / "book.md").write_text("failed trial")
        (self.root / "config.json").write_text('{"discovery_gate": true}')
        restore(self.checkpoint, self.destination, expected)
        for name, data in self.originals.items():
            self.assertEqual((self.destination / name).read_bytes(), data)
        self.assertEqual((self.root / "book.md").read_text(), "failed trial")
        self.assertTrue((self.checkpoint / "manifest.json").exists())
        self.assertEqual(json.loads((self.destination / RECEIPT).read_bytes())["manifest_sha256"], expected)

    def test_restores_after_source_deleted(self):
        expected = self.save()
        shutil.rmtree(self.root)
        restore(self.checkpoint, self.destination, expected)
        self.assertEqual((self.destination / "book.md").read_bytes(), self.originals["book.md"])

    def test_tampered_artifact_or_config_blocks_without_destination(self):
        expected = self.save()
        for name in ("book.md", "config.json"):
            with self.subTest(name=name):
                target = self.checkpoint / "files" / name
                old = target.read_bytes()
                target.write_bytes(b"tampered")
                with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                    restore(self.checkpoint, self.destination, expected)
                self.assertFalse(self.destination.exists())
                target.write_bytes(old)

    def test_rewritten_manifest_rejected_even_when_files_match_it(self):
        expected = self.save()
        target = self.checkpoint / "files/book.md"
        target.write_bytes(b"tampered")
        path = self.checkpoint / "manifest.json"
        manifest = json.loads(path.read_bytes())
        manifest["files"][0].update(sha256=hashlib.sha256(b"tampered").hexdigest(), size=8)
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "manifest SHA256 mismatch"):
            restore(self.checkpoint, self.destination, expected)
        self.assertFalse(self.destination.exists())

    def test_missing_object_blocks_without_destination(self):
        expected = self.save()
        (self.checkpoint / "files/pins.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing/non-regular"):
            restore(self.checkpoint, self.destination, expected)
        self.assertFalse(self.destination.exists())

    def test_existing_destination_never_overwritten(self):
        expected = self.save()
        self.destination.mkdir()
        (self.destination / "keep").write_bytes(b"original")
        with self.assertRaisesRegex(ValueError, "already exists"):
            restore(self.checkpoint, self.destination, expected)
        self.assertEqual((self.destination / "keep").read_bytes(), b"original")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.save()
        self.assertEqual(verify(self.checkpoint, expected)["status"], "PASS_BYTES_ONLY")

    def test_concurrent_destination_creation_never_overwritten(self):
        def competing_writer(stage):
            (stage / "data").write_bytes(b"staged content")
            self.destination.mkdir()  # Another actor wins after initial check.
        with self.assertRaises(OSError):
            publish_directory(self.destination, competing_writer)
        self.assertTrue(self.destination.is_dir())
        self.assertEqual(list(self.destination.iterdir()), [])
        self.assertFalse(list(self.base.glob(".deepwrite-checkpoint-*")))

    def test_traversal_absolute_duplicate_and_reserved_paths_rejected(self):
        for name in ("../book.md", "/book.md", "notes/../../book.md", "./book.md", RECEIPT):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.save(artifact=name)
                self.assertFalse(self.checkpoint.exists())
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.save(files=["book.md"])

    def test_source_and_checkpoint_symlinks_rejected(self):
        (self.root / "linked.md").symlink_to(self.root / "book.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.save(artifact="linked.md")
        (self.root / "linked-dir").symlink_to(self.root / "notes", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.save(files=["linked-dir/source.txt"])
        expected = self.save()
        target = self.checkpoint / "files/book.md"
        target.unlink()
        target.symlink_to(self.root / "book.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            restore(self.checkpoint, self.destination, expected)
        self.assertFalse(self.destination.exists())

    def test_unresolved_pins_and_non_object_config_rejected(self):
        for field, value in (("version", "READ_FROM_CURRENT"), ("commit", "main"), ("spec_sha", "PIN_ACTUAL_BLOB_SHA")):
            self.pins["protocols"]["deepwrite"][field] = value
            (self.root / "pins.json").write_text(json.dumps(self.pins))
            with self.assertRaises(ValueError):
                self.save()
            self.assertFalse(self.checkpoint.exists())
            self.pins = json.loads(self.originals["pins.json"])
        (self.root / "pins.json").write_bytes(self.originals["pins.json"])
        (self.root / "config.json").write_bytes(b"[]")
        with self.assertRaisesRegex(ValueError, "JSON object"):
            self.save()
        (self.root / "config.json").write_bytes(b'{"invalid": NaN}')
        with self.assertRaisesRegex(ValueError, "valid JSON"):
            self.save()

    def test_manifest_with_traversal_rejected_even_with_matching_hash(self):
        self.save()
        path = self.checkpoint / "manifest.json"
        manifest = json.loads(path.read_bytes())
        manifest["files"][0]["path"] = "../outside"
        data = json.dumps(manifest).encode()
        path.write_bytes(data)
        with self.assertRaises(ValueError):
            restore(self.checkpoint, self.destination, hashlib.sha256(data).hexdigest())
        self.assertFalse(self.destination.exists())

    def test_cli_requires_external_hash_and_reports_bytes_only(self):
        script = Path(__file__).with_name("checkpoint.py")
        result = subprocess.run([sys.executable, str(script), "snapshot", str(self.root), str(self.checkpoint),
                                 "--project-id", "public-fixture", "--artifact", "book.md", "--pins", "pins.json",
                                 "--config", "config.json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        expected = json.loads(result.stdout)["manifest_sha256"]
        result = subprocess.run([sys.executable, str(script), "verify", str(self.checkpoint),
                                 "--expected-manifest-sha256", expected], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS_BYTES_ONLY")
        result = subprocess.run([sys.executable, str(script), "restore", str(self.checkpoint), str(self.destination),
                                 "--expected-manifest-sha256", "0" * 64], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
