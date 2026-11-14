#!/usr/bin/env python3
"""Actual bytes / architecture preflight regression; not proof of research originality."""
import copy
import hashlib
import unittest
from source_first_gate import validate, SCHEMA


def h(raw):
    return hashlib.sha256(raw).hexdigest()


class SourceFirstGateTests(unittest.TestCase):
    def setUp(self):
        self.texts = {
            "sources/native.md": b"A buyer can wait for a lower quote, but that quote may never be offered.",
            "sources/study.md": b"Native source first. Compare rival structures before chapters."
        }
        self.cfg = {
            "project_id": "project-01",
            "chapters": [{"artifact_id": "ch1"}, {"artifact_id": "ch2"}],
            "sources": [{"path": path, "sha256": h(raw)} for path, raw in self.texts.items()],
            "source_first_architecture": {
                "schema": SCHEMA, "project_id": "project-01",
                "status": "PROVISIONAL_NOT_AUTHOR_APPROVED",
                "source_study": {"path": "sources/study.md", "sha256": h(self.texts["sources/study.md"])},
                "source_concepts": [{
                    "id": "quote_selection", "source_path": "sources/native.md",
                    "quote": "a lower quote, but that quote may never be offered",
                    "causal_mechanism": "Orders not filled are not sampled by the executed account.",
                    "counterinterpretation": "A passive order can receive positive expected spread.",
                    "transfer_limit": "Large-time-scale buy-and-hold may ignore tiny spread changes."
                }],
                "rival_directions": [
                    {"id": "pricing_first", "source_question": "What does a reported chance actually measure?",
                     "reader_problem": "A reader needs to separate predictions from decisions.",
                     "tradeoff": "This direction may overlap existing opening material."},
                    {"id": "execution_first", "source_question": "Which returns are actually executable?",
                     "reader_problem": "The reader should distinguish market from account outcomes.",
                     "tradeoff": "The example depends on market microstructure assumptions."}
                ],
                "selected_direction_id": "execution_first",
                "why_selected_over_rivals": "Makes the conditional selection problem concrete before statistics.",
                "book_design": {
                    "status": "PROVISIONAL",
                    "why_these_chapters_not_source_outline": "Two source mechanisms require distinct decision conditions.",
                    "chapter_contributions": [
                        {"chapter_id": "ch1", "source_concept_ids": ["quote_selection"],
                         "distinct_reader_change": "Separate forecast distribution from realizable trades."},
                        {"chapter_id": "ch2", "source_concept_ids": ["quote_selection"],
                         "distinct_reader_change": "Identify how execution conditions select returns."}
                    ]
                }
            }
        }

    def gate(self, cfg=None):
        return validate(cfg if cfg is not None else self.cfg, lambda path: self.texts[path])

    def test_valid_separate_source_and_book_topology_is_engineering_only(self):
        x = self.gate()
        self.assertEqual(x["status"], "PASS_ENGINEERING_ONLY_PROVISIONAL_SOURCE_ARCHITECTURE")
        self.assertFalse(x["chronology_independently_verified"])
        self.assertEqual(x["chapter_number_author_approval"], "PENDING")
        self.assertEqual(x["three_level_reader_value"], "UNVERIFIED")

    def test_no_architecture_cannot_bypass(self):
        self.cfg.pop("source_first_architecture")
        with self.assertRaisesRegex(ValueError, "ARCHITECTURE_REQUIRED"):
            self.gate()

    def test_no_chapter_rationale_blocks_reused_source_outline(self):
        self.cfg["source_first_architecture"]["book_design"]["why_these_chapters_not_source_outline"] = ""
        with self.assertRaisesRegex(ValueError, "TOPOLOGY_RATIONALE"):
            self.gate()

    def test_study_claim_without_real_bytes_blocks(self):
        self.texts["sources/study.md"] = b"CHANGED"
        with self.assertRaisesRegex(ValueError, "STUDY_BYTES_MISMATCH"):
            self.gate()

    def test_original_source_tamper_blocks(self):
        self.texts["sources/native.md"] = b"tampered"
        with self.assertRaisesRegex(ValueError, "ORIGINAL_SOURCE_BYTES_MISMATCH"):
            self.gate()

    def test_unlocated_quote_blocks(self):
        self.cfg["source_first_architecture"]["source_concepts"][0]["quote"] = "a statement absent from source"
        with self.assertRaisesRegex(ValueError, "NOT_LOCATED_IN_ORIGINAL_SOURCE"):
            self.gate()

    def test_rival_direction_required(self):
        self.cfg["source_first_architecture"]["rival_directions"].pop()
        with self.assertRaisesRegex(ValueError, "RIVAL_DIRECTIONS_REQUIRED"):
            self.gate()

    def test_cannot_claim_author_approval(self):
        self.cfg["source_first_architecture"]["status"] = "AUTHOR_APPROVED"
        with self.assertRaisesRegex(ValueError, "CANNOT_AUTHENTICATE_AUTHOR"):
            self.gate()

    def test_wrong_project_cannot_reuse_authority(self):
        self.cfg["source_first_architecture"]["project_id"] = "other-project"
        with self.assertRaisesRegex(ValueError, "WRONG_PROJECT"):
            self.gate()

    def test_unmapped_extra_chapter_blocks(self):
        self.cfg["chapters"].append({"artifact_id": "ch3"})
        with self.assertRaisesRegex(ValueError, "CHAPTER_CONTRIBUTIONS_REQUIRED"):
            self.gate()

    def test_source_domains_are_not_identical_to_chapter_count(self):
        self.cfg["chapters"].pop()
        self.cfg["source_first_architecture"]["book_design"]["chapter_contributions"].pop()
        self.assertEqual(self.gate()["chapter_ids"], ["ch1"])

if __name__ == "__main__":
    unittest.main()
