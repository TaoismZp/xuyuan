#!/usr/bin/env python3
"""Real PR #26 audit_gate integration regression; synthetic bytes, no model-quality claim.

Run with:
 python3 test_real_pr26_gate.py /path/to/audit_gate.py
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

GATE = Path(sys.argv.pop()).resolve() if len(sys.argv) > 1 else Path("deepwrite/master-audit/audit_gate.py").resolve()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

class RealGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = ("# 序言\n证据一二三四五六七八。\n# 第一章\n证据九十十一十二十三十四。\n").encode()
        self.write("book.md", self.source)
        self.parts = []
        start = 0
        lines = self.source.splitlines(keepends=True)
        for i, line in enumerate(lines):
            end = start + len(line)
            self.parts.append(dict(id=f"P{i+1:04d}",start_byte=start,end_byte_exclusive=end,
                start_line=i+1,end_line=i+1,sha256=sha(line)))
            start = end
        self.contract = dict(project_id="SYNTHETIC",author_goal="Synthetic audit fixture",
            source_blob_sha1=blob(self.source),workflow_policy="CANDIDATE_ONLY",
            author_fulltext_required=True)
        self.manifest = dict(source_blob_sha1=blob(self.source),
            source_bytes_utf8=len(self.source),source_sha256=sha(self.source),chunks=self.parts)
        self.receipts = dict(source_blob=blob(self.source),receipts=[
            dict(id=p["id"],start_byte=p["start_byte"],end_byte_exclusive=p["end_byte_exclusive"],
                start_line=p["start_line"],end_line=p["end_line"],source_chunk_sha256=p["sha256"],
                source_blob=blob(self.source),quote=self.source[p["start_byte"]:p["end_byte_exclusive"]].decode().strip(),
                semantic_function="Synthetic evidence note; not evidence of real model comprehension.",
                status="READ_CONFIRMED_SYNTHETIC") for p in self.parts])
        for name, obj in (("contract.json",self.contract),("manifest.json",self.manifest),
                          ("receipt.json",self.receipts),("semantic.json",{"note":"synthetic "*20})):
            self.write(name,json.dumps(obj,ensure_ascii=False).encode())

    def write(self,name,data):
        (self.root/name).write_bytes(data)

    def run_gate(self,phase="complete"):
        cmd=[sys.executable,str(GATE),phase,"--source",str(self.root/"book.md"),
             "--contract",str(self.root/"contract.json"),"--manifest",str(self.root/"manifest.json"),
             "--semantic-ledger",str(self.root/"semantic.json"),"--receipt",str(self.root/"receipt.json")]
        return subprocess.run(cmd,capture_output=True,text=True,timeout=15)

    def test_real_gate_complete_fixture(self):
        p=self.run_gate()
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)["status"],"SOURCE_RECEIPTS_COMPLETE_SCOPED")

    def test_mutated_source_fails(self):
        self.write("book.md",self.source+b"tampered")
        self.assertNotEqual(self.run_gate().returncode,0)

    def test_missing_receipt_fails(self):
        self.receipts["receipts"].pop()
        self.write("receipt.json",json.dumps(self.receipts,ensure_ascii=False).encode())
        self.assertNotEqual(self.run_gate().returncode,0)

    def test_forged_quote_fails(self):
        self.receipts["receipts"][0]["quote"]="NOT IN SOURCE 12345"
        self.write("receipt.json",json.dumps(self.receipts,ensure_ascii=False).encode())
        self.assertNotEqual(self.run_gate().returncode,0)

    def test_wrong_chunk_hash_fails(self):
        self.receipts["receipts"][0]["source_chunk_sha256"]="0"*64
        self.write("receipt.json",json.dumps(self.receipts,ensure_ascii=False).encode())
        self.assertNotEqual(self.run_gate().returncode,0)

if __name__=="__main__":
    if not GATE.is_file():
        raise SystemExit("Actual PR26 audit_gate.py required; do not substitute mock")
    unittest.main()
