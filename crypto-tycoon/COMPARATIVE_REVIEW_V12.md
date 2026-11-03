# Crypto Tycoon — Comparative Experience Review v12

Verdict: **FAIL — keep as architecture proof, do not expand across the game.**

Benchmark set: MONOPOLY GO!, Richman 11 / 大富翁11, Coin Master / Board Kings interaction grammar.
Scope reviewed: first dice roll → 5-tile movement → SOL purchase → first market-regime transition.

## Why v12 is useful but not product-grade
v12 proves the technical shell can support a semantic audiovisual layer without breaking the accepted v11 rules engine. The iPad and iPhone acceptance run proves UI press, anticipation cue, dice-rattle cue, dice-impact cue, movement cue, landing cue, purchase cue, positive burst, market-regime cue, sound toggle and the deterministic SOL purchase can coexist.

That is not the same as proving the experience is commercially satisfying.

## Benchmark-relative score — first dice roll
Scale: 0 absent, 1 prototype, 2 credible product, 3 benchmark-class.

| Dimension | v12 | Reason |
|---|---:|---|
| Anticipation | 2.0 | Button press + charge cue exists, but no authored physical dice wind-up or camera composition. |
| Motion quality | 1.4 | Existing v11 dice/token motion remains mostly technical interpolation; not enough weight, collision, overshoot, settle or personality. |
| Impact | 1.8 | Punch/ring/impact cue exists; visual contact does not yet convincingly read as physical impact. |
| Sound layering | 1.3 | Semantic layers exist, but current Web Audio synthesis is a timing prototype, not authored dice/board/material sound design. |
| Result salience | 2.0 | Result leads cleanly to the SOL decision, but the dice result itself is not yet a hero moment. |
| Pacing | 1.9 | Loop is readable and fast; still feels like a web interaction sequence rather than a staged game beat. |
| World reactivity | 1.5 | Board punch, ring and regime cue exist, but characters/landmarks/city do not react enough. |

Average: **1.70 / 3.00 — FAIL** (target >= 2.4, no category < 2).

## Benchmark-relative score — SOL purchase

| Dimension | v12 | Reason |
|---|---:|---|
| Anticipation | 1.5 | Decision modal reveals cleanly but purchase has little pre-commit tension. |
| Motion quality | 1.7 | Modal motion is improved; ownership still appears rather than being visibly constructed/claimed. |
| Impact | 1.9 | Positive flash/particle burst communicates success but lacks asset-specific physicalization. |
| Sound layering | 1.4 | Buy chord exists but lacks coin/cash/ownership/material layers and mix ducking. |
| Result salience | 2.1 | “仓位建立” + cash/owner state is understandable. |
| Pacing | 2.0 | Returns to the board quickly. |
| World reactivity | 1.4 | Tile/landmark/token does not visibly transform enough after ownership changes. |

Average: **1.71 / 3.00 — FAIL**.

## Evidence defects discovered
- The acceptance proof recorded `landingPulses=2` on the first landing. At least one pulse is an initialization/geometric duplicate and must be removed.
- Test-mode 5-tile travel produced only one semantic movement cue. Production geometry sampling can create more, but the experience contract needs deterministic step rhythm rather than relying on frame sampling.
- Positive purchase feedback can also react to Bot purchases through shared toast semantics, so human reward and background Bot activity are not yet cleanly mixed.
- The audio layer is synthesized at runtime; it validates timing and event taxonomy, not final audio quality.

## STOP-WORK decision
Do not expand v12 feedback to rent, airdrop, liquidation, all 24 tiles, or end-game yet.

## Candidate v13 must solve only the hero loop
1. Physical dice ritual with authored 3D foreground motion: anticipation, throw, multiple impacts, settle, readable result.
2. Deterministic per-tile movement rhythm, not rAF-dependent inference.
3. One and only one landing impact per human roll.
4. Tile-local landing spotlight tied to the actual destination.
5. Human SOL purchase has its own ownership-build animation; Bot purchase feedback is quieter.
6. Formal audio mix buses: UI / physical / reward / event / ambience, with ducking during hero beats.
7. Real haptic path where supported, graceful fallback on web.
8. Camera/board choreography for hero beats without breaking mobile readability.
9. Replace timing-prototype tones with authored/licensed/original sound assets before this slice can score Sound >=2.

Only after first roll + SOL purchase reaches benchmark threshold may the feedback grammar be propagated to the rest of the game.