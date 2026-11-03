# Crypto Tycoon v11 — Final Acceptance Report

Date: 2026-11-03
Protocol: `wish-delivery/versions/v7.6.md`
Repository: `TaoismZp/xuyuan`
Stable public surface: https://taoismzp.github.io/xuyuan/crypto-tycoon/
Accepted runtime identity: `candidate-v11`

## Final Verdict

PASS. The delivered artifact is a real public, playable 3D web game. It is not a screenshot, source-only handoff, localhost build, html-preview surface, stale loader, or planning document.

The stable `/crypto-tycoon/` entry uses the same HTML blob as the accepted `candidate-v11.html`. Public delivery verification additionally compared the deployed `index.html`, `candidate-v11-game.js`, and `candidate-v11.css` byte-for-byte against the repository candidate before browser acceptance was allowed to run.

## Gate Record

### Stage 1 — Visual Supervision

PASS.

Accepted visual candidate: v9 visual world.
Evidence: `crypto-tycoon/SUPERVISION_REPORT_V9.md`.
GitHub Actions run: `41565133323`.
Artifact: `13198509369`.
Artifact digest: `sha256:cb129e919dca7e64c4f56da8b4580e7dccf7a91e74f6d249a1d4d78b35141d73`.

The accepted visual world contains the authored 24-tile raised board, dimensional Chinese hero title, collectible player tokens, large physical dice, eight landmark categories, layered finance-city structures, authored city anchors, controlled lighting, and no reference-image pixel substitution.

### Stage 2 — Minimal Interactive Slice

PASS.

GitHub Actions run: `41569642128`.
Artifact: `13200697515`.
Artifact digest: `sha256:a898dbf469de381b27665949495370c5918ae823f5bdcbfb29168e897bb18a5d`.

Verified deterministic loop on desktop and iPad: roll `[2,3]`, player moves 17→22, buys SOL for ¥12,000, bot moves 10→14, market bull→mania, round 6→7, human cash ¥108,000, net worth ¥169,360, synchronized HUD/history, animation proof present, no interaction error or horizontal overflow.

### Stage 3 — Full Gameplay Integration

PASS.

Accepted candidate: `candidate-v11`.
GitHub Actions run: `41570530539`.
Artifact: `13200269452`.
Artifact digest: `sha256:924932a68a722397dd45689fab3c7cb2a0cd3c0b7130af4f4be904448440aeea`.

Verified on desktop and iPad:
- repeated four-player rounds remain playable;
- 24 tiles and 12 assets across CORE / BETA / INFRA / YIELD;
- buy/pass, owned-asset add/hold, rent, sector bonus;
- bots and market/event progression;
- bull/bear/airdrop/halving/vault/mine/liquidation events;
- forced liquidation / exit;
- 12-round end state, ranking, restart/replay;
- portfolio state and HUD stay synchronized.

Acceptance loop retained human SOL + Meme ownership across bot turns and advanced into round 3 with cash ¥101,000. Portfolio, restart, four-player settlement, and replay all passed.

### Mobile / Performance

PASS.

GitHub Actions run: `41571669131`.
Chrome iPhone artifact: `13201593033`.
Digest: `sha256:869bf9c4d6e5092aa85231b57df3407790694ad70325dfa66012f26c85a9fc53`.
WebKit/Safari artifact: `13201527786`.
Digest: `sha256:c08346ce68a7cab37e251e15cedfe11830f446496adfcdc34d1f62a8c878e72f`.

Production iPhone audit at 393×852, device DPR 2:
- internal render ratio ≈ 1.65;
- 882 visible meshes;
- 229,242 triangles;
- 40 visible lights;
- zero horizontal overflow;
- four 44×44 side controls;
- 48px decision controls.

Real touchscreen input completed the roll → SOL buy → bot turns → round 2 loop. WebKit iPhone smoke completed the same loop with WebGL available and no browser or interaction errors.

### Exact-Build Public Delivery Surface

PASS.

Stable public URL: https://taoismzp.github.io/xuyuan/crypto-tycoon/
Pages deployment run promoting the stable v11 entry: `41572318173` — SUCCESS.
Final exact-build public acceptance run: `41572396271` — SUCCESS.
Public acceptance artifact: `13201897629`.
Artifact digest: `sha256:d32de4c0ddf42a6efa143a2f3c2b45b330598d403facb806d45c1a7864dfeb00`.

Public byte identity proven before runtime verification:
- `index.html` SHA-256: `6957ddfcc10e3b89092508cae2e241e05093fe9510bcbb82cc73e68a2ffde13d`
- `candidate-v11-game.js` SHA-256: `ebccf4f8bc9ee6b18969142b97e7f3333569396aa9fabcb31e7cc365de7c07b4`
- `candidate-v11.css` SHA-256: `484a7fe101aa5e392d46f253050c3092b83bc967eddf102b16aeb822122340aa`

The real GitHub Pages URL then passed:
- desktop Chromium full first-round loop;
- iPhone-class real touch roll + SOL buy + bot turns + round 2;
- WebKit/Safari-compatible iPhone loop;
- 24-tile / four-player / `candidate-v11` identity checks;
- no reference-pixel substitution;
- no horizontal overflow;
- no browser or interaction errors.

## Important Delivery Lessons Locked Back Into Wish Delivery

1. An external process in `queued`, `in_progress`, `deployment-started`, or `workflow-triggered` state is never a terminal delivery state.
2. Monitoring failure and product failure are separate classes; the monitor must not become the production bottleneck.
3. Every acceptance gate must verify the same immutable artifact identity; a stale loader or wrong public entry invalidates Delivery Reality even when CI is green.
4. Visual work starts from production bottleneck and perceptual convergence, not from adding engineering complexity around a weak visual slice.
5. Long tasks require durable repository checkpoints so a chat/request timeout resumes from the last verified state rather than restarting or silently terminating.

## Final Artifact

Public playable game: https://taoismzp.github.io/xuyuan/crypto-tycoon/

Final status: ACCEPTED / DELIVERED.
