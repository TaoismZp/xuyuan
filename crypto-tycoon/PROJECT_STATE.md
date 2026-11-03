# Crypto Tycoon — Durable Project State

status: ACTIVE
updated_at: 2026-11-03T03:12:00Z
protocol: wish-delivery/versions/v7.6.md
current_gate: Mobile / Performance
candidate: candidate-v11 (Full Gameplay Integration accepted)
candidate_checkpoint: 42c515014576cdf2f5395313d6096b1ac79cf5e7
controlling_blueprint: crypto-tycoon/BUILD_BLUEPRINT_V5.md
last_good_checkpoint: Stage-3 Full Gameplay Integration accepted on desktop+iPad in GitHub Actions run 41570530539. Artifact 13200269452 (crypto-stage3-full-game-v11), digest sha256:924932a68a722397dd45689fab3c7cb2a0cd3c0b7130af4f4be904448440aeea. Both surfaces completed two full four-player rounds and remained playable at round 3. Human bought SOL on tile 5 then Meme on tile 7, cash ended at ¥101,000, ownership persisted across bot turns, portfolio UI reflected both holdings, restart reset positions/cash/owners, and end-state/replay rendered four-player ranking correctly with no interaction errors or horizontal overflow.
open_blocker: none at Stage-3.
next_executable_action: run the candidate-v11 full game through the Mobile / Performance gate: iPhone-class viewport and touch layout, WebKit/Safari-compatible functional smoke, no horizontal overflow, no clipped critical controls, stable restart/decision UI, and an explicit render/performance budget on the production rendering path. Fix only concrete mobile/performance failures; do not redesign accepted Stage-1 visuals or Stage-3 gameplay unless required. After PASS, advance to exact-build public Delivery Surface deployment and verification.
user_blocker: none

## Resume Rule
If this project is reopened while status is ACTIVE / INTERRUPTED / BLOCKED_TECH, do not stop at a status report. Validate `last_good_checkpoint`, then execute `next_executable_action` in the same active turn unless a real user authorization/blocker exists.

## External Process Closure Rule
Queued / in_progress / deployment-started / workflow-triggered are never terminal states and never justify ending an active execution turn by themselves. If an external process can be polled in the current turn, continue polling and doing useful adjacent work until it reaches success, explicit failure, or a genuine authorization/external blocker. A triggered CI run is an intermediate action, not delivery. If failure occurs, inspect the concrete failing step/log, fix or change strategy, and continue from the same durable checkpoint.

## Monitor Independence Rule
A monitor must not invalidate a product merely because its own screenshot/probe mechanism fails. Functional, visual, delivery, performance, and evidence-capture failures are classified separately. Evidence tooling should be simpler than the product and must not become the production bottleneck.

## Do Not Final
No public handover until Stage-1 visual supervision PASS → Stage-2 interaction PASS → full gameplay integration PASS → mobile/performance PASS → exact-build public Delivery Surface PASS → Acceptance Report.
