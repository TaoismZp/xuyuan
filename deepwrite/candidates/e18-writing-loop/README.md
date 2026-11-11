# E18 experimental writing runner — candidate only

This is reviewable implementation, not evidence of a completed live book experiment. No CURRENT, public bridge state or old manuscript is written by the runner. Private materials and responses belong in a caller-owned private project directory outside this repository.

## What is reused

- RESEARCH_LOOP.md and EDITORIAL_LOOP.md are copied unchanged from PR #12 commit e5a1c9f0b057f5483022bd196a53790e905b0896.
- book_packager_v0.1.py is the exact safer PR #12 source from that commit. It validates real source files, SHA and byte counts and refuses source/destination collisions.
- The existing Responses adapter remains the transport, with additive payload-only response logging (never credentials or authorization headers). It does not become a new model SDK.
- The CLI wrapper calls the existing discovery-gate/execute_codex_cli.py parse_events for one fresh turn. That old discovery-card executor is not presented as a book runner.
- qa/checkpoint.py and qa/resume_check.py provide byte snapshots, no-clobber restore and declared-policy checks.
- The repaired E15 review_closure_guard.check(record, root, expected_findings) is required. This branch is based on 163fef5; integration must bring the repaired guard from c3b2d621d94edabf19917dff2c49ba57d694a9f0. Do not run against the old PR #13 implementation.

## Actual behavior

The runner performs research, direction selection, complete chapter drafting, located review, complete revised chapter output for open findings, frozen-finding recheck, cross-chapter review/rewrite, front/back matter, assembly and checkpointing. It never edits a draft in place. It writes actual before/after files and unified diffs.

The process owns artifact inventories, paths, baseline hashes and frozen finding identities. The model supplies content, findings and paragraph references. It cannot replace the frozen issue/assertion/severity with its recheck answer. New unresolved major findings cannot be dropped just by changing CLOSED text. At least one located finding or justified KEEP is required per artifact. KEEP permits preserving correct prose.

Before assembly the guard-on arm also reexecutes every previously CLOSED/KEEP computable assertion against the final chapter bytes. A later chapter revision that invalidates a prior model-review artifact SHA is held for an explicit located reread; this initial implementation deliberately does not silently transfer that semantic judgment. Newly discovered MAJOR/CRITICAL recheck findings are saved in new_findings records and put the run on HOLD rather than being discarded from a fixed finding inventory.

Guard on rejects unchanged or whitespace-only fake fixes for CLOSED, reads the actual artifacts and reexecutes the supported literal assertion. Model review is still a model's located judgment; its verdict is bound to actual candidate bytes and saved as MODEL_REVIEW_REQUIRED. It is not proof of thought quality, truth, style or human acceptance. Unexpected protocol output, unavailable usage, missing identity, tool events and unresolved findings fail closed, leaving the evidence.

Guard off retains the ordinary review/rewrite prompts but bypasses the repaired closeout checker. It exists to isolate the guard's engineering effect. This switch does not establish that the whole B0/B1 experiment is fair, blinded, sufficiently budgeted or independent.

## Use and pins

Prepare an empty private project directory containing only sources/. Supply exact SHA256 for every source. Keep the config outside the project at first, and pin both formal protocol versions and every enabled candidate by exact Git commit. Existing checkpoints validate pin syntax and matching values; they do not query GitHub to authenticate the pins.

The configuration keys are:

- project_id, model, working_title, wish
- adapter: responses or codex (fixture requires explicit Python injection and never runs through the live CLI)
- guard: on or off
- token_budget, per_call_output_tokens, max_revision_rounds: positive integers
- chapters: ordered objects with artifact_id (letters/digits/underscore/hyphen) and title
- sources: relative path plus sha256; source bytes are frozen
- pins: project_id, protocols.deepwrite and protocols.wish_delivery (version, 40-hex commit, 40-hex spec_sha), channel and modules objects containing id/commit
- channel: CANDIDATE_OPT_IN or SHADOW
- module_policy: module ID to CANDIDATE/STABLE
- modules: module ID to Boolean
- module_commits: every enabled candidate ID to 40-hex commit

Use an explicit provider-supported model name. Do not put secrets in config, source paths or chat. Responses reads OPENAI_API_KEY from the environment. Codex uses the installed CLI's login. Authentication failure is BLOCKED_MODEL_AUTH; it never becomes a scripted live run.

~~~bash
python deepwrite/tools/writing_loop_experimental.py /private/e18-config.json /private/e18-b1
~~~

Cached-call reuse requires a state-anchored completion record binding the actual request, response and transport hashes together. A crash between response and transport persistence is an uncertain incomplete call: no cache acceptance and no automatic re-send.

Each model call stores its request, model/provider response identity, text, usage and available transport payload in calls/. Tokens are charged from actual input_tokens + output_tokens. Output caps are sent to Responses; Codex caps are post hoc only. Unknown usage blocks the run, rather than recording a convenient zero. The provider can consume tokens before an overrun is detected. No accepted run may exceed the configured accounted total; this is not a provider-side hard total spending guarantee.

CLI identity is the requested model flag plus CLI event/thread identity, not independent server attestation. An empty working directory, ephemeral turns and tool-event rejection do not establish OS-level isolation from author answers or the A baseline. Strict B0/B1 fairness stays UNVERIFIED until a separate controlled execution supplies evidence.

## Frozen manuscript replay

For an already identified defect in an existing private manuscript (such as the E12 replay), set run_mode to replay_frozen_drafts. Supply replay_drafts as an exact artifact-ID-to-path map; every path must already be a hash-pinned source. The runner copies actual source bytes to an immutable draft, skips fresh research/drafting, and then uses the same review/rewrite/recheck/cross-review/assembly/checkpoint loop. Optional known_findings are caller-owned frozen finding objects (id, artifact_id, kind, severity, OPEN/KEEP status, issue, evidence, paragraph and assertion where computable); model output cannot override their ids. The code resolves actual paragraph hashes from the real baseline. This is FROZEN_BASELINE_REPLAY_NOT_FRESH_B0_B1, never evidence of a new book written from scratch. Fresh mode rejects these replay inputs.

## Pause, resume, restore and rollback

The final receipt provides external state/manifest/requirements SHA256. Save this receipt outside the mutable project. A caller-approved early pause is available with --stop-after N. Resume requires the external SHA and verifies every tracked file before reusing saved responses:

~~~bash
python deepwrite/tools/writing_loop_experimental.py /private/e18-config.json /private/e18-b1 --expected-state-sha256 EXTERNAL_STATE_SHA256
~~~

A failed or uncertain provider request is never automatically sent again. Investigate billing/response identity before deciding to start a separate run. Do not delete failure files to make a run appear clean.

restore_project(checkpoint_path, new_directory, manifest_sha, requirements_path, requirements_sha) first checks the independently supplied hashes and declared recovery requirements, then calls existing no-clobber restore. The destination must be new. Restored tracked files are verified again on resume. To stop a candidate, preserve its output and restore the earlier declared checkpoint to a new directory/config; no sole original or stable protocol is overwritten.

The snapshot proves only declared files and policy values. It does not prove durable remote retention, authorized completeness or literary quality. The caller must persist the private run/checkpoint and external receipt in the designated private recovery repository; this script has no GitHub publication side effect.

## Engineering verification and unresolved gates

~~~bash
python -m unittest discover -s deepwrite/tools/tests -p 'test_writing_loop_experimental.py' -v
~~~

An actual CI can retain a complete readable synthetic output, responses, diffs and checkpoint with:

~~~bash
python deepwrite/tools/tests/test_writing_loop_experimental.py --fixture-output /tmp/e18-engineering-fixture
~~~

The command prints its receipt path. Archive the fixture directory and sibling receipt/checkpoint/requirements; it is public arithmetic content, not a live author manuscript. An output directory must be new.

All scripted tests are explicit ENGINEERING_FIXTURE_ONLY, use public arithmetic text, and make no provider call. They test actual file rewrite/diff, false CLOSED, whitespace fake fixes, correct KEEP, cross-chapter model-review binding, token accounting, unknown usage, identity switches, tool contamination, missing auth, interrupted-call nonrepeat, real snapshot/restore, tamper detection and packaged output SHA. A test suite only counts as PASS after actual CI execution; the source commit alone is not a receipt.

Even a successful live run ends CANDIDATE_PENDING_HUMAN with quality UNVERIFIED, human acceptance NOT_RUN and fair_B0_B1 UNVERIFIED. E1 autonomous whole-book delivery, E2 independent fair full-work reading, original NO FOLD B0/B1 representative chapters, manuscript improvement and author acceptance remain open unless separately evidenced. No existing Sunzi editing achievement is attributed to this runner.
