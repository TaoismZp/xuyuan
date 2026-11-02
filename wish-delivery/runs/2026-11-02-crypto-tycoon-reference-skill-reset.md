# 2026-11-02 — Crypto Tycoon Reference + Skill Reset

## Failure being corrected
The prior `crypto-tycoon/3d.html` was functionally playable but visually remained a DOM board with CSS perspective and emoji-like landmarks. It was incorrectly described as close to the generated 3D target image. User comparison exposed a Visual/Brand + Comparative Quality failure and an Evaluator failure.

## Capability gaps
- true 3D scene/camera/material/light pipeline;
- authored 3D tile landmarks and differentiated player pieces;
- game HUD that frames a world instead of looking like a dashboard;
- mobile 3D delivery and browser evidence;
- reference-first visual regression;
- traceable Skill procurement rather than a retrospective list of Skill names.

## Candidate search and static review
### Adopted
1. **OpenAI `web-game-foundations`**
   - source: `openai/plugins/plugins/game-studio/skills/web-game-foundations/SKILL.md`
   - reason: explicit browser-game architecture, vanilla Three.js default for direct 3D scene control, simulation/render separation, DOM HUD guidance, 3D asset policy.
   - implementation impact: premium build moved to a Three.js scene; game state remains serializable outside renderer; text-heavy HUD stays DOM-based.

2. **`threejs-game-director`** from `majidmanzarpour/threejs-game-skills`
   - reason: directly targets broad Three.js upgrades from playable prototype to premium/release-ready game and forbids stopping at a first playable slice when visual quality was rejected.
   - implementation impact: old CSS-perspective branch is treated as a prototype/failed baseline; the new route owns graphics, UI and QA as separate production phases.

3. **`threejs-gameplay-systems`**
   - reason: keeps the playable loop, deterministic test mode, input/state boundaries and a representative playable slice while the renderer changes.
   - implementation impact: preserved the board-game loop (dice → movement → land → decision → bot turns → market regime → settlement) rather than building a static art demo.

4. **`threejs-aaa-graphics-builder`**
   - reason: exact match for “still looks basic”; its core rule says glow does not make primitives AAA and requires authored forms → materials → lighting → effects.
   - implementation impact: exchange tower, bull, bear, rocket, whale, mine, vault, staking, NFT and player pieces are built as scene geometry; neon is added after forms instead of being used as the only polish.

5. **`threejs-game-ui-designer`**
   - reason: directly addresses the generic side-dashboard failure and requires hierarchy, safe areas, touch targets and UI/world cohesion.
   - implementation impact: leaderboard, round/goal, small side actions, ticker and oversized dice button frame the world without owning game logic.

6. **`threejs-qa-release`**
   - reason: requires real-input gameplay, target-viewport screenshots, mobile checks, production/static-host verification and browser error capture.
   - implementation impact: added a Playwright GitHub Actions pass for desktop, iPhone and public delivery surface with uploaded visual evidence.

### Reviewed but not selected as primary
- **Clawic `game-development`** — useful browser-game principles, but overlaps the selected architecture/playtest stack and is less specific about premium Three.js visual finishing. Retained as a secondary cross-check, not part of the minimum stack.
- **generic `develop-web-game` variants** — strong iterate/playtest loop, but largely duplicated by existing deterministic hooks + selected Three.js QA pack; not added to the primary stack.

## Representative head-to-head
Baseline A: prior `crypto-tycoon/3d.html` — CSS perspective over DOM board, generic panels, emoji/symbol props.

Candidate B: `crypto-tycoon/premium.html` — Three.js WebGL world, volumetric board, procedural authored landmarks, four stylized 3D player pieces, dice animation, lights/shadows/materials, skyline and DOM HUD.

Candidate B is allowed to replace A only after the browser workflow produces valid desktop/mobile/public screenshots and the visual comparison against `crypto-tycoon/REFERENCE_FIXTURE.md` is reviewed. Functional PASS alone is insufficient.

## Reference fixture
`crypto-tycoon/REFERENCE_FIXTURE.md` locks the generated 1672×941 concept image as the quality target. The source image SHA-256 at lock time is recorded there.

## Delivery surface
Primary target: iPhone/iPad/desktop browser with no login, wallet or install. Static hosting only. Current public candidate URL uses `raw.githack.com` against the exact Git commit so the tested revision and user-facing revision can match.

## Current status
This run is not allowed to claim Final until:
- premium browser workflow is green;
- uploaded active-play screenshot is inspected rather than trusting CI status alone;
- reference comparison does not read as “concept art vs ordinary webpage”;
- primary entry is switched only after the new candidate clears those gates.
