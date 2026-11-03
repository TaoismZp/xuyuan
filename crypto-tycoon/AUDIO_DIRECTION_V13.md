# Crypto Tycoon — Audio Direction v13

Status: candidate-v13 hero-loop production contract

## Intent
Sound should make the board feel physical, expensive and reactive—not like browser UI beeps.

The mix is divided into five semantic buses:
1. UI — tiny, dry, immediate.
2. Physical — dice, token, board impacts; carries weight and material identity.
3. Reward — ownership, cash, positive events; bright and musical.
4. Risk/Event — rent, liquidation, bear/panic, hacks; darker and wider.
5. Ambience — low-level city/market bed; ducks under hero moments.

## First-roll mix choreography
- Button press: short UI tactile cue.
- Anticipation: 120–180 ms rising charge; ambience -3 dB.
- Dice throw: authored rattle, not continuous oscillator noise.
- Impacts: 2–4 separated impacts with one dominant landing hit.
- Movement: one short token/board contact per tile.
- Landing: distinct board impact + local tile ring.
- Decision reveal: soft UI whoosh, not another reward cue.
- Purchase: ownership build sound + short musical confirmation.
- Recovery: ambience returns over 180–300 ms.

## Asset rule
Runtime synthesis may remain only for fallback or tiny UI sweeteners. Hero physical/reward cues must use pre-rendered original or clearly licensed audio assets.

## Mobile rule
- Audio starts only after trusted user gesture.
- Master mute is always reachable.
- No overlapping cue may clip the master bus.
- Hero cues may duck ambience but may not block interaction.
- Safari failure to decode one cue must degrade to procedural fallback, never break the game.

## Acceptance
The first-roll sequence must be understandable with eyes closed at the level of: button pressed → dice moving → dice landed → token moving tile by tile → token landed → asset decision → purchase completed.