"""Replay the real editorial decision path with unfamiliar synthetic passages.

The first pass has the same model, material and output cap in both arms.
Downstream repair is intercepted so this measures discovery and stopping.
"""

import argparse
import concurrent.futures
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess


SOURCE = """This constructed example compares available actions at time zero.
Market closes at time zero. The next session could open high or low. The desk
cannot know that opening price at time zero; it can submit an unconditional
order, or an order contingent on an observable price after reopening. The
actions have different timing and fill risks. No empirical profitability or
execution-rate evidence is supplied."""

CASE_A = """# When the choice is made

The book reconstructs a historical path. At Monday's close the desk had to choose a single unconditional position. On Tuesday the price fell to 70, giving a purchase an eventual gain of 30 on an exit at 100.

Because Tuesday opened at 70, the desk should already have committed to this exact entry at Monday's close. The later gain of 30 proves that the desk owned an actionable advantage before Tuesday's price was observable.

The subtraction is straightforward: 100 minus 70 is 30. Treat the same calculation as proof of a repeatable advantage in the next session."""

CASE_B = """# When the choice is made

At Monday's close the desk does not know whether Tuesday will open high or low. An unconditional purchase and an order that becomes eligible only after a specified price is observable are different actions. A contingent order also may not fill.

On one reconstructed path, entry at 70 and exit at 100 would produce a gross difference of 30. That arithmetic describes the path. It supplies neither the probability of the path nor evidence that the contingent order could be filled at 70.

For a new session, write down which information is observable when the decision is made, whether the order can fill and how costs change the comparison. If those inputs are unavailable, the example supports no claim about an actionable advantage."""

EXPECTED = {"A": {"must_locate_paragraph": 3, "error": "realized price used as prior information"},
            "B": {"required_revisions": 0, "comment": "no seeded material defect"}}


class RevisionBoundary(Exception):
    pass


def run_case(repo, out, label, case, model_name, cap):
    out.mkdir()
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    spec = importlib.util.spec_from_file_location("trial_" + label, repo / "deepwrite/tools/writing_loop_experimental.py")
    writer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(writer)
    work = writer.WritingLoop.__new__(writer.WritingLoop)
    work.root = out
    work.config = {"max_revision_rounds": 1, "guard": "on", "chapters": [],
                   "sources": [{"path": "sources/native_001.md"}], "reader_prior_knowledge_contract": {}}
    work.state = {"files": {}, "completed": {}}
    work.guard = writer.module("trial_closeout_" + label,
                               repo / "deepwrite/candidates/e15-review-closure/review_closure_guard.py")
    work.editorial_stop_guard = writer.module("trial_gate_" + label, repo / "deepwrite/tools/editorial_stop_gate.py")
    work.event = lambda *args, **kwargs: None
    work.reader_review = lambda *args, **kwargs: ({}, {"status": "MODEL_INTERNAL_REVIEW_RECORDED"})
    work.reader_findings = lambda *args, **kwargs: []
    work.write("sources/native_001.md", SOURCE)
    work.write("chapters/sample.md", CASE_A if case == "A" else CASE_B)
    live = writer.CodexExec(model_name, timeout=300)
    responses = []

    def call(key, role, payload):
        if role not in {"review", "editorial_confirmation"}:
            raise RevisionBoundary(role)
        # Both arms receive the exact same frozen source and artifact. The only
        # first-pass variation is the checked-out runner's question/constraints.
        payload = {**payload, "source_evidence": {"coverage": "FROZEN_PRIMARY_TEXTS",
                                                "texts": {"sources/native_001.md": SOURCE}}}
        instruction = "Use supplied material only. No tools. Return an English JSON object."
        request = {"role": role, "payload": payload}
        work.write(key + ".prompt.json", writer.json_bytes(request))
        result = live.generate(instruction, json.dumps(request, ensure_ascii=False), cap)
        raw = asdict(result)
        work.write(key + ".model.json", writer.json_bytes(raw))
        responses.append({"role": role, "usage": result.usage, "id": result.response_id})
        return raw

    work.call = call
    reason = ""
    try:
        work.review_cycle("sample", {"sample": "chapters/sample.md"})
        outcome = "KEEP"
    except RevisionBoundary:
        outcome = "REVISE_REQUESTED"
    except Exception as error:
        outcome, reason = "HOLD", str(error)
    result = {"commit": commit, "case": case, "run": label, "model": model_name,
              "output_cap": cap, "outcome": outcome, "reason": reason, "model_calls": responses}
    work.write("RESULT.json", writer.json_bytes(result))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    (args.output / "EXPECTED_PRIVATE_TO_ASSESSOR.json").write_text(json.dumps(EXPECTED, indent=2))
    plan = [(repo, arm + "-" + case + str(index), case)
            for arm, repo in (("before", args.baseline), ("after", args.candidate))
            for case, repeats in (("A", 1), ("B", 2)) for index in range(1, repeats + 1)]
    (args.output / "PLAN.json").write_text(json.dumps({"model": args.model, "cap": 4200,
        "scope": "FIRST_EDITORIAL_PASS_AND_STOP_DECISION", "runs": [item[1] for item in plan],
        "criterion_is_not_passed_to_reviewer": True}, indent=2))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(run_case, repo.resolve(), args.output.resolve() / label, label, case, args.model, 4200)
                for repo, label, case in plan]
        for job in concurrent.futures.as_completed(jobs):
            print(json.dumps(job.result(), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
