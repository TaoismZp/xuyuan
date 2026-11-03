# Crypto Tycoon — Independent Supervision Report v7

## Verdict
**FAIL — Stage 1 not accepted. Do not integrate full gameplay.**

v7 is a material step forward: it now reads as a real-time stylized 3D board-game world rather than a tilted webpage/dev scene. The board dominates, the HUD is integrated around the world, Chinese text is present, the central dice/stage, collectible pieces, crypto-city skyline and authored props all exist without using Reference Fixture pixels.

But under the controlling drawing thresholds, v7 is still below the locked effect drawing in three highest-weight areas: **center hierarchy, collectible-character quality, and authored background/landmark quality**. Therefore Stage 1 remains closed.

---

## Binding Chain
- Protocol: `wish-delivery/versions/v7.6.md`
- Protocol blob SHA: `955bdde3d332283ff6ccc89f943555824f741d59`
- Controlling blueprint: `crypto-tycoon/BUILD_BLUEPRINT_V5.md`
- Blueprint blob SHA: `fa5b905efe3af8736ddba897c2d528cd21db2835`
- Vision Fixture: `crypto-tycoon/REFERENCE_FIXTURE.md`
- Vision Fixture canonical image SHA-256: `5b0c5d5d4f8f9afbd2af5e8dddbd77e749975006873262efadd02125ac68a039`
- Candidate: `candidate-v7`
- Candidate commit: `468b728f07e3a2c21dde6fd1fc7a7c67f0ebe86d`
- Supervisor workflow run: `41563650448`
- Evidence artifact: `crypto-candidate-supervisor-evidence-v7`
- Artifact ID: `13197743291`
- Artifact digest: `sha256:fb99b7ba586af91c041dec5d1d01c3a1f09c75763f93e27edbd27d1ad66cf5d2`
- Evidence surfaces: desktop 1672×941, iPad landscape 1194×834
- Reference substitution: **not detected**

---

## Scorecard
| Category | v5 blueprint minimum | v7 score | Result |
|---|---:|---:|---|
| Composition | 8.0 | 7.6 | FAIL |
| Spatial depth | 8.0 | 8.2 | PASS |
| Authored forms | 7.5 | 7.3 | FAIL |
| Material hierarchy | 7.5 | 8.0 | PASS |
| Lighting / separation | 7.5 | 7.8 | PASS |
| Character quality | 7.5 | 6.8 | FAIL |
| Landmark density | 8.0 | 7.6 | FAIL |
| UI-world cohesion | 7.5 | 7.9 | PASS |
| Readability | 8.0 | 7.8 | FAIL |
| Desirability / product class | 8.0 | 7.6 | FAIL |

### Overall
**7.66 / 10 — significant convergence, but below Stage-1 acceptance.**

---

## What materially improved
1. **World read** — first glance now reads as a real 3D tabletop world, not a generic dashboard.
2. **Board silhouette** — the physical board, gold trim and raised tiles dominate the composition correctly.
3. **Material hierarchy** — lacquer/navy, gold, cyan/magenta emission and enamel tiles form a coherent toy-finance language.
4. **Depth** — foreground board, central stage, midground structures and skyline now create actual spatial layering.
5. **Tablet survival** — iPad composition remains recognizably the same product rather than collapsing into a different mobile dashboard.
6. **Construction integrity** — v7 no longer uses Reference Fixture pixels as runtime scenery.

---

## A-class defects / Stop-Work items

### A1 — Center hierarchy is still over-occupied
The central `币圈大富翁` title, legacy rear sign, crown forms and giant dice all compete in the same narrow depth band. The title partially covers the physical stage/dice instead of behaving like a clean hero installation behind them. The eye does not get the effect drawing's simple hierarchy: **title landmark → market stage/dice → board loop**.

**v8 requirement:** move/rebuild the hero title as a rear architectural landmark, remove visual duplication behind it, restore negative space around the dice and reveal the market platform edge.

### A2 — Character pieces are not yet collectible-grade
The astronaut/animal/NFT/bull family is differentiated semantically, but several pieces still read as procedural assemblies with similar body proportions. The effect drawing's characters are hero assets with distinct silhouettes and toy identities.

**v8 requirement:** strengthen each piece's silhouette, head/body proportion, face/visor treatment, signature accessory, material separation and pedestal read. At least three of the four pieces must be identifiable by silhouette alone.

### A3 — Background city is dense but not authored enough
The city has good density and color rhythm, but many buildings still read as repeated stacked slabs/shelves. It lacks enough large iconic shapes to make the skyline feel deliberately composed rather than procedurally filled.

**v8 requirement:** reduce repeated shelf towers; introduce 3–4 unmistakable hero structures (exchange crown, BTC monument, ETH crystal, market terminal / mining rig) with different height profiles and silhouettes; create clearer near/mid/far spacing.

### A4 — Readability loses to glow in the center
The center's gold/white luminance is high enough that the Chinese logo, dice pips and stage details merge in the brightest region. Some tile labels are also small relative to the visual density.

**v8 requirement:** lower local bloom/point-light dominance around the title/dice, darken the title backing architecture, and protect dice/tile contrast.

---

## Stage decision
**Stage 1 = FAIL.**

Do not proceed to roll interaction/full gameplay integration. Build `candidate-v8` only against A1–A4, then produce the same exact-build desktop+iPad evidence and re-run independent supervision.
