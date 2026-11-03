# Crypto Tycoon — Durable Project State

status: ACTIVE
updated_at: 2026-11-03T03:04:00Z
protocol: wish-delivery/versions/v7.6.md
current_gate: Full Gameplay Integration
candidate: candidate-v10 (Stage-2 accepted)
candidate_checkpoint: 1c94c189e7dc64a54ba851e92d6ed97e3e3ef235
controlling_blueprint: crypto-tycoon/BUILD_BLUEPRINT_V5.md
last_good_checkpoint: Stage-2 Minimal Interactive Slice accepted on desktop+iPad in GitHub Actions run 41569642128. Artifact 13200697515 (crypto-stage2-acceptance-v10), digest sha256:a898dbf469de381b27665949495370c5918ae823f5bdcbfb29168e897bb18a5d. Both surfaces completed the deterministic loop: roll [2,3], human tile 17→22, buy SOL for ¥12,000, bot tile 10→14, market bull→mania, round 6→7, SOL mark +8%, human cash ¥108,000, net worth ¥169,360, no interaction error and no horizontal overflow.
open_blocker: none at Stage-2. Supplemental post-interaction HUD screenshots can still stall in SwiftShader; this is a supervision-camera limitation, not a functional failure. Functional JSON evidence is authoritative for Stage-2, while Stage-1 remains authoritative for real 3D visual evidence.
next_executable_action: integrate the accepted Stage-2 loop into the fuller playable game rather than expanding demo-only logic. Preserve the accepted v9 visual world and v10 interaction semantics while adding repeated turns, owned-asset persistence, bot turns beyond one deterministic turn, market/event progression, buy/pass outcomes, round/end-state rules, restart/replay, and state/HUD synchronization. Then run desktop+iPad exact-build functional acceptance before mobile/performance and public Delivery Surface gates.
user_blocker: none

## Resume Rule
If this project is reopened while status is ACTIVE / INTERRUPTED / BLOCKED_TECH, do not stop at a status report. Validate `last_good_checkpoint`, then execute `next_executable_action` in the same active turn unless a real user authorization/blocker exists.

## External Process Closure Rule
Queued / in_progress / deployment-started / workflow-triggered are never terminal states and never justify ending an active execution turn by themselves. If an external process can be polled in the current turn, continue polling and doing useful adjacent work until it reaches success, explicit failure, or a genuine authorization/external blocker. A triggered CI run is an intermediate action, not delivery. If failure occurs, inspect the concrete failing step/log, fix or change strategy, and continue from the same durable checkpoint.

## Monitor Independence Rule
A monitor must not invalidate a product merely because its own screenshot/probe mechanism fails. Functional, visual, delivery, performance, and evidence-capture failures are classified separately. Evidence tooling should be simpler than the product and must not become the production bottleneck.

## Do Not Final
No public handover until Stage-1 visual supervision PASS → Stage-2 interaction PASS → full gameplay integration → mobile/performance PASS → exact-build public Delivery Surface PASS → Acceptance Report.
