# Crypto Tycoon — Market Benchmark & Game Feel Target

Status: controlling benchmark for candidate-v12+

## Reference Set

### 1) MONOPOLY GO! — mobile feedback benchmark
Use for: dice ritual, reward velocity, readable board progression, large mobile feedback, event cadence, audiovisual salience.

Observed product principles:
- The dice are a hero interaction, not a background RNG control.
- Fast reward loops and visually rich progression are core to the product feel.
- The product uses lively animation, themed worlds, landmarks and event interludes to turn a simple board action into repeated spectacle.
- Sound is treated as a first-class design system, not a finishing patch.
- Every meaningful result is amplified: movement, build, collect, attack, steal, win.

Do not copy proprietary art/audio/UI. Extract only timing, hierarchy, feedback density and interaction grammar.

### 2) Richman 11 / 大富翁11 — board-world reactivity benchmark
Use for: character personality, transport/movement identity, cards, map mechanisms, special-tile events, voice/character feedback.

Observed product principles:
- Characters possess distinct visual identity and movement presentation.
- Cards and mechanisms are events with their own presentation, not plain modal text.
- The board contains reactive world objects and special systems.
- Full voice/audio support reinforces personality and event readability.

### 3) Coin Master / Board Kings family — short-loop rhythm benchmark
Use for: action → result → reward/failure → next action pacing; high-salience short interludes; reward anticipation.

Observed product principles:
- One tap produces a short staged sequence rather than an immediate number change.
- Positive and negative outcomes have different audiovisual signatures.
- The user is returned quickly to the next meaningful action.

## Core Design Principle

Crypto Tycoon should not imitate Monopoly's IP expression. It should translate mature casual-board feedback grammar into a crypto-native world:
- Dice = risk entering the market.
- Movement = capital moving through regimes/opportunities.
- Asset landing = entry/position decision.
- Rent = counterparty/market transfer.
- Bull/Bear = world state transformation.
- Liquidation = dramatic failure event.
- Airdrop/Mine/Vault = reward moments.

## Feel Vertical Slice Contract

The first accepted slice must cover one complete human turn:

1. **Ready**
   - Board has low-volume ambient life.
   - Roll button has subtle idle pulse, not distracting.

2. **Input**
   - Press has <100ms visual response.
   - Audio context unlocks on user gesture.
   - Roll button compresses and releases.

3. **Dice Anticipation**
   - 100–180ms wind-up.
   - Small camera/board pull-back or energy gather.
   - Short pre-roll tick/charge.

4. **Dice Action**
   - 650–900ms roll with multiple rotational axes.
   - Audible rattle / impacts.
   - Final landing has a distinct low-frequency impact.
   - Result is held long enough to read before movement begins.

5. **Movement**
   - Each tile step has a short hop/lean rhythm.
   - Every step produces a light tick/footstep.
   - Final step is larger than intermediate steps.

6. **Landing Impact**
   - Token squash/settle.
   - Board/canvas gets a restrained punch.
   - Landing tile gets a local light/ring pulse.
   - Landing sound differs by tile category.

7. **Resolution**
   - Asset: ownership / purchase decision arrives with tile spotlight and short whoosh.
   - Event: presentation takes over center attention briefly; not just a static webpage modal.
   - Reward: positive particle/cash burst + rising chime.
   - Loss: lower sting + red pressure pulse + restrained shake.

8. **State Change**
   - Cash/net-worth number animates between values.
   - Ownership ring builds in rather than appearing instantly.
   - Bull/bear regime change affects board ambience/light/audio motif.

9. **Recovery**
   - FX resolves cleanly.
   - Ambient mix returns.
   - Next actionable state is visually obvious.

## Audio Asset Contract

At minimum:
- UI press
- roll anticipation
- dice rattle loop
- dice impact
- movement tick x variants
- landing neutral
- purchase success
- upgrade success
- rent/payment loss
- reward/airdrop
- negative/liquidation
- bull regime sting
- bear regime sting
- event reveal
- end-game win/loss
- subtle ambient/music bed

Implementation may start with synthesized/procedural Web Audio, but placeholder beeps are not accepted final assets. Each cue needs intentional envelope, timbre and mix role.

## Motion Contract

Every key motion documents:
- duration
- easing
- anticipation
- overshoot/impact
- settle
- interrupt behavior
- reduced-motion fallback

No core action may be represented only by linear interpolation.

## Camera / Screen Choreography

Because this is a mobile web 3D game, effects must remain restrained enough for iPhone Safari:
- Prefer short camera/board punches over continuous camera travel.
- Avoid motion sickness and large forced zooms.
- Maintain readable UI during movement.
- Never hide the next required action behind long celebration.

## Acceptance Tasks

Candidate must be compared to benchmarks on:
1. first dice roll
2. asset purchase
3. rent/payment loss
4. special positive event (airdrop/vault/mine)
5. special negative event (liquidation/hack/bear)
6. market regime change
7. round transition
8. final ranking

For each task score 0–3:
- anticipation
- motion quality
- impact
- sound layering
- result salience
- pacing
- world reactivity

PASS requires every category >=2 and average >=2.4 on the five most frequent tasks.

## Current v11 Gap

v11 has:
- real dice rotation and vertical arc
- per-tile token hop
- deterministic gameplay loop
- functional modal/toast feedback

v11 is missing or weak on:
- sound system
- layered dice impacts
- per-step movement audio
- anticipation / settle staging
- tile-local landing FX
- animated money / ownership transitions
- differentiated positive/negative feedback
- market-regime audiovisual transformation
- event presentation
- end-game ceremony
- ambient world/audio life

Therefore v11 must be classified as **playable prototype / accepted technical baseline**, not finished commercial game.