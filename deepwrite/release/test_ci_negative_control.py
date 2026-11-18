"""Real CI negative control; public engineering fixture, not writing evidence.

This isolated draft PR intentionally begins with a flag that makes this test
fail. Removing the flag is the repair. It must never be represented as an
independent review, literary quality result, or proof of repository settings.
"""
from pathlib import Path
import unittest


class PipelineNegativeControl(unittest.TestCase):
    def test_release_negative_control_flag_is_absent(self):
        flag = Path(__file__).resolve().parent / "evidence" / "CI_NEGATIVE_CONTROL"
        self.assertFalse(
            flag.exists(),
            "EXPECTED ENGINEERING NEGATIVE CONTROL: remove the isolated CI flag "
            "to repair this draft PR; no manuscript or production code is involved.",
        )


if __name__ == "__main__":
    unittest.main()
