"""Exercise the actual one-call writer with the real PR26 gate and scripted models."""
from pathlib import Path
import json
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import test_default as fixture

dw = fixture.dw


class AuditModel(fixture.StudyModel):
    def __init__(self, *, repair=None, force_replan=False, missing_chapter=False, forged_author=False):
        super().__init__(force_replan=force_replan)
        self.repair = repair
        self.missing_chapter = missing_chapter
        self.forged_author = forged_author

    def generate(self, instructions, prompt, max_output_tokens=5000):
        request = json.loads(prompt)
        role, payload = request["role"], request["payload"]
        if role == "master_audit_repair":
            self.roles.append(role)
            text = payload["section"]
            if self.repair == "unchanged":
                text += "\n\n"
            elif self.repair == "short":
                text = "An abbreviated conclusion."
            else:
                text = text.replace("verified by counting two pairs",
                                    "verified by counting two disjoint pairs in the stated sample")
            return self.result({"section_id": payload["section_id"], "section": text})
        if role == "master_audit_repair_recheck":
            self.roles.append(role)
            quote = "two disjoint pairs in the stated sample"
            return self.result({"retention": "PRESERVED", "resolutions": [
                {"id": item["id"], "status": "OPEN" if self.repair == "open" else "CLOSED",
                 "quote": quote, "reason": "The new wording distinguishes overlap from disjoint pairs."}
                for item in payload["issues"]]})
        response = super().generate(instructions, prompt, max_output_tokens)
        data = json.loads(response.text)
        if (role == "master_audit_section" and self.repair
                and payload["section_id"] == "CH01" and payload["phase"] == "initial"):
            data["issues"] = [{"severity": "MAJOR", "section_id": "CH01",
                               "quote": "verified by counting two pairs",
                               "issue": "Specify that counting pairs requires nonoverlapping members.",
                               "test": "Both groups must be described as disjoint in the revised example."}]
        if role == "master_audit_book" and self.missing_chapter:
            data["covered_section_ids"].remove("CH01")
        if role == "master_audit_full_read" and self.forged_author:
            data["author_acceptance"] = "APPROVED"
        response.text = json.dumps(data, ensure_ascii=False)
        return response

    def result(self, value):
        return fixture.SimpleNamespace(model="synthetic-study-model", provider_kind="fixture",
                                       response_id="demo-" + str(len(self.roles)),
                                       text=json.dumps(value, ensure_ascii=False),
                                       usage={"input_tokens": 50, "output_tokens": 50})


class MasterAuditFlow(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture.DefaultInvocationTests("test_one_command_autoselects_all_gates_to_actual_book")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.addCleanup(self.fixture.tearDown)
        self.project = self.fixture.destination
        self.evidence = self.project / "discovery_evidence"
        self.audit = self.evidence / "master_audit"

    def write_book(self, model):
        return dw.run(self.fixture.request, self.project, research_model=model,
                      writer_model=fixture.writer_test.ScriptedModel())

    def resume(self, model):
        sha = dw.sha((self.project / "writer_project/run_state.json").read_bytes())
        return dw.resume(self.project, sha, research_model=model,
                         writer_model=fixture.writer_test.ScriptedModel())

    def test_keep_real_gate_final_read_and_status_resume_agree(self):
        model = AuditModel()
        result = self.write_book(model)
        report = result["master_audit"]
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertEqual(report["selected_writer"], "writer_project")
        self.assertEqual(report["mechanical_evidence"], "SOURCE_RECEIPTS_COMPLETE_SCOPED")
        self.assertEqual(report["author_acceptance"], "NOT_RUN")
        self.assertEqual(model.roles.count("master_audit_full_read"), 2)
        self.assertEqual(dw.status(self.project)["project_status"], result["status"])
        reviewer = AuditModel()
        self.assertEqual(self.resume(reviewer)["master_audit"], report)
        self.assertEqual(reviewer.roles, [])

    def test_replan_rebinds_to_actual_derived_manifest_and_rejects_old_bytes(self):
        result = self.write_book(AuditModel(force_replan=True))
        report = result["master_audit"]
        primary = self.project / "writer_project/book.md"
        derived = self.project / "writer_project_topology_r2/book.md"
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertEqual(report["selected_writer"], "writer_project_topology_r2")
        self.assertEqual(report["final_book_sha256"], dw.sha(derived.read_bytes()))
        self.assertNotEqual(report["final_book_sha256"], dw.sha(primary.read_bytes()))
        data = json.loads((self.audit / "final/SEMANTIC_LEDGER.json").read_text())
        self.assertEqual(list(data["sections"]), ["CH01", "CH02", "FRONT", "TAIL"])
        (self.audit / "final/book.md").write_bytes(primary.read_bytes())
        self.assertEqual(dw.status(self.project)["project_status"], "BLOCKED_MASTER_AUDIT")
        self.assertEqual(self.resume(AuditModel())["status"], "BLOCKED_MASTER_AUDIT")

    def test_major_repair_produces_full_derivative_recheck_and_fresh_read(self):
        reviewer = AuditModel(repair="real")
        result = self.write_book(reviewer)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        audit = result["master_audit"]
        self.assertEqual(len(audit["repaired_major_issues"]), 1)
        self.assertIn("master_audit_repair_recheck", reviewer.roles)
        self.assertEqual(reviewer.roles.count("master_audit_full_read"), 2)
        original = self.project / "writer_project/book.md"
        revised = Path(audit["final_book"])
        self.assertIn("two disjoint pairs", revised.read_text())
        self.assertNotIn("two disjoint pairs", original.read_text())
        self.assertNotEqual(audit["selected_book_sha256"], audit["final_book_sha256"])
        initial_receipt = (self.audit / "initial/RECEIPTS.json").read_bytes()
        (self.audit / "final/RECEIPTS.json").write_bytes(initial_receipt)
        self.assertEqual(dw.status(self.project)["project_status"], "BLOCKED_MASTER_AUDIT")
        self.assertEqual(self.resume(AuditModel())["status"], "BLOCKED_MASTER_AUDIT")

    def test_unresolved_major_stays_blocked_after_summary_is_forged(self):
        result = self.write_book(AuditModel(repair="open"))
        self.assertEqual(result["status"], "BLOCKED_MASTER_AUDIT", result)
        self.assertIn("MAJOR_ISSUE_STILL_OPEN", result["master_audit"]["reason"])
        (self.evidence / "RESULT.json").write_bytes(dw.canonical({"status": "CANDIDATE_PENDING_AUTHOR",
                                                                  "author_acceptance": "APPROVED"}))
        status = dw.status(self.project)
        self.assertEqual(status["project_status"], "BLOCKED_MASTER_AUDIT")
        self.assertEqual(status["author_acceptance"], "NOT_RUN")
        reviewer = AuditModel(repair="real")
        self.assertEqual(self.resume(reviewer)["status"], "BLOCKED_MASTER_AUDIT")
        self.assertEqual(reviewer.roles, [])

    def test_truncation_triggers_retention_hold_not_a_quality_comparison(self):
        result = self.write_book(AuditModel(repair="short"))
        self.assertEqual(result["status"], "BLOCKED_MASTER_AUDIT", result)
        self.assertIn("CONTENT_RETENTION_REVIEW_REQUIRED", result["master_audit"]["reason"])
        self.assertEqual(result["master_audit"]["book_quality"], "UNVERIFIED")
        self.assertFalse((self.audit / "revised/book.md").exists())

    def test_frozen_sequential_baseline_flags_batch_truncation_without_claiming_quality(self):
        baseline = self.fixture.base / "sequential.md"
        baseline.write_text("# Sequential reference fixture\n\n" + "\n".join(
            f"Worked counterexample {i} keeps the two groups separate before measuring." for i in range(25)))
        self.fixture.data["sequential_baseline"] = {"path": str(baseline),
                                                    "sha256": dw.sha(baseline.read_bytes())}
        self.fixture.save_request()
        reviewer = AuditModel()
        result = self.write_book(reviewer)
        self.assertEqual(result["status"], "BLOCKED_MASTER_AUDIT")
        self.assertIn("BLACKBOX_SEQUENTIAL_LENGTH_ANOMALY", result["master_audit"]["reason"])
        self.assertEqual(result["master_audit"]["book_quality"], "UNVERIFIED")
        self.assertNotIn("master_audit_full_read", reviewer.roles)
        self.assertEqual(dw.status(self.project)["project_status"], "BLOCKED_MASTER_AUDIT")

    def test_missing_chapter_and_forged_acceptance_fail_in_actual_chain(self):
        result = self.write_book(AuditModel(missing_chapter=True))
        self.assertEqual(result["status"], "BLOCKED_MASTER_AUDIT", result)
        self.assertIn("BOOK_COVERAGE_MISSING", result["master_audit"]["reason"])
        self.assertEqual(dw.status(self.project)["project_status"], "BLOCKED_MASTER_AUDIT")
        self.project = self.fixture.base / "author_forgery"
        forged = self.write_book(AuditModel(forged_author=True))
        self.assertEqual(forged["status"], "BLOCKED_MASTER_AUDIT")
        self.assertIn("MODEL_CANNOT_SIGN_AUTHOR", forged["master_audit"]["reason"])
        self.assertEqual(forged["author_acceptance"], "NOT_RUN")

    def test_interruption_after_durable_reply_resumes_unread_work_only(self):
        audit = dw.master_audit_module()
        atomic = audit.atomic

        def interrupted(path, value):
            atomic(path, value)
            if path.name == "00002.reply.json":
                raise KeyboardInterrupt

        with patch.object(dw, "master_audit_module", return_value=audit), patch.object(audit, "atomic", interrupted):
            with self.assertRaises(KeyboardInterrupt):
                self.write_book(AuditModel())
        path = self.audit / "calls/00002.reply.json"
        original = path.read_bytes()
        self.assertEqual(dw.status(self.project)["project_status"], "AWAIT_MASTER_AUDIT")
        reviewer = AuditModel()
        result = self.resume(reviewer)
        self.assertEqual(result["status"], "ENGINEERING_FIXTURE_ONLY_NOT_LIVE", result)
        self.assertEqual(reviewer.roles.count("master_audit_section"), 1)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(dw.status(self.project)["project_status"], result["status"])

    def test_missing_response_is_not_recreated_after_commit(self):
        self.write_book(AuditModel())
        (self.audit / "calls/00006.reply.json").unlink()
        self.assertNotIn(dw.status(self.project)["project_status"],
                         ["CANDIDATE_PENDING_AUTHOR", "ENGINEERING_FIXTURE_ONLY_NOT_LIVE"])
        reviewer = AuditModel()
        self.assertEqual(self.resume(reviewer)["status"], "BLOCKED_MASTER_AUDIT")
        self.assertEqual(reviewer.roles, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
