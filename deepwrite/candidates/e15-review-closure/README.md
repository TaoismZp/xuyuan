# E15 review closeout guard — E18 repair candidate

EXPERIMENTAL, NOT ACTIVE. This repairs the existing PR #13 checker rather than creating a new quality gate. Formal CURRENT files and the collaboration bridge are untouched.

Baseline source: PR #13 at d7dadf80aaef3963d0784787219e2b5e6e12b59f. Its exact checker is preserved only as a regression fixture. Tests reproduce its empty-findings and arbitrary-CLOSED-evidence false passes; the fixture is not a usable release gate.

## Actual contract

API: check(record, root, expected_findings=None). CLI:

    python review_closure_guard.py closeout.json --root PRIVATE_PROJECT \
      --expected-findings frozen-findings.json \
      --expected-findings-sha256 EXTERNALLY_SAVED_SHA256

Schema: deepwrite/review-closeout/v1.

- artifacts is a nonempty list of artifact_id plus baseline/candidate objects containing canonical relative path and raw-byte sha256.
- coverage exactly matches the complete artifact inventory. Every artifact requires a located finding or an evidenced KEEP. An empty findings list does not certify review.
- findings have unique id, artifact_id, kind (computable or model_review), severity, status (OPEN/CLOSED/KEEP), issue, evidence, and location.baseline/location.candidate, each with 1-based paragraph and sha256.
- paragraphs(text) normalizes CRLF/CR to LF, splits at blank lines, and filters whitespace-only segments. The returned paragraph text itself is not trimmed; its UTF-8 SHA is checked.
- computable assertions allow only contains, not_contains, literal_count with value and optional count. evaluate(assertion, text) returns actual count/pass. Checks run over the entire artifact after whitespace removal; no regex/eval/commands are accepted.
- CLOSED needs non-whitespace change to both artifact and located paragraph, baseline assertion failure, actual candidate assertion success, and location/literal association. Changing line breaks, moving the location to an unchanged ending, or altering another chapter cannot close the known literal defect.
- KEEP may retain correct original bytes, including when a major allegation is disproved; it requires a reason and evidence. For computational claims both original and candidate checks must pass.
- model_review CLOSED/KEEP needs review.verdict/reviewer/rationale bound to the actual candidate SHA and paragraph SHA. This records a model review; it NEVER proves reasoning, style, novelty, discovery or human approval.
- expected_findings freezes id, artifact_id, kind, issue, assertion, baseline location and severity floor. The CLI additionally requires its externally retained raw file SHA.

A successful result is still only PASS_STRUCTURAL_ONLY. semantic_status is MODEL_REVIEW_REQUIRED for model records, otherwise NOT_CERTIFIED. human_acceptance and unreported_defect_discovery remain NOT_ESTABLISHED.

## Caller trust boundary

The runner must own/freeze the complete artifact inventory, file identities and initial review findings; never let a revising model substitute paths, shorten the book or redefine the finding. This checker alone cannot know omitted chapters or discover unreported literary weaknesses. Literal checks are deliberately narrow and do not certify removal of every semantic error.

This change is not a live-model runner, an autonomous book, a fair B0/B1 experiment, independent human review or a promotion. The earlier local 31-test variant had a later-discovered static bypass and is not the code tested here. The new remote suite must be judged by its actual GitHub Actions run; no test result is preclaimed.

## Executed remote regression evidence

GitHub Actions [run 42991098335](https://github.com/TaoismZp/xuyuan/actions/runs/42991098335), job 130423898016, tested commit `393df4d23dbb613bc3392fa8d3d75be83ed7938a` on Python 3.12.3: **42 tests ran, OK**. Logs were actually fetched and read. `CI_RECEIPT.json` pins the tested guard/test/legacy blobs. This is new remote engineering evidence, not an inheritance of the interrupted local variant's 31 tests, nor real-model or writing-quality evidence.
