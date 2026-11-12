#!/usr/bin/env python3
"""Research-only A0/A1 fresh-call probe for DeepWrite insight origination.

Not an alternative book writer. Uses the existing E18 OpenAI Responses transport
and E23 experimental insight gate. This tool does not grade novel ideas or use
author/private conclusions in a public fixture. Caller owns private data/output.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys


DW = Path(__file__).resolve().parents[1]


def import_path(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = obj
    spec.loader.exec_module(obj)
    return obj


gate = import_path("e25_insight_gate", DW / "candidates/e23-frame-wiring/insight_origin_gate.py")
transport = import_path("e25_transport", DW / "tools/model_adapter_openai_responses_experimental_v0_1.py")
SCHEMA = "deepwrite/insight-pair-probe/v0.1"


def digest(b):
    return hashlib.sha256(b).hexdigest()


def canonical(x):
    return (json.dumps(x, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_once(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(data)


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("UNSAFE_SOURCE_PATH")
    parts = Path(relative).parts
    if any(x in (".", "..") for x in parts):
        raise ValueError("UNSAFE_SOURCE_COMPONENT")
    p = root / relative
    if not p.resolve().is_relative_to(root.resolve()) or not p.is_file() or p.is_symlink():
        raise ValueError("SOURCE_OUTSIDE_PRIVATE_WORKSPACE")
    return p


def preflight(config, source_root):
    if config.get("schema") != SCHEMA or config.get("channel") != "SHADOW":
        raise ValueError("REQUIRES_EXPERIMENTAL_SHADOW_CONFIG")
    if not isinstance(config.get("model"), str) or not config["model"].strip():
        raise ValueError("EXPLICIT_MODEL_REQUIRED")
    if config["model"].upper().startswith(("VERIFY_", "REPLACE_", "MODEL_ID_")):
        raise ValueError("MODEL_ID_MUST_BE_VERIFIED_BEFORE_PREFLIGHT")
    lim = config.get("max_output_tokens_per_arm")
    if type(lim) is not int or not 256 <= lim <= 16000:
        raise ValueError("INVALID_EQUAL_OUTPUT_BUDGET")
    wish = config.get("wish")
    if not isinstance(wish, str) or len(wish.strip()) < 20:
        raise ValueError("NEUTRAL_WISH_REQUIRED")
    frozen = config.get("insight_origin")
    if not isinstance(frozen, dict):
        raise ValueError("INSIGHT_ORIGIN_CONTRACT_REQUIRED")
    gate.check_run_config(dict(config, run_mode="fresh"))
    sources = {}
    for row in config["sources"]:
        name = row["path"]
        if name in sources:
            raise ValueError("DUPLICATE_SOURCE_PATH")
        content = safe_path(source_root, name).read_bytes()
        if digest(content) != row["sha256"]:
            raise ValueError("SOURCE_SHA256_MISMATCH")
        try:
            sources[name] = content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("SOURCE_NOT_UTF8") from None
    return sources


_COMMON = (
    "You are evaluating only the research questions raised by the provided "
    "source texts. Do NOT write a book chapter or infer an author's intended answer. "
    "Your answer MUST be a standalone JSON object with origin_status="
    "'MODEL_PROPOSAL_UNVERIFIED', and lenses containing >=3 items. "
    "Each lens has id, default_question, alternative_question, decision_before, "
    "decision_after, source_falsifier, source_anchor:{path,quote}. "
    "Quote verbatim from one provided source path (>=12 characters), "
    "make decisions concrete and testable, avoid invented facts. "
    "No claim of authorship, novelty, author approval, or scientific proof."
)
_ARMS = {
    "A0_NEUTRAL": (
        "Develop alternative research questions about this material; explain "
        "what decision each question might change, using exact evidence."
    ),
    "A1_ASSUMPTION_CHALLENGE": (
        "Before settling on any question, examine the standard question's assumed "
        "objective, excluded costs or actors, unexplained observations and strongest "
        "counterexamples. Generate rival questions that could produce different "
        "decisions; if the ordinary interpretation holds, allow it to survive."
    ),
}


def request_for(arm, config, sources):
    return {
        "arm": arm,
        "model": config["model"],
        "max_output_tokens": config["max_output_tokens_per_arm"],
        "instructions": _COMMON,
        "payload": {"neutral_wish": config["wish"], "sources": sources,
                    "task": _ARMS[arm]},
    }


def run_probe(config_path, source_root, output_dir, model_factory=None, preflight_only=False):
    config_path = Path(config_path).resolve()
    source_root = Path(source_root).resolve()
    output_dir = Path(output_dir).absolute()
    cfg_raw = config_path.read_bytes()
    config = json.loads(cfg_raw)
    sources = preflight(config, source_root)
    arms = {arm: request_for(arm, config, sources) for arm in _ARMS}
    if output_dir.exists():
        raise ValueError("FROZEN_RUN_DIRECTORY_MUST_NOT_EXIST")
    output_dir.mkdir(parents=True, exist_ok=False)
    write_once(output_dir / "config.frozen.json", cfg_raw)
    write_once(output_dir / "input_manifest.json", canonical({
        "schema": SCHEMA, "input_config_sha256": digest(cfg_raw),
        "source_sha256": {name: digest(value.encode("utf-8")) for name, value in sources.items()},
        "arms": list(_ARMS), "model": config["model"],
        "max_output_tokens_each": config["max_output_tokens_per_arm"],
        "test_quality": "NOT_RUN", "author_thesis_semantic_absence": "UNVERIFIED",
    }))
    for arm, request in arms.items():
        write_once(output_dir / (arm + ".request.json"), canonical(request))
    if preflight_only:
        status = {"status": "PREFLIGHT_PASS_NO_MODEL_CALL",
                  "quality": "UNVERIFIED", "comparison": "NOT_RUN"}
        write_once(output_dir / "status.json", canonical(status))
        return status
    if model_factory is None and not os.environ.get("OPENAI_API_KEY"):
        status = {"status": "BLOCKED_MISSING_OPENAI_API_KEY",
                  "quality": "UNVERIFIED", "comparison": "NOT_RUN"}
        write_once(output_dir / "status.json", canonical(status))
        return status
    receipts = {}
    for arm, request in arms.items():
        try:
            # Each arm receives a *fresh* transport instance; no conversational context
            # or previous_response_id is passed. Real provider calls must be recorded.
            m = (model_factory(arm) if model_factory else
                 transport.OpenAIResponses(config["model"]))
            payload = canonical(request["payload"]).decode("utf-8")
            reply = m.generate(request["instructions"], payload,
                               max_output_tokens=request["max_output_tokens"])
            record = {
                "arm": arm, "provider_kind": reply.provider_kind,
                "response_id": reply.response_id, "model": reply.model,
                "usage": reply.usage, "output_sha256": digest(reply.text.encode("utf-8")),
                "raw_output": reply.text,
            }
            write_once(output_dir / (arm + ".response.json"), canonical(record))
            try:
                parsed = json.loads(reply.text)
                audit = gate.inspect_proposals(parsed, sources)
            except (TypeError, ValueError, json.JSONDecodeError):
                audit = {"status": "STOP_INVALID_MODEL_JSON", "semantic_novelty": "UNVERIFIED"}
            write_once(output_dir / (arm + ".audit.json"), canonical(audit))
            receipts[arm] = {"response_id": reply.response_id,
                             "model": reply.model, "usage": reply.usage,
                             "output_sha256": record["output_sha256"],
                             "audit": audit["status"], "provider_kind": reply.provider_kind}
        except Exception as error:
            # A failed invocation must never lead to a second automatic paid call.
            # Do not copy provider error bodies or environment credentials.
            status = {"status": "BLOCKED_MODEL_CALL", "failed_arm": arm,
                      "error_class": type(error).__name__,
                      "quality": "UNVERIFIED", "completed_receipts": receipts}
            write_once(output_dir / "status.json", canonical(status))
            return status
    is_live = all(x["provider_kind"] == "openai_live" for x in receipts.values())
    models_match = (receipts["A0_NEUTRAL"]["model"] == receipts["A1_ASSUMPTION_CHALLENGE"]["model"])
    status = {"status": ("BLOCKED_SERVED_MODEL_MISMATCH" if not models_match else
                          "LIVE_A0_A1_FROZEN_QUALITY_UNVERIFIED" if is_live else
                          "FIXTURE_A0_A1_FROZEN_NO_MODEL_EVIDENCE"),
              "same_model_requested": True,
              "served_model_identity_equal": models_match,
              "same_output_cap": True,
              "actual_token_usage_equal": (receipts["A0_NEUTRAL"]["usage"] ==
                                            receipts["A1_ASSUMPTION_CHALLENGE"]["usage"]),
              "research_prompt_length_equal": False,
              "quality": "UNVERIFIED", "human_blind_review": "NOT_RUN",
              "receipts": receipts}
    write_once(output_dir / "status.json", canonical(status))
    return status


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--source-root", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--preflight", action="store_true")
    args = ap.parse_args()
    try:
        result = run_probe(args.config, args.source_root, args.output_dir,
                           preflight_only=args.preflight)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {"status": "BLOCKED_PREFLIGHT", "error_class": type(exc).__name__,
                  "message": str(exc)[:160], "quality": "UNVERIFIED"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in (
        "PREFLIGHT_PASS_NO_MODEL_CALL", "LIVE_A0_A1_FROZEN_QUALITY_UNVERIFIED",
        "FIXTURE_A0_A1_FROZEN_NO_MODEL_EVIDENCE") else 2


if __name__ == "__main__":
    raise SystemExit(main())
