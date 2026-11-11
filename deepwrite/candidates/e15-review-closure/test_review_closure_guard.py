import copy
import unittest
from review_closure_guard import check

BASE = {
    "schema": "deepwrite/review-closeout/v0",
    "baseline_sha256": "a" * 64,
    "candidate_sha256": "b" * 64,
    "comparison": {
        "baseline_read": True, "candidate_read": True,
        "reviewed_units": ["chapter-1", "chapter-2"],
        "comparison_rationale": "Compared actual paragraphs and chapter-specific reader decisions",
    },
    "findings": [],
}

def finding(status="OPEN", severity="MAJOR", **overrides):
    return dict({"id": "F-01", "severity": severity, "status": status,
                 "location": "chapter-2 p.4", "issue": "same decision as chapter-1"}, **overrides)

class GateTests(unittest.TestCase):
    def setUp(self):
        self.case = copy.deepcopy(BASE)

    def assert_hold(self):
        self.assertEqual(check(self.case)["status"], "HOLD")

    def test_unresolved_review_blocks_even_when_book_complete(self):
        self.case["findings"] = [finding()]
        self.assert_hold()

    def test_report_closed_without_text_recheck_blocks(self):
        self.case["findings"] = [finding("CLOSED")]
        self.assert_hold()

    def test_stale_recheck_sha_blocks(self):
        self.case["findings"] = [finding("CLOSED", revised_sha256="c" * 64, recheck_evidence="checked")]
        self.assert_hold()

    def test_fixed_and_rechecked_passes_only_structurally(self):
        self.case["findings"] = [finding("CLOSED", revised_sha256="b" * 64, recheck_evidence="diff hunk and reread")]
        self.assertEqual(check(self.case)["status"], "PASS_STRUCTURAL_ONLY")

    def test_missing_comparison_blocks(self):
        self.case["comparison"]["baseline_read"] = False
        self.assert_hold()

    def test_missing_baseline_blocks(self):
        self.case.pop("baseline_sha256")
        self.assert_hold()

    def test_critical_cannot_be_waived(self):
        self.case["findings"] = [finding("WAIVED", "CRITICAL", authority="AUTHOR", risk_acceptance="ok")]
        self.assert_hold()

    def test_major_waiver_without_author_authority_blocks(self):
        self.case["findings"] = [finding("WAIVED", "MAJOR", authority="MODEL", risk_acceptance="ok")]
        self.assert_hold()

    def test_minor_open_is_visible_but_not_blocking(self):
        self.case["findings"] = [finding("OPEN", "MINOR")]
        r = check(self.case)
        self.assertEqual(r["status"], "PASS_STRUCTURAL_ONLY")
        self.assertEqual(len(r["warnings"]), 1)

    def test_duplicate_finding_id_blocks(self):
        self.case["findings"] = [finding(), finding()]
        self.assert_hold()

    def test_missing_location_blocks(self):
        self.case["findings"] = [finding(location="")]
        self.assert_hold()

if __name__ == "__main__":
    unittest.main()
