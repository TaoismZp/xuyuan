# Crypto Tycoon — Build Blueprint v5 (Controlling Drawing)

## Status
This is the **controlling construction drawing** for the current rebuild under `wish-delivery/versions/v7.6.md`.

It supersedes `BUILD_BLUEPRINT_V4.md`. All system decomposition, Reference-to-Implementation mapping, asset manifest, camera/composition and Stage-1 quality thresholds from v4 remain in force unless explicitly changed below.

The accepted build must never import or render `keyart-chunk-*.js`, `visual-v3*`, screenshots, mockups or any Reference Fixture pixels at runtime.

The existing public game remains the fallback until the new candidate passes construction supervision, gameplay acceptance, mobile/performance acceptance and exact-build public delivery acceptance.

---

## 1. Binding Chain
Every supervision report is invalid unless it binds:
1. **Vision Fixture**: `REFERENCE_FIXTURE.md` + locked effect-image identity;
2. **Controlling Blueprint**: this file path + current Git blob SHA;
3. **Protocol**: `wish-delivery/versions/v7.6.md` + Git blob SHA;
4. **Candidate**: exact candidate commit SHA + candidate version marker;
5. **Evidence**: exact workflow run + artifacts from that candidate.

Final acceptance adds exact public Delivery Surface build identity.

---

## 2. Durable Project State
`PROJECT_STATE.md` is mandatory for this project. Any chat end, timeout or CI failure changes task state but does not terminate the project. When the project is resumed, read the state file and execute `next_executable_action` before asking the user to restate context.

---

## 3. Production Bottleneck
Current highest-weight bottleneck remains **commercial stylized 3D art reconstruction**.

Priority:
1. silhouette / composition
2. authored hero assets and landmark density
3. tile storytelling / readability
4. material hierarchy
5. lighting / contact / depth
6. character collectible quality
7. UI-world cohesion
8. motion / game feel
9. performance
10. gameplay integration
11. deployment

Until items 1–7 pass Stage-1 supervision, gameplay expansion is prohibited.

---

## 4. Capability / Skill Proof
Methods already read and applied:
- `threejs-game-director`
- `threejs-aaa-graphics-builder`
- `threejs-3d-generator`
- `threejs-game-ui-designer`
- `threejs-qa-release`
- `threejs-aaa-graphics-builder/references/visual-scorecard.md`

Permanent lessons already bound to this drawing:
- CSS-perspective and reference-composite routes rejected;
- v4 true Three.js candidate functional but below target;
- v6 improved materially but failed center hierarchy, skyline authorship and collectible-character gates;
- v7 crossed from dev-scene into a coherent commercial 3D prototype but still failed center hierarchy, collectible-character quality, authored skyline quality, readability and desirability thresholds;
- reference pixels may never substitute for authored 3D.

---

## 5. Stage-1 Acceptance Blueprint
At desktop 1672×941 and iPad landscape 1194×834, the real-time WebGL candidate must meet every minimum:

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

Hard FAIL if any of the following holds:
- Reference Fixture pixels appear at runtime;
- hero asset reads first as placeholder/raw primitive assembly;
- active scene reads as webpage/dashboard rather than a 3D tabletop world;
- board stops dominating composition;
- candidate remains materially lower product class than effect drawing;
- candidate / protocol / blueprint / evidence identities do not match;
- Chinese title/tile information is broken on supervised surface;
- darkness, bloom, blur or HUD coverage hides weak authored forms.

---

## 6. Current Stage-1 Construction Order — v8
v8 is restricted to the A-class defects in `SUPERVISION_REPORT_V7.md`.

### A1. Center hierarchy
- Remove competing legacy center signs/crests from the hero depth band.
- Rear-mount the Chinese title as an architectural landmark rather than placing it over the dice.
- Preserve negative space and readable physical stage/dice silhouette.

### A2. Character collectible quality
- Strengthen silhouette differentiation for astronaut, Doge, NFT/robot and bull pieces.
- Improve visor/face treatment, head-body proportion, signature accessories, pedestal language and material separation.
- At least three pieces should be recognizable from silhouette alone.

### A3. Environment authorship
- Further trim repeated shelf-tower skyline mass.
- Add unmistakable hero structures with distinct profiles rather than additional generic boxes.
- Preserve clear foreground / midground / background spacing.

### A4. Readability / light balance
- Lower center point-light dominance so dice pips, stage edge and Chinese title do not merge into a single hot region.
- Prevent `掷骰子` wrapping on iPad.
- Keep tile and market-state information readable without enlarging generic HUD panels.

**No gameplay expansion until v8 independent supervision explicitly PASSes Stage 1.**

---

## 7. Monitor Simplicity Rule
The monitor must be simpler than the product.

### Proven Stage-1 evidence chain
**candidate reaches exact version marker → allow final live frame to render → freeze future animation → Chrome DevTools Protocol `Page.captureScreenshot` from the actual viewport → PNG artifact + metadata.**

This is the repository's proven stable path for software-WebGL capture. Do not replace it with:
- Three.js prototype monkey-patching;
- a second renderer/composer/world;
- synchronous `readRenderTargetPixels`/raw `gl.readPixels` evidence paths;
- `canvas.toDataURL()` if SwiftShader stalls;
- full-page Playwright screenshot fallbacks.

Monitor failure is `BLOCKED_TECH`, not product failure. Evidence-capture PASS only proves the evidence exists; it does not imply Visual PASS.

---

## 8. Stage-2 Minimal Interactive Slice
Only after Stage 1 PASS:
- real roll input;
- real dice state/animation;
- human token movement on the same 24-tile loop;
- one asset purchase/pass decision changing serializable state;
- one bot turn;
- one market-regime transition;
- HUD/state synchronization;
- post-interaction screenshot regression.

---

## 9. Stage-3 Full Gameplay
Only after Stage 2 PASS:
- integrate 24-tile domain rules;
- buy / rent / upgrade / sector bonus;
- bull/bear/mania/panic/sideways regimes;
- Airdrop/Gas/Rug/Hack/ETF/liquidation/Halving/whale events;
- forced liquidation;
- 3 bots;
- 12 rounds;
- result/bankruptcy/replay;
- save/resume if compatible.

---

## 10. Stage-4 Mobile / Performance
Target includes iPad/iPhone Safari. Preserve the same 3D world, cap DPR as needed, instance repeated props, constrain shadows/lights, reduce texture memory without replacing authored forms.

---

## 11. Stage-5 Candidate Public Deployment
Deploy accepted candidate to a non-root public path first. Verify exact candidate commit on actual GitHub Pages surface. No root replacement yet.

---

## 12. Stage-6 Final Acceptance
Before replacing `crypto-tycoon/index.html`, independent acceptance must prove construction integrity, visual comparison, full functional core loop, desktop+iPad/iPhone quality, exact public build identity, no reference substitution and no open A-class defect.

Only then may the accepted candidate replace the public root and be called the finished user artifact.