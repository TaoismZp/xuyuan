# Crypto Tycoon — Supervisor Correction for v5

## Why this correction exists
`SUPERVISION_REPORT_V5.md` mistakenly evaluated candidate v5 against the older `BUILD_BLUEPRINT_V2.md` thresholds.

The repository already contained a newer construction drawing, `BUILD_BLUEPRINT_V3.md`, which is the controlling blueprint for Stage 1 and raises several predeclared minimums:
- Authored forms: 7.5
- Material hierarchy: 7.5
- Lighting / separation: 7.5
- Character quality: 7.5
- UI-world cohesion: 7.5

A supervisor is not allowed to choose the easier drawing after construction. Acceptance criteria must come from the latest locked blueprint that governed the build.

## Corrected v5 result
Candidate v5 remains a major genuine improvement and passes Reference Non-Substitution, but its previously recorded scores included:
- Authored forms: 7.3 < 7.5
- Character quality: 7.1 < 7.5

Therefore:

**The prior Stage 1 PASS is withdrawn. Candidate v5 = FAIL under `BUILD_BLUEPRINT_V3.md`.**

## Process finding
This is a supervision/process defect, not a rendering defect:

> An acceptance report that does not name and verify the exact controlling blueprint is invalid.

Future supervisor reports must record:
1. controlling blueprint path + blob SHA;
2. candidate commit SHA;
3. evidence artifact/run;
4. thresholds copied from that exact blueprint before scoring;
5. PASS only if every hard minimum is satisfied.

## Construction instruction
Do not start Stage 2 gameplay yet. Continue Stage 1 with the existing v6 visual candidate, focusing on the stricter authored-form / character / UI thresholds, then re-supervise against `BUILD_BLUEPRINT_V3.md`.
