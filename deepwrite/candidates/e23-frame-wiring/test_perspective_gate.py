#!/usr/bin/env python3
"""Synthetic regression for experimental prewrite guard. No proprietary manuscripts."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from perspective_gate import evaluate

def h(x):
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

class PerspectiveGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        prior = "Prior manuscript explicitly recognizes a familiar earlier mechanism where delayed observation changes the price."
        source = "Original domain rules permit a position to gain informational advantage while retaining possible counter-moves."
        (self.root / "prior.md").write_text(prior, encoding="utf-8")
        (self.root / "source.md").write_text(source, encoding="utf-8")
        self.prior = prior
        self.source = source
        self.base = {
          "schema": "deepwrite/perspective-inversion/v0.1",
          "prior_drafts": [{"path":"prior.md","sha256":h(prior)}],
          "source_materials": [{"path":"source.md","sha256":h(source)}],
          "lenses": []
        }
        def make(i,mode,verdict,quote):
            return {
                "id": "L" + str(i),
                "source_assumption": "Conventional theory version " + str(i) + " assumes a stable objective",
                "counterinterpretation": "Alternative explanatory account " + str(i) + " rejects the default",
                "source_mechanism": "The original rules specify asymmetric moves and limited rights",
                "source_falsifier": "A player can respond before the assumed advantage materializes",
                "target_default": "Investors assume information can be awaited without any cost",
                "target_break": "The target system re-prices observable evidence differently " + str(i),
                "decision_before": "Act by extrapolating the unchanged baseline likelihood",
                "decision_after": "Make the decision contingent on a newly revised risk budget",
                "target_falsifier": "The information can arrive without creating any price divergence",
                "why_book_architecture_changes": "The proposed interpretation changes which problem comes first",
                "claim_type": mode,
                "source_quotes": [{"source_index":0,"quote":"informational advantage while retaining possible counter-moves"}],
                "prior_checks":[{"prior_index":0,"verdict":verdict,"quote":quote}]
            }
        self.base["lenses"] = [
            make(1,"RECOVERED","COVERED","earlier mechanism where delayed observation changes the price"),
            make(2,"REFRAME","PARTIAL","familiar earlier mechanism where delayed observation changes the price"),
            make(3,"HYPOTHESIS_NEW","NOT_FOUND_UNVERIFIED","")
        ]

    def tearDown(self): self.tmp.cleanup()

    def test_holds_even_when_structurally_complete(self):
        obj = evaluate(self.base, self.root)
        self.assertEqual(obj["structural"],"PASS")
        self.assertFalse(obj["quality_or_novelty_auto_pass"])
        self.assertEqual(obj["prewrite_decision"],"HOLD_PERSPECTIVE_ADJUDICATION_NO_BOOK_REWRITE")
        self.assertEqual(obj["lenses"][0]["status"],"REJECT_AS_NEW_DISCOVERY")

    def test_prior_covered_must_not_be_called_new(self):
        m = copy.deepcopy(self.base)
        m["lenses"][0]["claim_type"] = "HYPOTHESIS_NEW"
        o = evaluate(m, self.root)
        self.assertIn("FALSE_NOVELTY_CONFLICTS_WITH_COVERED_PRIOR",o["lenses"][0]["errors"])
        self.assertEqual(o["prewrite_decision"],"STOP_REPAIR_INPUTS")

    def test_wrong_source_quote_fails(self):
        m = copy.deepcopy(self.base)
        m["lenses"][1]["source_quotes"][0]["quote"] = "This quotation was never in the source file"
        self.assertIn("SOURCE_QUOTE_NOT_VERIFIED",evaluate(m,self.root)["lenses"][1]["errors"])

    def test_wrong_prior_quote_fails(self):
        m = copy.deepcopy(self.base)
        m["lenses"][1]["prior_checks"][0]["quote"]="a completely invented excerpt from a fabricated prior"
        self.assertIn("PRIOR_COVERAGE_QUOTE_NOT_VERIFIED",evaluate(m,self.root)["lenses"][1]["errors"])

    def test_tampered_hash_fails(self):
        m = copy.deepcopy(self.base)
        m["prior_drafts"][0]["sha256"] = "0"*64
        self.assertIn("PRIOR_SHA_MISMATCH",evaluate(m,self.root)["issues"])

    def test_not_enough_competitors_fails(self):
        m=copy.deepcopy(self.base)
        m["lenses"]=m["lenses"][:2]
        self.assertIn("LESS_THAN_THREE_COMPETING_LENSES",evaluate(m,self.root)["issues"])

    def test_duplicate_candidate_fails(self):
        m=copy.deepcopy(self.base)
        m["lenses"][2]=copy.deepcopy(m["lenses"][1])
        self.assertIn("DUPLICATE_FRAME",evaluate(m,self.root)["lenses"][2]["errors"])

    def test_not_found_is_not_proof_of_novelty(self):
        obj = evaluate(self.base, self.root)
        self.assertEqual(obj["lenses"][2]["status"],"HOLD_HUMAN_SEMANTIC_AND_ADVERSARIAL_REVIEW")

    def test_missing_prior_baseline_fails(self):
        m=copy.deepcopy(self.base)
        m["prior_drafts"]=[]
        self.assertIn("NO_FROZEN_PRIOR_DRAFT",evaluate(m,self.root)["issues"])

if __name__=="__main__":
    unittest.main()