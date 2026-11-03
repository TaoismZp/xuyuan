# Build Blueprint — TaoismZp Longform v2

Identity: `blueprint-longform-v2-2026-11-03-a`
Bound Vision: `vision-longform-v2-2026-11-03-a`

## 1. System decomposition

### Reading surface
- `index.html`: publication home + archive.
- `article.html`: article reader.
- `styles.css`: shared editorial design system.
- `app.js`: archive search/filter, article loading, reading progress, share/copy.

### Content layer
- `posts/index.json`: ordered post metadata.
- `posts/<slug>.json`: article payload with pre-rendered safe HTML body.
- `source/<slug>.md`: canonical Markdown source kept for author/edit history.

### Publishing surface
- `write.html`: owner-facing publishing desk.
- `.github/ISSUE_TEMPLATE/publish-longform.yml`: secure publish form.
- `.github/workflows/publish-longform.yml`: transforms an approved publish issue into committed source + rendered article + updated index.
- `longform-v2/scripts/publish_issue.py`: deterministic parser/renderer, no third-party Python packages.

### Verification
- `.github/workflows/verify-longform-v2.yml`: candidate/static checks on push.
- `.github/workflows/verify-longform-v2-public.yml`: post-deploy public checks against GitHub Pages.
- `longform-v2/tests/verify_static.py`: semantic/HTML/content/security checks.
- `longform-v2/tests/verify_public.py`: public URL delivery checks and responsive markup invariants.

## 2. Reference-to-implementation mapping
- Warm paper / ink world → CSS tokens, not an image layer.
- Editorial hierarchy → semantic HTML + type scale + whitespace system.
- Narrow longform measure → `max-width` constraints on prose.
- Quiet archive → table/list-like editorial rows, no generic card grid.
- Reading progress → 2px fixed progress bar calculated from document scroll.
- Secure publishing → GitHub Issue Form + Actions; never browser-embedded token.

## 3. Asset manifest
Required assets: none. Visual quality must come from typography, spacing, rules, and interaction. This is intentional: no decorative stock images, remote fonts, or icon packs.

## 4. Capability / Skill plan
Production bottleneck: **editorial reading quality + secure low-friction publishing**, not raw coding.

Candidates:
A. Existing `essays/` spike: client-side Markdown fetch + hand-coded static UI.
B. Jekyll/theme route: stronger conventional blog tooling but adds theme/build coupling and makes the reading surface look template-derived unless heavily overridden.
C. Bespoke static publication + GitHub Issue CMS: no framework dependency, full control over typography, secure authoring via GitHub identity, deterministic generated article payloads.

Representative evidence:
- A already proved public static deployment and basic reading, but did not prove design quality or a robust owner publishing loop.
- B is rejected for this project because the key requirement is not theme velocity; it adds a build/runtime convention without reducing the hardest product risk.
- C is selected as the minimum stack because it directly solves both bottlenecks while preserving a simple delivery surface.

Minimum stack lock: semantic HTML + CSS + vanilla JS + Python stdlib + GitHub Issues/Actions/Pages.

## 5. Build sequence
1. Lock editorial tokens and one vertical slice: home → article.
2. Build reading surface with sample article.
3. Build publishing Issue Form and deterministic renderer.
4. Add static verification.
5. Independent supervision against Vision/Blueprint.
6. Merge exact candidate to `main`.
7. Deploy exact commit to Pages.
8. Run public verification against exact deployment.
9. Create Acceptance Report bound to exact identities.

## 6. Acceptance blueprint
Hard gates:
- Functional: home, article, archive search, share/copy, publish issue form link.
- Security: no secret/token/client credential in published code.
- Delivery: GitHub Pages returns 200 for home/article/post payload/write surface.
- Experience: no horizontal overflow by design; safe mobile tap targets; readable measures.
- Perceptual: matches Vision Fixture hierarchy and anti-goals.
- Construction integrity: no reference screenshot/image embedded as product.
- Publishing loop: publish workflow can parse a synthetic issue body and generate valid post files in test mode.
- Exact identity: final reports bind to the same commit deployed publicly.

## 7. Stop-work criteria
- If public deployment serves a different commit than the candidate, stop and rebind evidence.
- If publishing requires a browser token or manual file editing, fail the core loop.
- If first screen becomes a generic card/dashboard UI, fail perceptual gate.
- If verification becomes more complex than the product, simplify the verifier.
