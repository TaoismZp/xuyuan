# Crypto Tycoon — Build Blueprint V7

Candidate: candidate-v13
Goal: make one dice roll + one SOL purchase feel like a mature casual-board-game hero interaction before scaling feedback to the rest of the game.
Protocol: wish-delivery/versions/v7.7.md
Inputs: GAME_FEEL_BENCHMARK.md, COMPARATIVE_REVIEW_V12.md, AUDIO_DIRECTION_V13.md

## Scope lock
Do not add new economy, tiles, progression, events, characters or monetization. Do not propagate v12 feedback across all event families yet.

## Hero interaction requirements

### 1. Dice as a hero object
- Physical anticipation pose before release.
- Non-linear throw arc with independent angular momentum on both dice.
- Multiple contact beats before final settle.
- Final face held 260–420 ms before token movement.
- Foreground composition must remain readable on iPhone.

### 2. Deterministic movement rhythm
- Exactly one movement beat per tile traversed.
- Each beat includes visual hop/contact and a short contact sound.
- Last step is stronger than intermediate steps.
- Step feedback is driven by semantic movement schedule, not frame-sampling inference.

### 3. One landing, one impact
- One semantic landing event per human roll.
- Local destination ring/spotlight.
- Board/camera punch only once.
- Remove initialization and geometry duplicate landing pulses.

### 4. Ownership build
After SOL buy confirmation:
- tile ownership is visibly claimed/built over 300–550 ms;
- cash change is animated rather than silently replaced;
- purchase success gets a dedicated physical + musical cue;
- Bot purchases use lower-priority mix/visual treatment.

### 5. Authored audio
Replace hero-loop runtime synthesized cues with pre-rendered original/licensed assets for:
- dice rattle
- dice impact
- token step
- landing
- purchase success
Runtime synthesis remains fallback only.

### 6. Mix choreography
- UI, Physical, Reward, Event, Ambience buses.
- ambience ducks during dice throw/landing/purchase.
- no master clipping.
- Safari decode failure falls back safely.

### 7. Haptics
Use `navigator.vibrate` where supported for small tactile punctuation only; do not depend on it for comprehension.

## Comparative acceptance
Re-score first dice roll and SOL purchase on:
anticipation / motion quality / impact / sound layering / result salience / pacing / world reactivity.

PASS: every category >=2 and average >=2.4.
If score remains below threshold, candidate-v13 remains a failed vertical slice and must not expand.