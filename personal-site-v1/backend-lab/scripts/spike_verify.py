from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "personal-site-v1" / "backend-lab"
SAMPLE = LAB / "sample-content" / "genius-trader-tail-risk.md"

required = ["title", "dek", "slug", "date", "tags", "draft"]
text = SAMPLE.read_text(encoding="utf-8")
assert text.startswith("---\n"), "sample missing front matter"
_, front, body = text.split("---", 2)

meta: dict[str, object] = {}
current_list = None
for raw in front.strip().splitlines():
    if not raw.strip():
        continue
    if raw.startswith("  - ") and current_list:
        meta[current_list].append(raw[4:].strip())  # type: ignore[index]
        continue
    key, value = raw.split(":", 1)
    key, value = key.strip(), value.strip()
    if value == "":
        meta[key] = []
        current_list = key
    else:
        current_list = None
        if value in {"true", "false"}:
            meta[key] = value == "true"
        else:
            meta[key] = value

for key in required:
    assert key in meta, f"missing common field: {key}"
assert re.fullmatch(r"[a-z0-9-]+", str(meta["slug"])), "slug is not URL-safe"
assert len(body.strip()) > 200, "representative body too short"

checks = {
    "pagescms": LAB / "pagescms" / ".pages.yml",
    "sveltia": LAB / "sveltia" / "config.yml",
    "tina": LAB / "tina" / "config.ts",
}
for name, path in checks.items():
    candidate = path.read_text(encoding="utf-8")
    assert "personal-site-v1/content/essays" in candidate, f"{name} targets a different content store"
    for field in required + ["body"]:
        assert field in candidate, f"{name} missing field {field}"

payload = (LAB / "payload" / "ASSESSMENT.md").read_text(encoding="utf-8")
assert "database" in payload.lower(), "Payload operational cost not recorded"
issue = (LAB / "github-issues" / "ASSESSMENT.md").read_text(encoding="utf-8")
assert "publish-longform.yml" in issue, "control transport not tied to real existing workflow"

manifest = {
    "schema": 1,
    "source": "Git-backed Markdown representative fixture",
    "entry": meta | {"body_chars": len(body.strip())},
    "accepted_frontend_identity": "b82b5bb2496d9b7ccd960f0785e7fde15e86be0a",
}
out = LAB / "spike-output" / "content-manifest.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=False, indent=2))
