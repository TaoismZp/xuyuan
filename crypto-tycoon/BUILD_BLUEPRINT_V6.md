# Crypto Tycoon — Build Blueprint V6

Candidate: candidate-v12
Goal: turn the accepted v11 technical baseline into a benchmarked audiovisual game-feel vertical slice before any further feature expansion.
Protocol: wish-delivery/versions/v7.7.md
Benchmark: crypto-tycoon/GAME_FEEL_BENCHMARK.md

## Scope Lock
This phase does NOT add new economic systems, tiles, bots, progression, monetization or live-ops. It only upgrades the feel of the existing core loop.

## Primary Slice
One human turn:
**Roll press → dice anticipation/roll/impact → token movement → landing impact → decision/event → positive/negative resolution → return to next action.**

## Implementation Plan

### A. Audio Engine
Create a small Web Audio engine that unlocks on the first user gesture and exposes semantic cues rather than raw oscillator calls.
Cues: ui, charge, dice-rattle, dice-impact, step variants, land, buy, reward, loss, bull, bear, event, finish.
Requirements:
- gain staging and master mute
- no autoplay violation
- no continuous CPU-heavy DSP
- semantic event log for testing
- graceful no-audio fallback

### B. Motion Layer
Enhance current v11 movement without rewriting game rules:
- roll button press/release
- dice anticipation before existing roll
- landing impact pulse
- human token local squash/settle after movement
- ownership/reward visual pulse
- positive and negative screen feedback
- animated floating cash/result text
- modal entrance/exit with game-style transition

### C. World Reactivity
- subtle board ambience while idle
- bull/bear regime visual tint pulse
- positive event sparkle burst
- negative event pressure pulse
- local tile highlight on landing when detectable

### D. Controls
- sound on/off control
- reduced-motion detection / fallback
- preserve 44px+ mobile targets

## Non-Destructive Architecture
candidate-v11 remains immutable baseline.
candidate-v12 is composed as:
- candidate-v12.html
- candidate-v11.css (baseline)
- candidate-v12-feel.css (new experience layer)
- candidate-v11-game.js (accepted rules engine)
- candidate-v12-feel.js (new audiovisual reaction layer)

No v11 file is modified.

## Evidence Hooks
candidate-v12 exports `window.__cryptoFeelProof` with:
- version
- audioUnlocked
- cueCounts
- diceImpacts
- stepCues
- positiveBursts
- negativeBursts
- landingPulses
- reducedMotion
- interactionErrors

## Gate 1 — Functional Preservation
v11 deterministic gameplay smoke still passes through candidate-v12.

## Gate 2 — Feel Slice
The first human turn must emit, in order:
1. input cue
2. anticipation cue
3. dice motion/rattle
4. dice impact
5. movement cues
6. landing feedback
7. decision/event reveal
8. resolution feedback
9. return to actionable state

## Gate 3 — Mobile
- iPhone-class viewport
- zero horizontal overflow
- audio unlock occurs only on gesture
- sound control reachable
- reduced-motion works

## Gate 4 — Comparative Review
Compare candidate-v12 against GAME_FEEL_BENCHMARK on first dice roll + asset purchase. If the candidate still reads as a technical demo, STOP-WORK before expanding the effect system.

## Acceptance Rule
Candidate-v12 can only be called a Game Feel vertical slice, not final product. Full-product status requires the same feedback grammar to cover all major event families and final ranking.