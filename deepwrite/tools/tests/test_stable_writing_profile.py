#!/usr/bin/env python3
"""Temporary-Git STABLE selection is engineering evidence, never a real release.

Uses the existing scripted transport; no provider, author approval or reader
acceptance is manufactured, and the real checkout's CURRENT is never written.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]
RUNTIME = [
    "deepwrite/tools/writing_loop_experimental.py",
    "deepwrite/tools/model_adapter_openai_responses_experimental_v0_1.py",
    "deepwrite/tools/book_packager_v0.1.py",
    "deepwrite/qa/checkpoint.py",
    "deepwrite/qa/resume_check.py",
    "deepwrite/candidates/e15-review-closure/review_closure_guard.py",
    "deepwrite/candidates/e23-frame-wiring/reader_source_gate.py",
    "deepwrite/candidates/RESEARCH_LOOP.md",
    "deepwrite/candidates/EDITORIAL_LOOP.md",
    "deepwrite/release/activation.py",
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class StableWritingProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="deepwrite-stable-profile-fixture-")
        self.base = Path(self.temp.name)
        self.code = self.base / "code"
        self.code.mkdir()
        self.git("init", "-q", "--initial-branch=main")
        self.git("config", "user.name", "Engineering fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        active_spec = json.loads((REPO / "deepwrite/CURRENT.json").read_text())["active_workbench_spec"]
        for relative in RUNTIME + [
            "deepwrite/CURRENT.json", "wish-delivery/CURRENT.json",
            active_spec, "wish-delivery/versions/v7.6.md",
            "deepwrite/tools/tests/test_writing_loop_experimental.py",
        ]:
            target = self.code / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, target)
        # The real checkout currently has no active engine. This committed
        # temporary fixture installs only its own explicit WRITING profile.
        self.impl = self.commit("Fixture source only; not GitHub publication")
        current = json.loads((self.code / "deepwrite/CURRENT.json").read_text())
        parent = json.loads((self.code / "wish-delivery/CURRENT.json").read_text())
        record = {
            "schema": "deepwrite/release-record/v1", "status": "ACTIVE_RELEASE",
            "version": "fixture-writing-1", "workbench_version": current["active_workbench_version"],
            "implementation_commit": self.impl,
            "runtime_files": [self.item(p) for p in RUNTIME],
            "spec": self.item(current["active_workbench_spec"]),
            "parent": {"version": "v7.6", "current_sha256": sha((self.code / "wish-delivery/CURRENT.json").read_bytes()),
                       "spec": self.item(parent["active_spec"])},
            "module_identities": [{"id": "e18_loop", "commit": self.impl}],
            "execution_profile": {"kind": "WRITING", "mandatory_gates": [
                "AUTHOR_PROJECT_MODE", "READER_SOURCE_TRANSFER", "ACTUAL_FILE_CLOSEOUT", "BOOKWIDE_RECHECK"]},
            "evidence_scope": "ENGINEERING_FIXTURE_NOT_GITHUB_RELEASE_OR_HUMAN_ACCEPTANCE",
        }
        record_path = "deepwrite/releases/fixture-writing-1.json"
        self.write_json(record_path, record)
        current["active_engine"] = {
            "version": record["version"], "implementation_commit": self.impl,
            "path": RUNTIME[0], "sha256": self.item(RUNTIME[0])["sha256"],
            "release_channel": "STABLE", "release_record": record_path,
            "release_record_sha256": self.item(record_path)["sha256"],
        }
        self.write_json("deepwrite/CURRENT.json", current)
        self.activation = self.commit("Temporary fixture activation; no real authorization claim")
        path = self.code / "deepwrite/tools/tests/test_writing_loop_experimental.py"
        name = "stable_profile_fixture_" + self.activation[:12]
        spec = importlib.util.spec_from_file_location(name, path)
        self.fixture = importlib.util.module_from_spec(spec)
        sys.modules[name] = self.fixture
        spec.loader.exec_module(self.fixture)
        self.project = self.base / "project"
        self.cfg = self.fixture.config(self.project)
        self.cfg["channel"] = self.cfg["pins"]["channel"] = "STABLE"
        # These containers list candidates only. Stable engine identity comes
        # from the real temporary record and module receipt, not a fake pin.
        self.cfg["module_policy"] = {"e18_loop": "STABLE"}
        self.cfg["pins"]["modules"] = []
        self.cfg["module_commits"] = {}
        self.cfg["pins"]["protocols"]["deepwrite"]["version"] = current["active_workbench_version"]
        for name, path in (("deepwrite", current["active_workbench_spec"]),
                           ("wish_delivery", parent["active_spec"])):
            self.cfg["pins"]["protocols"][name]["commit"] = self.impl
            self.cfg["pins"]["protocols"][name]["spec_sha"] = self.git("rev-parse", self.impl + ":" + path)

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", "--no-replace-objects", "-C", str(self.code), *args],
                                       stderr=subprocess.DEVNULL, text=True).strip()

    def commit(self, message):
        self.git("add", "."); self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def item(self, path):
        return {"path": path, "sha256": sha((self.code / path).read_bytes())}

    def write_json(self, relative, value):
        path = self.code / relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def test_committed_selected_writer_runs_real_repair_checkpoint_and_resume(self):
        dispatch = subprocess.run([sys.executable, "-B", str(self.code / "deepwrite/release/activation.py"),
            "--root", str(self.code), "--run", "--", "--help"], capture_output=True, text=True)
        self.assertEqual(dispatch.returncode, 0, dispatch.stderr)
        self.assertIn("ACTIVE_ENGINE_IDENTITY_VERIFIED_QUALITY_NOT_IMPLIED", dispatch.stdout)
        self.assertIn("--author-approval-receipt", dispatch.stdout)
        model = self.fixture.ScriptedModel()
        loop = self.fixture.loop
        result = loop.WritingLoop(self.project, self.cfg, model=model).run()
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertIn("source_learning", model.calls)
        self.assertIn("source_evidence_review", model.calls)
        self.assertIn("revise", model.calls)
        self.assertIn("recheck", model.calls)
        self.assertTrue(list((self.project / "diffs").glob("*.patch")))
        self.assertNotIn("ERROR", (self.project / "book.md").read_text())
        receipt = result["checkpoint"]
        manifest = json.loads((Path(receipt["path"]) / "manifest.json").read_text())
        expected = {row["path"]: row["sha256"] for row in manifest["files"]}
        shutil.rmtree(self.project)
        restored = self.base / "restored"
        loop.restore_project(receipt["path"], restored, receipt["manifest_sha256"],
                             receipt["requirements"], receipt["requirements_sha256"])
        self.assertTrue(all(sha((restored / path).read_bytes()) == h for path, h in expected.items()))
        resumed_model = self.fixture.ScriptedModel()
        again = loop.WritingLoop(restored, self.cfg, model=resumed_model,
                                expected_state_sha=receipt["state_sha256"]).run()
        self.assertEqual(again["resume"], "ALREADY_COMPLETE_NO_MODEL_CALL", again)
        self.assertEqual(resumed_model.calls, [])
        state = json.loads((restored / "run_state.json").read_text())
        self.assertEqual(state["acceptance"]["AUTHOR_ACCEPTANCE"], "NOT_RUN")
        self.assertEqual(state["acceptance"]["HUMAN_BLIND_EVALUATION"], "NOT_RUN")

    def test_same_version_fake_protocol_commit_is_not_an_active_pin(self):
        self.cfg["pins"]["protocols"]["deepwrite"]["commit"] = "f" * 40
        with self.assertRaisesRegex(self.fixture.loop.Blocked, "STABLE_WRITER_PROTOCOL"):
            self.fixture.loop.WritingLoop(self.project, self.cfg, model=self.fixture.ScriptedModel())


if __name__ == "__main__":
    unittest.main()
