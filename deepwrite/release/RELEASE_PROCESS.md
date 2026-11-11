# DeepWrite activation and release rail | E24 candidate

Status: **candidate engineering only / NOT_ACTIVE** until the protected PR is merged; this document does not release a new DeepWrite book-writing version.

## Failure addressed

Previously many real DeepWrite candidates existed (PR #12, PR #13, E18 actual-file writing runner with CI, E23 source-frame preflight), but `deepwrite/CURRENT.json` in main remained v0.1. Researchers sometimes wrote via independent dialogue processes or invoked a candidate directly, so tests could be green while later writing tasks continued with old behavior. The main agent bridge also became stale relative to later E18 development.

**Three separate identities must always be observable:** (1) a candidate exists; (2) it passed engineering/content acceptance; (3) the authoritative stable entry point actually loads it. A Git branch or passing CI is NEVER a release.

## Proposed release policy

- **One stable resolver**: `python3 deepwrite/release/activation.py --root .` reads actual `deepwrite/CURRENT.json`, `wish-delivery/CURRENT.json`, spec, and an optional active runner's exact SHA256 + release-record identity. No model-memory version inference. For v0.1 it truthfully says no autonomous runner. `--run` refuses any old/v0.1 or unpinned experimental runner.
- **One promotion request**: a candidate promotion JSON goes through `release_verify.py` to detect stale base, missing real files, invalid SHA, unverified gates, missing author or independent reader evidence, absent rollback. A structural PASS is **not** a semantic/human proof.
- **One protected activation change**: active pointer, spec, runner, immutable release record and rollback pin are changed **together in a GitHub PR**. Authoritative authorization is real GitHub review or protected environment approval, never a text field `approved: true`. Merge is the switch; subsequent new projects resolve the newly active version.
- **One Reality Gate**: after merge, clone main again, run the resolver, load the active pinned module, perform a real representative run and inspect its finished artifact, not just the README. Existing projects keep their pinned versions; upgrades require explicit migration and replay.
- **One rollback**: restore earlier tested release by new reviewed PR, preserving all book drafts, candidate branches and failing evidence.
- **Engineering-first releases** can land under `deepwrite/release/` without claiming the book-writing engine quality has been independently proven. Enabling a **live stable full-book runner** requires independent real manuscripts, reader evidence and author acceptance; these must not be fabricated.

## Exact observed prerequisites (2026-11-11)

- main DeepWrite current = v0.1 / `automatic_full_book_generation=NOT_IMPLEMENTED`; parent Wish Delivery = v7.6.
- PR #12 and PR #13 remain open, not active.
- E18 runner is substantial implementation with 5 recorded green engineering workflow runs; NOT evidence of live publication quality.
- E23 prewrite gate passed 17 synthetic tests on a public branch and actual private old manuscript negative controls; GitHub Actions E23 passed.
- New resolver+promotion preflight: 12 local synthetic tests PASS; GitHub CI status must be checked separately.
- **Main branch is not currently protected** and repository has `allow_auto_merge=false`. The current available connector cannot update branch protection or repository settings. Consequently GitHub cannot yet guarantee unattended safe auto-promotion; do NOT promise it.
- A reliable future automatic rollout requires owner configuring GitHub branch protection and required checks, and enabling auto-merge; the protected review then permits automatic merge when checks go green. Explicit author approval remains needed for workbench capability promotion until the owner delegates a clear bounded release authority.

## How to avoid repeated candidate purgatory

For every new change, its pull request must include a `release_intent`:
`ENGINEERING_ONLY` (safe underlying infrastructure; stable pointer unchanged);
`CANDIDATE_ONLY` (parallel or SHADOW only);
`PROMOTE_WORKBENCH` (requires all gates, release record, PR authorization, active pointer, post-merge Reality Gate).
It must end as `MERGED_AND_ACTIVE`, `MERGED_INFRA_ONLY`, `CANDIDATE_HOLD`, or `REJECTED`—never ambiguously “iterated”.

*This mechanism cannot force a plain ChatGPT conversation to execute external repository code without a connected capable runtime. A genuine CLI/Work or Codex execution must invoke the launcher. A ChatGPT-only writing task should read CURRENT and state honestly which implementation is or is not executable.*
