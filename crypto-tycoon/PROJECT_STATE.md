# Crypto Tycoon — Durable Project State

status: ACTIVE
updated_at: 2026-11-03T03:25:00Z
protocol: wish-delivery/versions/v7.6.md
current_gate: Exact-Build Public Delivery Surface
candidate: candidate-v11 (Mobile / Performance accepted)
candidate_checkpoint: fa63ff673641b8947f118df359564366e6ea3c0d
controlling_blueprint: crypto-tycoon/BUILD_BLUEPRINT_V5.md
last_good_checkpoint: Mobile / Performance accepted in GitHub Actions run 41571669131. Chrome iPhone production/touch artifact 13201593033, digest sha256:869bf9c4d6e5092aa85231b57df3407790694ad70325dfa66012f26c85a9fc53; WebKit/Safari artifact 13201527786, digest sha256:c08346ce68a7cab37e251e15cedfe11830f446496adfcdc34d1f62a8c878e72f. Production iPhone viewport 393×852 at device DPR 2 rendered with capped internal ratio ≈1.65, 882 visible meshes, 229,242 triangles, 40 visible lights, zero horizontal overflow, four 44×44 action controls, and 48px decision controls. Real touch input completed the SOL-buy loop into round 2. WebKit iPhone smoke also completed the same loop without browser or interaction errors.
open_blocker: none at Mobile / Performance.
next_executable_action: publish the exact accepted candidate-v11 build to a stable public delivery surface, make it the user-facing Crypto Tycoon entry, verify that the public URL resolves the same candidate identity and runs on desktop+iPhone/iPad-class surfaces, then write the final Acceptance Report. GitHub Pages is preferred if repository Pages is now available; otherwise use an already-authorized stable deployment connector. Do not substitute html-preview, localhost, source files, screenshots, or a stale public loader.
user_blocker: none unless every stable host requires a new user authorization.

## Resume Rule
If this project is reopened while status is ACTIVE / INTERRUPTED / BLOCKED_TECH, do not stop at a status report. Validate `last_good_checkpoint`, then execute `next_executable_action` in the same active turn unless a real user authorization/blocker exists.

## External Process Closure Rule
Queued / in_progress / deployment-started / workflow-triggered are never terminal states and never justify ending an active execution turn by themselves. If an external process can be polled in the current turn, continue polling and doing useful adjacent work until it reaches success, explicit failure, or a genuine authorization/external blocker. A triggered CI run is an intermediate action, not delivery. If failure occurs, inspect the concrete failing step/log, fix or change strategy, and continue from the same durable checkpoint.

## Monitor Independence Rule
A monitor must not invalidate a product merely because its own screenshot/probe mechanism fails. Functional, visual, delivery, performance, and evidence-capture failures are classified separately. Evidence tooling should be simpler than the product and must not become the production bottleneck.

## Do Not Final
No public handover until Stage-1 visual supervision PASS → Stage-2 interaction PASS → full gameplay integration PASS → mobile/performance PASS → exact-build public Delivery Surface PASS → Acceptance Report.
