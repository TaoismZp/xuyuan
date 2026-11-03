# Crypto Tycoon — Durable Project State

status: ACTIVE
updated_at: 2026-11-03T02:22:00Z
protocol: wish-delivery/versions/v7.6.md
current_gate: Stage-2 Minimal Interactive Slice
candidate: candidate-v9 (Stage-1 accepted); next candidate candidate-v10
candidate_checkpoint: 7653246073b6645c164ef5bacdedf3724cdc3460
controlling_blueprint: crypto-tycoon/BUILD_BLUEPRINT_V5.md
last_good_checkpoint: Stage-1 Visual Vertical Slice accepted in SUPERVISION_REPORT_V9.md; exact-build desktop+iPad evidence from run 41565133323, artifact 13198509369, digest sha256:cb129e919dca7e64c4f56da8b4580e7dccf7a91e74f6d249a1d4d78b35141d73
open_blocker: Stage-2 interaction has not yet been built and independently accepted
next_executable_action: build candidate-v10 on top of candidate-v9 with a real minimal interaction loop: roll input + dice animation/state + human token movement on the same 24-tile loop + one buy/pass decision mutating serializable state + one bot turn + one market-regime transition + HUD synchronization; create a dedicated exact-build Stage-2 test and post-interaction CDP visual evidence; write Stage-2 acceptance report only if both functional and visual regression gates pass
user_blocker: none

## Resume Rule
If this project is reopened while status is ACTIVE / INTERRUPTED / BLOCKED_TECH, do not stop at a status report. Validate `last_good_checkpoint`, then execute `next_executable_action` in the same active turn unless a real user authorization/blocker exists.

## Do Not Final
No public handover until Stage-1 visual supervision PASS → Stage-2 interaction PASS → full gameplay integration → mobile/performance PASS → exact-build public Delivery Surface PASS → Acceptance Report.
