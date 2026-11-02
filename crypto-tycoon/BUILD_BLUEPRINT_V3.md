# Crypto Tycoon — Build Blueprint v3

## 0. Contract
This is the **construction drawing** for the real-time 3D rebuild under `wish-delivery/versions/v7.4.md`.

The accepted build must never import or render `keyart-chunk-*.js` or any Reference Fixture pixels at runtime.

The existing public game remains a functional fallback until the new candidate passes independent supervision + acceptance.

---

## 1. Primary Artifact
A real-time Three.js crypto tycoon board game that opens from the public GitHub Pages URL and can be played on iPad/iPhone/desktop.

### Core loop
Enter table → roll dice → move → buy/upgrade/pay/resolve crypto event → bots act → market regime evolves → survive 12 rounds / bankruptcy → final net-worth result → replay.

### Final Delivery Surface
`https://taoismzp.github.io/xuyuan/crypto-tycoon/`

### Candidate Surface
New visual work stays on `candidate-*` files until accepted.

---

# 2. Production Bottleneck
Highest-weight bottleneck: **commercial stylized 3D art reconstruction**.

Quality order:
1. silhouette / composition
2. authored hero assets and landmark density
3. tile storytelling / readability
4. material hierarchy
5. lighting / contact / depth
6. UI-world cohesion
7. motion / game feel
8. performance
9. gameplay integration
10. deployment

Until 1–6 pass Vertical Slice supervision, gameplay expansion and deployment are not evidence of visual completion.

---

# 3. Capability / Skill Proof
Actual GitHub Skill resources read for this construction phase:

1. `majidmanzarpour/threejs-game-skills/skills/threejs-game-director/SKILL.md`
   - applied rule: premium request requires complete authored visible surfaces, representative scene first, active-play evidence, and independent focused review.
2. `.../threejs-aaa-graphics-builder/SKILL.md`
   - applied production order: **authored forms → materials → lighting → effects**; glow may not rescue primitives; weak surfaces must be upgraded beyond the hero.
3. `.../threejs-3d-generator/SKILL.md`
   - applied asset rule: premium hero surfaces should use generated/imported game-ready assets when that capability is available; if unavailable, procedural work must still produce authored silhouettes, not stand-ins.
4. `.../threejs-game-ui-designer/SKILL.md`
   - applied UI rule: avoid generic stat-card dashboard; hierarchy is status/objective/feedback/flavor; HUD must frame the board rather than replace it.

### Representative comparison already observed
- old CSS-perspective / reference-composite paths: rejected;
- true Three.js candidate v2: same broad product class but visual score only ~7.17/10 and readability 5.8;
- therefore next work concentrates on the five supervisor blockers rather than adding gameplay.

### Minimum stack locked
- Runtime: Three.js r180 + real WebGL canvas
- Geometry: authored procedural geometry using RoundedBoxGeometry + custom factories
- Materials: MeshPhysical / Standard + CanvasTexture only for text/sign information surfaces
- Post: existing composer/bloom after geometry and lighting, not as a substitute for forms
- HUD: HTML/CSS overlay driven by game state
- QA: Playwright screenshot capture + independent supervision report + public GitHub Pages acceptance

---

# 4. Reference-to-Implementation Mapping
| Reference element | Real implementation | Forbidden substitute | Gate |
|---|---|---|---|
| Square-loop board | thick beveled Three.js board + 24 raised tiles | CSS transform / screenshot | depth + composition |
| Central logo/stage | physical layered stage + globe/market object + real 3D title monument | flat HTML banner | hero focal point |
| Character pieces | authored collectible figurine geometry | dots / emoji / simple stack | silhouette |
| Bull / bear / whale / rocket / exchange | authored multi-part 3D landmarks | icon-only tile | landmark density |
| Tile names/effects | real tile planes with CanvasTexture information surfaces | tiny unreadable labels | readability |
| Skyline | authored varied facade kit, roofs, signs, depth layers | repeated box wall | environment authorship |
| Dice / chips / coins | real foreground geometry | HUD-only dice icon | foreground density |
| HUD | compact authored clusters around board | tall generic side dashboard | UI-world cohesion |
| Effect image | comparison-only evidence | runtime backplate | construction integrity |

---

# 5. Asset Manifest v3

## Hero Assets
- 1 thick board chassis with gold/cyan rails
- central market globe/stage
- large physical `币圈大富翁 / CRYPTO TYCOON` monument
- 2 hero dice
- foreground chips / coin stacks

## Character Tokens
- astronaut trader
- Doge whale
- NFT quant
- bull holder

Each must have: base, readable head/torso silhouette, signature cue, multi-material separation and toy-scale proportions.

## Landmark Kit
Required high-weight set:
- exchange tower
- bull market statue
- bear market statue
- mining rig
- airdrop/parachute
- halving rocket
- NFT collectible
- DeFi / staking structure
- whale
- vault

## Environment Kit
- 4–6 signature towers
- 8–14 secondary varied buildings
- finance terminal billboard
- BTC / ETH beacon structures
- facade ribs / roof caps / neon signage
- far skyline silhouettes

## UI / VFX
- portfolio rank cluster
- market cycle plaque
- compact asset/cards/rules controls
- physical-looking roll control
- market ticker
- landing / active-tile pulse

---

# 6. Stage-1 Vertical Slice — Current Construction Scope
Do **not** add full gameplay in this pass.

The next candidate may modify only these supervisor blockers:

1. **Tile storytelling/readability**
   - large title + consequence on the physical tile;
   - high contrast under actual scene lighting;
   - readable from the locked camera without zooming.
2. **Center / foreground density**
   - two real hero dice inside the lower-center board area;
   - chip / coin stacks around the center front;
   - reduce dead black center space.
3. **Lighting value range**
   - brighter toy-like value structure;
   - maintain gold/cyan neon but avoid black compression;
   - hero forms must read without bloom.
4. **Environment authorship**
   - replace repeated-window-wall impression with distinct facade families, rooftop forms and signage;
   - skyline must have near/mid/far hierarchy.
5. **Hero scale/detail**
   - landmarks and tokens receive stronger collectible silhouette and scale;
   - no new content category until these existing assets improve.

---

# 7. Camera / Composition
Desktop locked target:
- 1672×941 evidence viewport;
- Perspective camera ~34° FOV family;
- board occupies ~75–82% width;
- center stage is dominant focal point;
- foreground dice overlap the lower-center board area;
- skyline stays behind the board and does not become a wall.

Tablet:
- same world/camera family;
- camera may pull back slightly;
- board remains dominant; do not convert to dashboard composition.

---

# 8. Acceptance Blueprint
Vertical Slice passes only if independent supervision finds:

| Category | Minimum |
|---|---:|
| Composition | 8.0 |
| Spatial depth | 8.0 |
| Authored forms | 7.5 |
| Material hierarchy | 7.5 |
| Lighting / separation | 7.5 |
| Character quality | 7.5 |
| Landmark density | 8.0 |
| UI-world cohesion | 7.5 |
| Readability | 8.0 |
| Desirability / product class | 8.0 |

Hard FAIL regardless of score if:
- reference pixels appear in runtime;
- a hero object reads first as a primitive placeholder;
- active play becomes a generic dashboard;
- the board stops dominating the scene;
- the candidate is materially lower product class than the effect drawing;
- candidate and evidence are different commits.

---

# 9. Supervision / Stop-Work
Supervisor must inspect real screenshots, not code intent.

If any of the five Stage-1 blockers remains clearly dominant after two construction rounds, Stop-Work and return to asset/camera/material design instead of adding more detail elsewhere.

Only after Stage 1 PASS may work proceed to:
- minimal interactive slice;
- full gameplay integration;
- mobile optimization;
- candidate public deployment;
- final acceptance and root replacement.
