"""Bounded regression: two failures, useful controls, and no implicit resume."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from resume_check import check

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / 'deepwrite/experiments/2026-11-09-resume-boundary/replay_cases.py'
CHECKER = Path(__file__).with_name('resume_check.py')


class ResumeBoundaryTests(unittest.TestCase):
    def test_negative_cases_and_stable_and_opt_in_controls(self):
        execution = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(execution.returncode, 0, execution.stderr)
        receipt = json.loads(execution.stdout)
        cases = receipt['cases']
        self.assertEqual([c['actual_resume_check']['status'] for c in cases],
                         ['BLOCKED', 'BLOCKED', 'PASS_DECLARED_RESUME_CHECKS_ONLY',
                          'PASS_DECLARED_RESUME_CHECKS_ONLY', 'BLOCKED'])
        self.assertEqual(len({c['frozen_requirements_sha256'] for c in cases[:3]}), 1)
        self.assertTrue(all(c['byte_restore'] == 'PASS_BYTES_ONLY' for c in cases))
        self.assertTrue(all(c['actual_resume_check']['complete_project_recovery'] == 'UNVERIFIED'
                            for c in cases))

    def test_missing_or_wrong_requirement_anchor_blocks_before_byte_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requirements = root / 'requirements.json'
            requirements.write_bytes(b'{}')
            for path, sha in [(requirements, '0' * 64), (root / 'missing.json', 'a' * 64)]:
                result = check(root / 'not-a-checkpoint', 'a' * 64, path, sha)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertEqual(result['byte_gate'], 'NOT_RUN')
                self.assertFalse(result['author_authorization_verified'])
            self.assertEqual(list(root.iterdir()), [requirements])

    def test_cli_cannot_silently_resume_without_frozen_requirements(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(CHECKER), directory,
                                     '--expected-manifest-sha256', 'a' * 64],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('--requirements', result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
