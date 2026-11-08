#!/usr/bin/env python3
"""Offline synthetic regression for DeepWrite book_packager_v0.1.py."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGER = Path(__file__).resolve().parents[1] / "tools" / "book_packager_v0.1.py"

def hash_text(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()

def test_packager():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        (root/"chapters").mkdir()
        sources={
          "front.md":"# 序言\n\n测试序言。\n",
          "chapters/01.md":"# 第一章\n\n第一章正文。\n",
          "chapters/02.md":"# 第二章\n\n第二章正文。\n",
          "tail.md":"# 尾声\n\n测试尾声。\n"
        }
        for name,content in sources.items():
            path=root/name
            path.write_text(content,encoding="utf-8")
        def source(name): return {"relative_path":name,"sha256":hash_text(sources[name])}
        manifest={"working_title":"Synthetic book","expected_chapters":2,
          "chapters":[
            {"number":1,"title":"One","bytes":len(sources["chapters/01.md"].encode()),**source("chapters/01.md")},
            {"number":2,"title":"Two","bytes":len(sources["chapters/02.md"].encode()),**source("chapters/02.md")}],
          "front":source("front.md"),"tail":source("tail.md")}
        file=root/"manifest.json"
        file.write_text(json.dumps(manifest,ensure_ascii=False),encoding="utf-8")
        cmd=[sys.executable,str(PACKAGER),"--manifest",str(file),"--root",str(root),
             "--output",str(root/"book.md"),"--report",str(root/"report.json")]
        ok=subprocess.run(cmd,capture_output=True,text=True)
        assert ok.returncode==0,(ok.stdout,ok.stderr)
        book=(root/"book.md").read_text(encoding="utf-8")
        assert book.index("测试序言")<book.index("第一章正文")<book.index("第二章正文")<book.index("测试尾声")
        report=json.loads((root/"report.json").read_text(encoding="utf-8"))
        assert report["chapters"]==2
        assert report["sha256"]==hashlib.sha256((root/"book.md").read_bytes()).hexdigest()
        print("PASS synthetic assembly, order, and digest")
        (root/"chapters/02.md").write_text("tampered",encoding="utf-8")
        fail=subprocess.run(cmd,capture_output=True,text=True)
        assert fail.returncode!=0 and "SHA256 mismatch" in fail.stdout+fail.stderr
        print("PASS source tamper rejection")
        (root/"chapters/02.md").write_text(sources["chapters/02.md"],encoding="utf-8")
        manifest["chapters"][0]["number"]=2
        file.write_text(json.dumps(manifest,ensure_ascii=False),encoding="utf-8")
        fail2=subprocess.run(cmd,capture_output=True,text=True)
        assert fail2.returncode!=0
        print("PASS chapter order rejection")

if __name__=="__main__":test_packager()
