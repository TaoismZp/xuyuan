#!/usr/bin/env python3
"""Deterministic E1 paired-call experiment controls. No external model calls."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("e25_pair_probe", TOOLS / "insight_pair_probe_experimental.py")
pair = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pair)

SOURCE = "A shared resource can be reserved, but the reader may fail to collect it before expiry."


def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PairProbeFixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / "source_root"
        (self.root / "sources").mkdir(parents=True)
        (self.root / "sources/public.md").write_text(SOURCE, encoding="utf-8")
        self.wish = "Research the competing costs of allocating a shared resource with limited pickup windows."
        self.source = {"path": "sources/public.md", "sha256": sha(SOURCE)}
        self.cfg = {
            "schema": pair.SCHEMA, "channel": "SHADOW", "model": "fixture-model",
            "wish": self.wish, "sources": [self.source],
            "max_output_tokens_per_arm": 2000,
            "insight_origin": {
                "schema": pair.gate.SCHEMA, "mode": "BLIND_PRE_REVEAL",
                "author_thesis_disclosed": False,
                "neutral_wish_sha256": sha(self.wish),
                "experiment_id": "synthetic_unseen_20261112",
                "source_roles": [dict(self.source, role="SOURCE_DOMAIN")],
            },
        }
        self.cfgpath = self.base / "config.json"
        self.out = self.base / "outputs"

    def tearDown(self):
        self.tmp.cleanup()

    def save(self):
        self.cfgpath.write_text(json.dumps(self.cfg, ensure_ascii=False), encoding="utf-8")

    def run_probe(self, **kwargs):
        self.save()
        return pair.run_probe(self.cfgpath, self.root, self.out, **kwargs)

    @staticmethod
    def model_factory(calls):
        class Model:
            def __init__(self, arm):
                self.arm = arm

            def generate(self, instructions, prompt, max_output_tokens):
                task = json.loads(prompt)
                calls.append((self.arm, instructions, task, max_output_tokens))
                lenses = []
                for i in range(3):
                    lenses.append({
                        "id": "L" + str(i),
                        "default_question": "What is the current baseline allocation rule number " + str(i),
                        "alternative_question": "How does a different decision objective alter allocation " + str(i),
                        "decision_before": "Keep the current short pickup window during cycle " + str(i),
                        "decision_after": "Compare alternative holding windows in cycle " + str(i),
                        "source_falsifier": "If pickup failures never occur this would not change resource allocation.",
                        "source_anchor": {"path": "sources/public.md",
                                          "quote": "the reader may fail to collect it before expiry"},
                    })
                result = {"origin_status": "MODEL_PROPOSAL_UNVERIFIED", "lenses": lenses}
                return SimpleNamespace(text=json.dumps(result), response_id="fixture-" + self.arm,
                                       model="fixture-model", provider_kind="scripted_fixture",
                                       usage={"input_tokens": 35, "output_tokens": 70})
        return Model

    def test_preflight_freezes_inputs_no_model_calls(self):
        r = self.run_probe(preflight_only=True)
        self.assertEqual(r["status"], "PREFLIGHT_PASS_NO_MODEL_CALL")
        self.assertFalse((self.out / "A0_NEUTRAL.response.json").exists())
        self.assertTrue((self.out / "A0_NEUTRAL.request.json").exists())
        self.assertTrue((self.out / "A1_ASSUMPTION_CHALLENGE.request.json").exists())
        self.assertEqual(json.loads((self.out / "input_manifest.json").read_text())["source_sha256"]
                         ["sources/public.md"], sha(SOURCE))

    def test_two_calls_same_source_same_model_same_cap(self):
        self.save()
        calls = []
        factory = self.model_factory(calls)
        r = pair.run_probe(self.cfgpath, self.root, self.out, model_factory=factory)
        self.assertEqual(r["status"], "FIXTURE_A0_A1_FROZEN_NO_MODEL_EVIDENCE", r)
        self.assertEqual(len(calls), 2)
        self.assertEqual([x[0] for x in calls], ["A0_NEUTRAL", "A1_ASSUMPTION_CHALLENGE"])
        self.assertEqual(calls[0][2]["sources"], calls[1][2]["sources"])
        self.assertEqual(calls[0][3], calls[1][3])
        self.assertEqual(r["quality"], "UNVERIFIED")
        self.assertEqual(r["human_blind_review"], "NOT_RUN")
        self.assertTrue(all((self.out / (x[0] + ".response.json")).exists() for x in calls))
        self.assertTrue(all(json.loads((self.out / (x[0] + ".audit.json")).read_text())
                            ["status"] == "PASS_STRUCTURAL_ORIGIN_FROZEN_SEMANTICS_UNVERIFIED"
                            for x in calls))

    def test_missing_key_records_blocked_not_synthetic_pass(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            r = self.run_probe()
        self.assertEqual(r["status"], "BLOCKED_MISSING_OPENAI_API_KEY")
        self.assertEqual(json.loads((self.out / "status.json").read_text())["quality"], "UNVERIFIED")
        self.assertFalse((self.out / "A1_ASSUMPTION_CHALLENGE.response.json").exists())

    def test_tampered_source_does_not_call_or_create_results(self):
        self.cfg["sources"][0]["sha256"] = "0" * 64
        self.cfg["insight_origin"]["source_roles"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SOURCE_SHA256_MISMATCH"):
            self.run_probe(preflight_only=True)
        self.assertFalse(self.out.exists())

    def test_author_thesis_declared_fails_closed(self):
        self.cfg["insight_origin"]["source_roles"][0]["role"] = "AUTHOR_THESIS"
        with self.assertRaisesRegex(ValueError, "SOURCE_ROLE_DISALLOWED"):
            self.run_probe(preflight_only=True)
        self.assertFalse(self.out.exists())

    def test_second_paid_call_wont_repeat_on_same_directory(self):
        self.run_probe(preflight_only=True)
        with self.assertRaisesRegex(ValueError, "FROZEN_RUN_DIRECTORY_MUST_NOT_EXIST"):
            self.run_probe(preflight_only=True)

    def test_output_cap_must_be_equal_and_large_enough(self):
        self.cfg["max_output_tokens_per_arm"] = 80
        with self.assertRaisesRegex(ValueError, "INVALID_EQUAL_OUTPUT_BUDGET"):
            self.run_probe(preflight_only=True)

    def test_malformed_proposal_does_not_fake_insight_pass(self):
        class BadModel:
            def generate(self, instructions, prompt, max_output_tokens):
                return SimpleNamespace(text='{"lenses":[]}', response_id="bad",
                                       model="fixture-model", provider_kind="scripted_fixture",
                                       usage={"input_tokens": 10, "output_tokens": 10})
        r = self.run_probe(model_factory=lambda arm: BadModel())
        self.assertEqual(r["status"], "FIXTURE_A0_A1_FROZEN_NO_MODEL_EVIDENCE")
        audit = json.loads((self.out / "A0_NEUTRAL.audit.json").read_text())
        self.assertEqual(audit["status"], "STOP_INVALID_MODEL_FRAME")
        self.assertEqual(r["quality"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
