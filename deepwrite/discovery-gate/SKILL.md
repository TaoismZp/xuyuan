---
name: deepwrite-discovery-gate
version: v0.2-proposed
status: PROPOSED_NOT_ACTIVE
purpose: Discover and test valuable explanatory ideas before book/essay drafting.
---

# Discovery Gate | Agent operating skill (candidate)

## Trigger

Use before building a book outline, or when an existing piece is accurate and well edited but adds little insight. For new material, begin from source text and problem only. **Do not retrieve the user's historical style, projects or previously favored theses during the first idea generation pass.** If the executor has already read past drafts, record `CLEAN_ROOM_CONTAMINATED`; do not imply true independence.

## Required outputs

1. A contradiction pool of at least six independently different unresolved facts/tensions; label each as actual sourced observation, hypothetical, or open question.
2. Two or more contradiction branches with three **causally distinct** rival mechanisms apiece, each predicting a different observable result under a stated condition.
3. For each candidate: falsifier; scope; documented prior art; evidence status; decision before/after on the same information; decision test with conditional reversibility.
4. A kill-or-keep decision for each candidate (`REJECT`, `HOLD_RESEARCH`, `APPLICATION_VALUE_CANDIDATE`, or `HUMAN_TEST_REQUIRED`). Never label a theory academically original without supporting independent literature review.
5. The machine structural-validation report and its failure list, tied to the input hash.
6. A recovery checkpoint with original source SHA, any exposed prior context, one next executable action, and exact author/external review gates.

## Execution

Read `PROPOSAL_v0.2.md`, then `REVIEW_PROTOCOL_v0.2.md`. Author candidate cards in private JSON. Run `python3 discovery_gate.py private_cards.json --report validation.json`. For testing this skill use `python3 -m unittest discover -s . -p 'test_discovery_gate.py' -v`.

**Warning**: `PASS_STRUCTURAL` means fields exist and a few list checks passed. It does NOT mean meaningful novelty, semantic distinction, real-world truth, quality, or reviewer agreement. The executor must actually research rivals, seek counterevidence, and preserve source scope before any book-building claim.

## Blocking rules

- If no strong candidate survives, return `STOP_WORK_NO_BOOK`, not a 50,000-word manuscript.
- Prior art found: downgrade scholarly originality, not necessarily the reader's application value.
- No real independent blind readers: keep `HUMAN_REVIEW_NOT_RUN`.
- A/B not equally resourced and isolated: keep `FAIR_AB_NOT_RUN`.
- No permission or private destination for unpublished manuscripts: keep private data out of public repos.
- Never silently change DeepWrite `CURRENT.json`. This is a candidate until separately approved and verified.
