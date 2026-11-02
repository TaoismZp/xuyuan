# Crypto Tycoon — Supervisor Report v3

## Candidate
- supervised build: `candidate-v3.html`
- evidence workflow run: `41498340584`
- evidence commit: `40247dd4964c394d111f70fcf6f3d1c681af7642`
- exact-version gate: `candidate-v3`
- reference substitution: PASS
- desktop + iPad capture: PASS

## Decision
**FAIL — Stage 1 remains open.**

## What improved versus v2
- tiles now have real semantic/story panels rather than only icons;
- center foreground has real hero dice and finance props;
- city has vertical facade ribs and distinct finance signage;
- hero/landmark scale moved closer to the Reference Fixture.

## Regression caught by Supervisor
The new lighting pass exceeded the material value range. Light tiles, dice, astronaut/rocket surfaces and several labels clip toward white. This harms readability and toy-material separation and is a direct regression versus v2.

This is a useful monitor failure: progress in density/readability intent cannot compensate for a lighting regression.

## Stop-work correction
No new assets or gameplay may be added in v4. Only:
1. remove/reduce the extra v3 light energy;
2. make tile story panels color-stable and readable under the final lighting rig;
3. re-check desktop/iPad screenshots.

## Status
Reference Non-Substitution: PASS  
Construction Integrity: PASS  
Visual Vertical Slice: **FAIL**
