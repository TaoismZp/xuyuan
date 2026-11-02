# Crypto Tycoon — Build Blueprint v2

## 0. Contract
This blueprint is the construction drawing for the true-3D rebuild under `WISH_DELIVERY_V7.md` v7.5.

The current live game remains a functional fallback only. The accepted rebuild must not import or render `keyart-chunk-*.js` or use any Reference Fixture pixels at runtime.

## 1. Primary Artifact
A real-time Three.js crypto tycoon board game that opens from the public GitHub Pages URL and can be played on iPad/iPhone/desktop.

### Core loop
Enter table → roll dice → move → buy/upgrade/pay/resolve crypto event → bots act → market regime evolves → survive 12 rounds / bankruptcy → final net-worth result → replay.

### Delivery surface
`https://taoismzp.github.io/xuyuan/crypto-tycoon/`

The final public root may switch to the rebuilt version only after monitor + acceptance gates pass.

---

# 2. Production Bottleneck
Highest-weight bottleneck: **commercial stylized 3D art reconstruction**.

Quality order:
1. silhouette / composition
2. authored 3D assets and density
3. material hierarchy
4. lighting / contact / depth
5. UI-world cohesion
6. motion / game feel
7. performance
8. gameplay integration
9. deployment

Until items 1–5 pass the Vertical Slice gate, items 6–9 cannot be used as evidence of visual completion.

---

# 3. Skill Proof Record
Actual GitHub resources read for this rebuild:

1. `majidmanzarpour/threejs-game-skills/skills/threejs-game-director/SKILL.md`
   - used for premium pipeline, representative scene first, sibling skill routing, active-play evidence.
2. `.../threejs-3d-generator/SKILL.md`
   - used to define when hero characters/buildings require generated/imported game-ready 3D rather than primitive stand-ins.
3. `.../threejs-aaa-graphics-builder/SKILL.md`
   - used for the hard production order: authored forms → materials → lighting → effects, premium scorecard philosophy, hero + world-kit coverage.

The build must record any additional Skill loaded before its phase is implemented.

---

# 4. Scene Architecture

## 4.1 Renderer
- Three.js WebGLRenderer.
- ACES Filmic tone mapping.
- sRGB output.
- desktop DPR max ~1.75; tablet ~1.5; phone lower if needed.
- WebGL canvas occupies the primary visual surface; HTML is HUD only.

## 4.2 Camera
Desktop master camera:
- Perspective camera, 30–38 mm equivalent feel.
- three-quarter top-down pitch ≈ 32–38°.
- board fills ~75–82% viewport width.
- center monument remains the hero focal point.
- foreground dice overlap lower board edge slightly.
- skyline stays behind board, never forming a vertical wall.

Tablet camera:
- same world and angle family;
- move camera back and reduce side HUD width rather than collapsing to a dashboard.

## 4.3 Spatial Layers
1. Foreground: dice, chips, cards, rail/coins.
2. Board: raised tiles, characters, landmarks.
3. Center: title/crown + market globe/ticker stage.
4. Background near: exchange tower / skyline props.
5. Background far: simplified city silhouettes / chart lights.

---

# 5. Geometry Construction

## 5.1 Board
- rounded rectangular base with real thickness;
- double-layer gold/blue trim;
- recessed center pit;
- 24 raised tile plinths distributed around a square loop;
- tile faces use bevelled geometry, not CSS or sprites;
- corner tiles receive signature structural props.

## 5.2 Tile System
Each tile owns:
- base mesh;
- top enamel panel;
- category icon plate;
- ownership rim;
- level pylons;
- optional landmark anchor;
- interaction highlight.

Tile labels may use CanvasTexture/SDF text because text itself is not the hero geometry.

## 5.3 Center Stage
Three levels:
1. lower circular/hex pedestal with gold trim;
2. glass market globe + candlestick orbit;
3. raised gold title/crown monument.

The center must read as a physical installation, not a floating HTML banner.

## 5.4 Character Tokens
Four collectible figurines, each with:
- base/plinth;
- torso/head/limbs or equivalent authored silhouette;
- signature prop/readability cue;
- distinct material palette;
- subtle idle motion;
- landing pulse.

If a token still reads first as primitive assembly in the reference camera, it fails and must be replaced/refined before full production.

## 5.5 Landmarks
Vertical slice must include six high-weight landmarks:
- exchange tower;
- bull;
- bear;
- whale;
- rocket;
- staking vault.

Each gets a thumbnail-readable silhouette and at least 3 authored detail layers.

---

# 6. Material Construction

Create a reusable `materials.js` / material factory with named roles:
- goldMetal
- darkLacquer
- enamelRed/Green/Blue/Purple
- ivoryResin
- cyanGlass
- brushedMetal
- toySkin/Fur-like matte variants
- emissiveScreen

No hero object may use one flat material for all of its visible surfaces.

---

# 7. Lighting / Post

Only after geometry review:
- warm directional/spot key;
- cyan rim;
- violet environment fill;
- shadow receiver on board;
- contact shadows for hero objects;
- selective bloom or emissive pass if performance allows;
- subtle vignette / color grade only after screenshot comparison.

Bloom, darkness and fog cannot be used to hide weak forms.

---

# 8. UI Construction

HTML HUD is permitted, but it must frame rather than replace the world.

Desktop:
- left compact leaderboard;
- right top round/goal plaque;
- right middle contextual actions;
- lower-right physical-looking roll control;
- ticker near lower center.

Tablet:
- leaderboard narrows;
- actions collapse to compact icons/chips;
- board remains visually dominant.

No tall generic dashboard column.

---

# 9. Gameplay Integration

Reuse proven domain rules where possible, but separate engine from renderer.

Required public state interface:
- `getState()` or equivalent serializable state;
- current player positions;
- tile ownership / levels;
- cash / net worth;
- market regime;
- round / turn;
- modal/action state.

Renderer subscribes to state; game logic must not own DOM layout or Three.js scene construction.

---

# 10. Construction Sequence

## Stage 1 — Visual Vertical Slice (NO full gameplay expansion)
Build:
- board base;
- 10–12 visible tiles;
- center stage;
- 4 character tokens;
- 6 landmarks;
- skyline kit;
- dice/coins;
- final camera;
- material library;
- lighting;
- HUD shell.

Output: active-play-like static scene at 1672×941 and iPad landscape.

Gate: Monitor compares it with Reference Fixture. If first impression is a different product class, return to geometry/assets/art direction.

## Stage 2 — Minimal Interactive Slice
Connect:
- roll dice;
- move one human token;
- one purchase modal;
- one bot turn;
- one market-state change.

Gate: visual quality may not regress during interaction.

## Stage 3 — Full Gameplay
Connect full 24 tiles, asset ownership/upgrades/rent/events/bots/12-round ending/replay.

## Stage 4 — Performance / Mobile
Optimize instancing, shadow count, texture resolution, DPR and layout while preserving the reference composition.

## Stage 5 — Public Deployment
Deploy candidate under a non-root candidate path first.

## Stage 6 — Independent Acceptance
Only after monitor passes visual + construction + functional + delivery checks may candidate replace the public root.

---

# 11. Monitor / Acceptance Metrics

Visual gate, equal-size comparison with Reference Fixture:
- Composition: >= 8/10
- Spatial depth: >= 8/10
- Authored form quality: >= 7/10
- Material hierarchy: >= 7/10
- Lighting/depth separation: >= 7/10
- Character quality: >= 7/10
- Landmark density: >= 8/10
- UI-world cohesion: >= 7/10
- Readability: >= 8/10
- Overall desirability/product class: >= 8/10

Hard fail regardless of average if:
- reference image pixels appear in runtime;
- hero object reads as primitive placeholder;
- board occupies a minority of the visual surface;
- active play becomes a generic dashboard;
- candidate is materially worse than the effect image in first-impression product class;
- public URL serves an older build than the accepted candidate.

---

# 12. Versioning / Safe Construction

- existing live root is not overwritten during Stage 1–4;
- rebuild lives under a separate candidate path / files;
- screenshots and QA artifacts are tied to commit SHA;
- failed visual approaches remain archived but are not imported by production;
- only accepted candidate becomes `crypto-tycoon/index.html` public root.
