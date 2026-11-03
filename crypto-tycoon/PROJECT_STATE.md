# Crypto Tycoon — Durable Project State

status: ACTIVE
updated_at: 2026-11-03T04:07:00Z
protocol: wish-delivery/versions/v7.7.md
current_gate: Game Feel Vertical Slice / Comparative Experience
candidate: candidate-v12
locked_technical_baseline: candidate-v11
accepted_product_checkpoint: fa63ff673641b8947f118df359564366e6ea3c0d
public_acceptance_checkpoint: b5e51d2559d22bd03ee2e4934a392bef599d8ea6
controlling_blueprint: crypto-tycoon/BUILD_BLUEPRINT_V6.md
controlling_benchmark: crypto-tycoon/GAME_FEEL_BENCHMARK.md
prior_acceptance_report: wish-delivery/runs/2026-11-03-crypto-tycoon-v11-acceptance.md
stable_public_url: https://taoismzp.github.io/xuyuan/crypto-tycoon/
stable_public_status: candidate-v11 technical baseline remains live while candidate-v12 is under experience production; do not replace stable root before v12 comparative acceptance.
last_good_checkpoint: candidate-v11 remains the locked functional/visual/mobile/public baseline. Its exact public Delivery Surface passed byte identity, desktop Chromium, iPhone-class real touch, and WebKit/Safari. User review on 2026-11-03 correctly identified that the former acceptance contract omitted market benchmarking, animation/game feel, sound design, audiovisual feedback hierarchy, event presentation and commercial-product polish. Under v7.7, that v11 result is therefore reclassified as an accepted playable technical baseline, not a finished commercial game.
current_work_checkpoint: candidate-v12 game-feel layer created on top of immutable v11, adding semantic Web Audio cues, ambience, roll anticipation, dice/movement/landing feedback, positive/negative bursts, market-regime audiovisual response, animated decision presentation, mute control and reduced-motion support. Game-feel verification is active; run 41575794307 exposed a slow-baseline initialization race and was fixed in commit 1d21ad9112271fe26a9a6f074dbcf6c8db96fde0. Run 41576087709 is the current verification run.
open_blocker: none
next_executable_action: close candidate-v12 Game Feel verification to terminal; inspect evidence rather than only CI status; then perform benchmark-relative review of the first dice-roll + SOL-purchase loop against MONOPOLY GO / Richman 11 feedback grammar. If the slice still reads as a technical demo, STOP-WORK and improve the feel slice before expanding to rent, airdrop, liquidation, market-regime and end-game event families.
user_blocker: none

## Resume Rule
If status is ACTIVE / INTERRUPTED / BLOCKED_TECH, do not stop at a status report. Validate the locked baseline and current_work_checkpoint, then execute next_executable_action in the same active turn unless a genuine user authorization/external blocker exists.

## External Process Closure Rule
Queued / in_progress / deployment-started / workflow-triggered are never terminal states and never justify ending an active execution turn by themselves. If an external process can be polled in the current turn, continue polling and doing useful adjacent work until it reaches success, explicit failure, or a genuine authorization/external blocker. A triggered CI run is an intermediate action, not delivery. If failure occurs, inspect the concrete failing step/log, fix or change strategy, and continue from the same durable checkpoint.

## Monitor Independence Rule
A monitor must not invalidate a product merely because its own screenshot/probe mechanism fails. Functional, visual, delivery, performance, experience and evidence-capture failures are classified separately. Evidence tooling should be simpler than the product and must not become the production bottleneck.

## Final Gate Chain v7.7
Market Benchmark PASS → visual/art baseline PASS → Functional Reality PASS → Game Feel Vertical Slice PASS → Experience Reality PASS → Comparative Experience PASS → full gameplay/event-family coverage PASS → mobile/performance PASS → exact-build public Delivery Surface PASS → final Acceptance Report → COMPLETE.

## Classification Rule
A functional, visually plausible, mobile-safe, publicly deployed build may still only be a Prototype if its high-frequency interactions lack authored motion, sound, state choreography, reward/failure salience and benchmark-relative product feel. No future acceptance may call such a build a finished commercial game.