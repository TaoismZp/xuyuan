# Post-book master-audit integration spike (candidate only)

**Not active; not a DeepWrite v0.3.1 release. No model or human quality certification.**

This is a reversible, public-only code experiment based on the unmerged `deepwrite-master-audit-gate-20261120` branch (PR #26). It must not contain private manuscripts, source read receipts, or user evaluations.

## Why this exists

The formal writer currently performs E18 chapter adversarial reviews, a cross-chapter review, a full-book recheck, packages `writer_project/book.md`, and may return `CANDIDATE_PENDING_HUMAN`. `deepwrite/deepwrite.py:finalize_execution` then performs a separate bookwide topology KEEP/REPLAN check. Neither step currently requires the new byte-contiguous PR #26 audit evidence. Merely adding `audit_gate.py` and an agent policy does not wire the released engine.

`master_audit_closure.py` is a **candidate validator**. It binds the selected book SHA-256 to the E18 run/config SHA, topology KEEP/REPLAN selection, audited chunk receipts, chapter semantics, issue resolution, final version read report, and still returns `ENGINEERING_EVIDENCE_PASS_BOOK_QUALITY_UNVERIFIED`. It invokes the PR #26 audit CLI. It does not generate actual read receipts or verify that a model understood a manuscript.

## Experiment command

```bash
python3 -B deepwrite/candidates/master-audit-integration/master_audit_closure.py \
  --project /private/isolated-book-project \
  --bundle /private/isolated-audit-bundle \
  --audit-gate deepwrite/master-audit/audit_gate.py

python3 -m unittest discover \
  -s deepwrite/candidates/master-audit-integration \
  -p 'test_master_audit_closure.py' -v
```

The 11 included regressions use a **mock PR #26 gate** and a toy synthetic book, not a real model, not the actual audit backend. Local Python 3 tests on 2026-11-20: 11/11 passed. GitHub CI, actual PR #26 gate integration, end-to-end model execution, and reader testing are still pending.

## Integration seam (not yet wired)

1. Keep E18 per-chapter review, G6 `review_cycle(cross)`, G7 `review_cycle(full_book_recheck)`, and `package`. Treat E18's status as an internal draft candidate, not external author-ready completion.
2. Keep `run_bounded_bookwide_topology_check` in `finalize_execution`; bind actual selected original/derived `book.md`. Note the current topology prompt uses `book[:230000]`, so it cannot prove complete reading of a longer book.
3. After topology, orchestrate source-full-read/chapter-semantic/cross-chapter issue cluster repairs and final full sequential read. Make the validator fail closed on the final source blob.
4. Wire the identical requirement into `run`, `resume`, and `status`, and into a newly versioned release manifest. Do not edit integrity-bound main v0.3.1 code in place. Synthetic tests are not human quality PASS.

## Open negative checks

- Explicitly pin the expected PR #26 gate module byte identity in the future release, rather than accepting a caller-provided executable without governance.
- Verify actual gate CLI with real manuscript-bound receipt fixtures and strong semantic coverage. Reject false-pass audit wrappers.
- Audit REPLAN derived `writer_project_topology_r2/manifest.json` separately; this spike currently checks section count against the original manifest and must not be accepted as complete REPLAN support.
- Handle large books via genuine bounded batches (usually 3 full chapters / ~10–20 chunks), clear downsizing reasons, and model/context evidence, rather than assuming one huge prompt read everything.
- Formalize stop/loop budget, stable issue cluster IDs, content retention and full revised chapter author delivery. Do not reuse prior full-read PASS after any book-byte change.
- Preserve ASSISTED_AUTHOR_GATED sample stop, external author signatures, privacy checks and real human reader trials.

**Gate:** no promotion to STABLE or PR merge merely because this spike exists.
