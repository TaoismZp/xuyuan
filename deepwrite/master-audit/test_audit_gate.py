#!/usr/bin/env python3
"""Public synthetic regression fixtures only; no private manuscript text."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("audit_gate.py")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob_sha(b: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


class MasterAuditGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.source = self.dir / "source.md"
        self.manifest = self.dir / "manifest.json"
        self.contract = self.dir / "contract.json"
        self.receipts = self.dir / "receipts.json"
        self.semantic = self.dir / "semantic.md"
        s1 = "# 第一章\n这是一段为了验证覆盖流程而编写的原始合成文字。\n"
        s2 = "# 第二章\n另一段独立的合成内容，用来证明分片可逐一核验。\n"
        raw1, raw2 = s1.encode("utf-8"), s2.encode("utf-8")
        raw = raw1 + raw2
        self.source.write_bytes(raw)
        self.source_sha = blob_sha(raw)
        self.chunks = [
            {"id": "P0001", "start_byte": 0, "end_byte_exclusive": len(raw1),
             "start_line": 1, "end_line": 2, "sha256": sha256(raw1)},
            {"id": "P0002", "start_byte": len(raw1), "end_byte_exclusive": len(raw),
             "start_line": 3, "end_line": 4, "sha256": sha256(raw2)},
        ]
        self.save(self.manifest, {"source_blob_sha1": self.source_sha,
                                 "source_sha256": sha256(raw), "source_bytes_utf8": len(raw),
                                 "chunks": self.chunks})
        self.save(self.contract, {"project_id": "synthetic-audit-fixture",
                                  "author_goal": "Read all chapters and explain their independent arguments",
                                  "source_blob_sha1": self.source_sha,
                                  "workflow_policy": "deepwrite/master-audit/MASTER_AUDIT_POLICY_v1.md",
                                  "author_fulltext_required": True})
        self.rows = [
            {"id": "P0001", "source_blob": self.source_sha,
             "source_chunk_sha256": self.chunks[0]["sha256"],
             "quote": "为了验证覆盖流程而编写的原始合成文字",
             "semantic_function": "完整检查第一章的真实片内短引与独有陈述位置，反方理由待后续确认。",
             "status": "READ_CONFIRMED_SOURCE_RANGE_AND_EDIT_NOTE",
             **{k: self.chunks[0][k] for k in ("start_byte", "end_byte_exclusive", "start_line", "end_line")}},
            {"id": "P0002", "source_blob": self.source_sha,
             "source_chunk_sha256": self.chunks[1]["sha256"],
             "quote": "另一段独立的合成内容，用来证明分片",
             "semantic_function": "第二章采用不同素材说明完整内容与分片边界的一致，尚非文学验收。",
             "status": "READ_CONFIRMED_SOURCE_RANGE_AND_EDIT_NOTE",
             **{k: self.chunks[1][k] for k in ("start_byte", "end_byte_exclusive", "start_line", "end_line")}},
        ]
        self.save(self.receipts, {"source_blob": self.source_sha, "records": self.rows})
        self.semantic.write_text("# 章节机制与跨章审查\n" + "通过源领域与反方比较确认章节角色；" * 15, encoding="utf-8")

    @staticmethod
    def save(path: Path, data: dict):
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def run_gate(self, phase: str, *, receipt=True, semantic=False):
        args = [sys.executable, str(SCRIPT), phase, "--source", str(self.source),
                "--manifest", str(self.manifest), "--contract", str(self.contract)]
        if receipt:
            args += ["--receipt", str(self.receipts)]
        if semantic:
            args += ["--semantic-ledger", str(self.semantic)]
        return subprocess.run(args, capture_output=True, text=True, check=False)

    def test_preflight_does_not_claim_read(self):
        r = self.run_gate("preflight", receipt=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["read_receipts_verified"], 0)

    def test_progress_accepts_exact_quotes(self):
        r = self.run_gate("progress")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["read_receipts_verified"], 2)

    def test_complete_requires_ledger(self):
        r = self.run_gate("complete")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("SEMANTIC_BOOKWIDE_LEDGER_REQUIRED", r.stderr)

    def test_complete_evidence_scope_only(self):
        r = self.run_gate("complete", semantic=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["author_approval"], "PENDING")

    def test_missing_receipt_blocks_complete(self):
        self.save(self.receipts, {"source_blob": self.source_sha, "records": self.rows[:1]})
        r = self.run_gate("complete", semantic=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("STRICT_FULL_READ_INCOMPLETE", r.stderr)

    def test_fake_quote_blocks_progress(self):
        wrong = dict(self.rows[0])
        wrong["quote"] = "本片原文中绝对不存在这个短引"
        self.save(self.receipts, {"source_blob": self.source_sha, "records": [wrong]})
        r = self.run_gate("progress")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("QUOTE_NOT_IN_FROZEN_CHUNK", r.stderr)

    def test_missing_byte_blocks_preflight(self):
        broken = [dict(x) for x in self.chunks]
        broken[1]["start_byte"] += 1
        self.save(self.manifest, {"source_blob_sha1": self.source_sha,
                                  "source_sha256": sha256(self.source.read_bytes()),
                                  "source_bytes_utf8": len(self.source.read_bytes()),
                                  "chunks": broken})
        r = self.run_gate("preflight", receipt=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("SOURCE_BYTE_COVERAGE_FAIL", r.stderr)

    def test_wrong_manuscript_blocks_preflight(self):
        self.source.write_text("# 被篡改的原文\n", encoding="utf-8")
        r = self.run_gate("preflight", receipt=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("CONTRACT_SOURCE_SHA_MISMATCH", r.stderr)


if __name__ == "__main__":
    unittest.main()
