# Crypto Tycoon — Supervision Report v6

## 1. Inspection Scope
- candidate implementation: `candidate-v6.html` + `candidate-v6-augment.js`
- evidence build head: `c15d1c69c61d46621782e519db273a72a2276b82`
- candidate construction commit: `cc06f59bfea8326ecb9c722fae9b1c0b95501a3d`
- evidence workflow run: `41500910737`
- evidence artifact: `crypto-candidate-supervisor-evidence-v6-cjk`
- desktop evidence: 1672×941
- iPad evidence: 1194×834
- locked Vision Fixture: `REFERENCE_FIXTURE.md`
- Build Blueprint: `BUILD_BLUEPRINT_V3.md`
- governing protocol: `wish-delivery/versions/v7.4.md`

## 2. Integrity Check
- effect image used as runtime background: **NO — PASS**
- `keyart-chunk-*.js` imported at runtime: **NO — PASS**
- real WebGL geometry: **YES — PASS**
- Chinese evidence rendered with actual CJK supervision font: **YES — PASS**
- candidate / evidence same source revision family: **YES — PASS**
- Fake Convergence: **not detected**

## 3. Independent Visual Judgment

### Result: **FAIL — remain in Visual Vertical Slice**

v6 is a real improvement over v4 and now reads as a crypto board game rather than a generic developer demo. However it still does not pass the effect-drawing / commercial-product bar.

### 0–10 construction score
| Category | v4 baseline | v6 | Gate | Supervisor finding |
|---|---:|---:|---:|---|
| Composition | 7.8 | 7.6 | 8.0 | central focus is stronger, but the new thick title plaque blocks the globe/stage and partially suppresses the dice |
| Spatial depth | 8.2 | 8.2 | 8.0 | board / skyline / stage have convincing real depth |
| Authored forms | 6.8 | 7.4 | 7.5 | added towers, decks and landmarks help, but skyline and several heroes still expose procedural construction |
| Material hierarchy | 7.5 | 7.8 | 7.5 | gold / enamel / dark metal / neon roles are clearer |
| Lighting / separation | 6.8 | 7.4 | 7.5 | brighter and more commercial, but front-left props are over-hot while some skyline mass stays dark |
| Character quality | 6.8 | 7.0 | 7.5 | silhouettes read, but characters still look like assembled primitives beside the reference's collectible figures |
| Landmark density | 7.2 | 7.9 | 8.0 | meaningful gain; still lacks the reference's large BTC/ETH hero beacons and skyline variety |
| UI-world cohesion | 7.4 | 7.8 | 7.5 | Chinese HUD fits the board game better and no longer dominates the scene |
| Readability | 5.8 | 7.7 | 8.0 | CJK tiles and HUD are readable, but perspective shrinks many tile consequences and title hierarchy is cluttered by old + new logo layers |
| Desirability / product class | 7.4 | 7.8 | 8.0 | now clearly game-like and attractive, but still one product tier below the locked effect drawing |

Average: **7.66 / 10**. Hard gate remains FAIL because several required categories are below threshold.

## 4. A-class blockers
1. **Double / conflicting center brand hierarchy**
   - the old `CRYPTO TYCOON` monument remains visible behind the new Chinese plaque;
   - the new plaque is too thick, too opaque and too low;
   - it hides the market globe and competes with the hero dice instead of integrating with them.
2. **Reference still wins immediately on authored-world density**
   - current skyline remains visibly generated from repeated tower families;
   - the effect drawing has distinct exchange architecture, BTC beacon, ETH beacon, chart wall and layered city depth.
3. **Hero characters still below collectible-toy bar**
   - their roles read, but construction still reads as sphere/box assembly at first glance.

## 5. B-class defects
- front-left local lights blow out astronaut / coin surfaces;
- Chinese tile descriptions remain too small on the far side;
- right-side hero skyline is weak relative to the reference;
- foreground card decks help but are visually detached from the board rim.

## 6. Stop-Work Decision
**CONTINUE VISUAL CONSTRUCTION ONLY.**

Do not add gameplay yet. Do not deploy v6 as the production root. Do not call CI PASS an aesthetic PASS.

## 7. v7 Remediation Matrix
| Defect | Level | Root cause | v7 action | Gate |
|---|---|---|---|---|
| opaque center plaque | A | copied hierarchy semantically but not spatially | replace with transparent/open 3D crest; reveal globe/dice; remove old English logo from sight | Composition ≥8 |
| repeated skyline | A | procedural building family still dominates | suppress repeated skyline mass; add distinct exchange/BTC/ETH/chart hero structures and near/mid/far spacing | Forms ≥7.5 / Density ≥8 |
| primitive character read | A | accessories added without silhouette redesign | increase toy proportions, add face/helmet/wardrobe signature pieces and cleaner material separation | Character ≥7.5 |
| lighting imbalance | B | local practical lights stacked over earlier lighting | reduce blown highlights, raise controlled fill on skyline | Lighting ≥7.5 |
| far tile readability | B | 24 small panels under steep perspective | strengthen key tile title scale and reduce secondary text on far edge | Readability ≥8 |

## 8. Supervisor statement
v6 proves the construction method is converging without using reference pixels, which is important. It does **not** prove the target has been reached. The correct action is another focused visual pass, not gameplay expansion and not delivery.