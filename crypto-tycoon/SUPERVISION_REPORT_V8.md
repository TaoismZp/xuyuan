# Crypto Tycoon — Independent Supervision Report v8

## Verdict
**FAIL — Stage 1 remains closed.**

v8 improved environmental authorship and collectible-token differentiation, and fixed the iPad roll-control wrapping. But the center hierarchy is still not acceptable: the legacy stage sign was nested inside the original stage rather than at the root, so the v8 root-level cleanup did not remove it. The resulting active view contains a **rear hero title + legacy front plaque + globe + dice** competing in one focal zone.

This is a construction defect, not a matter of taste. The next candidate must perform center subtraction before any further asset addition.

---

## Binding Chain
- Protocol: `wish-delivery/versions/v7.6.md`
- Controlling blueprint at v8 supervision trigger: `crypto-tycoon/BUILD_BLUEPRINT_V5.md`
- Vision Fixture: `crypto-tycoon/REFERENCE_FIXTURE.md`
- Candidate: `candidate-v8`
- Candidate/evidence commit: `75df04640dd45bb5a331471d486e362c797764a6`
- Supervisor workflow run: `41564424681`
- Evidence artifact: `crypto-candidate-supervisor-evidence-v8`
- Artifact ID: `13197563915`
- Artifact digest: `sha256:50f26c4f199cbfda0d78d1cd7d1d4ec604af3dbd82a7399fda3b5436ae205723`
- Evidence surfaces: desktop 1672×941, iPad landscape 1194×834
- Reference substitution: **not detected**

---

## Scorecard
| Category | Minimum | v8 score | Result |
|---|---:|---:|---|
| Composition | 8.0 | 7.7 | FAIL |
| Spatial depth | 8.0 | 8.3 | PASS |
| Authored forms | 7.5 | 7.7 | PASS |
| Material hierarchy | 7.5 | 8.1 | PASS |
| Lighting / separation | 7.5 | 7.8 | PASS |
| Character quality | 7.5 | 7.2 | FAIL |
| Landmark density | 8.0 | 8.0 | PASS |
| UI-world cohesion | 7.5 | 8.0 | PASS |
| Readability | 8.0 | 7.8 | FAIL |
| Desirability / product class | 8.0 | 7.8 | FAIL |

**Overall: 7.84 / 10 — improved, but below Stage-1 acceptance.**

---

## Improvements confirmed
1. New mining-rig and ring-tower silhouettes reduce the sense of a purely repeated shelf skyline.
2. NFT/robot and horned token silhouettes are more differentiated.
3. Board/material/light language remains coherent and commercial-looking.
4. iPad preserves the same world and `掷骰子` no longer breaks into two lines.
5. Reference Fixture pixels remain absent from runtime.

---

## A-class defects

### A1 — Center still has four competing heroes
The legacy `stage/sign` lives inside the original center stage (`stage.position.y≈0.86`, sign local `y≈3.55,z≈0.45`), so v8's root-child filtering could not remove it. The rear v8 title therefore sits behind another plaque. The globe and dice then create two more focal masses.

**v9 requirement:** target the actual nested stage structure directly; hide the legacy sign; reduce/lower the globe; leave the rear Chinese hero title and physical dice as the two primary reads.

### A2 — Character quality is close but still uneven
NFT/robot and horned token improved most; astronaut remains overexposed and the brown animal piece still reads more like a generic procedural toy than a premium collectible.

**v9 requirement:** reduce over-hot key lighting on foreground pieces; preserve visor/face contrast; strengthen material color separation rather than adding more small geometry.

### A3 — Do not add more city assets
Landmark density has reached the minimum. More objects would now reduce readability. v9 should be a subtraction/lighting pass only.

---

## Stage decision
**Stage 1 = FAIL.**

Build v9 as a center-cleanup and character-readability pass only. No gameplay expansion and no new city landmark inventory.