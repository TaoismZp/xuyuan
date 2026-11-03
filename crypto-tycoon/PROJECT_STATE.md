# Crypto Tycoon — Durable Project State

status: COMPLETE
updated_at: 2026-11-03T03:34:00Z
protocol: wish-delivery/versions/v7.6.md
current_gate: COMPLETE / ACCEPTED
candidate: candidate-v11
accepted_product_checkpoint: fa63ff673641b8947f118df359564366e6ea3c0d
public_acceptance_checkpoint: b5e51d2559d22bd03ee2e4934a392bef599d8ea6
controlling_blueprint: crypto-tycoon/BUILD_BLUEPRINT_V5.md
acceptance_report: wish-delivery/runs/2026-11-03-crypto-tycoon-v11-acceptance.md
public_url: https://taoismzp.github.io/xuyuan/crypto-tycoon/
last_good_checkpoint: Exact-build public Delivery Surface accepted in GitHub Actions run 41572396271. Public acceptance artifact 13201897629, digest sha256:d32de4c0ddf42a6efa143a2f3c2b45b330598d403facb806d45c1a7864dfeb00. The public index, candidate-v11-game.js and candidate-v11.css were byte-compared against the repository before runtime acceptance. Public SHA-256 values: index 6957ddfcc10e3b89092508cae2e241e05093fe9510bcbb82cc73e68a2ffde13d; game ebccf4f8bc9ee6b18969142b97e7f3333569396aa9fabcb31e7cc365de7c07b4; CSS 484a7fe101aa5e392d46f253050c3092b83bc967eddf102b16aeb822122340aa. The same stable GitHub Pages URL passed desktop Chromium, iPhone-class real touch, and WebKit/Safari-compatible interaction loops with candidate-v11 identity, 24 tiles, four players, SOL purchase, bot turns, round progression, zero horizontal overflow, and no browser or interaction errors.
open_blocker: none
next_executable_action: none — delivery complete. Future changes must start a new candidate/version and may not overwrite this accepted checkpoint without a new acceptance cycle.
user_blocker: none

## Resume Rule
This project is COMPLETE. Do not silently resume construction from this state. Any future requested change creates a new candidate/version from this accepted checkpoint and re-enters the relevant gates.

## External Process Closure Rule
Queued / in_progress / deployment-started / workflow-triggered are never terminal states and never justify ending an active execution turn by themselves. If an external process can be polled in the current turn, continue polling and doing useful adjacent work until it reaches success, explicit failure, or a genuine authorization/external blocker. A triggered CI run is an intermediate action, not delivery. If failure occurs, inspect the concrete failing step/log, fix or change strategy, and continue from the same durable checkpoint.

## Monitor Independence Rule
A monitor must not invalidate a product merely because its own screenshot/probe mechanism fails. Functional, visual, delivery, performance, and evidence-capture failures are classified separately. Evidence tooling should be simpler than the product and must not become the production bottleneck.

## Final Gate Chain
Stage-1 visual supervision PASS → Stage-2 interaction PASS → full gameplay integration PASS → mobile/performance PASS → exact-build public Delivery Surface PASS → Acceptance Report archived → COMPLETE.
