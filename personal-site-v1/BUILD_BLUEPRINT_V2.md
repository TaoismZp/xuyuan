# Build Blueprint v2 — Minimalist personal site

Vision binding: `VISION_FIXTURE_V2.md`

## System decomposition
- Home: identity hero, latest essays, long-term projects
- Essays index: editorial archive + simple tag filter
- Article: title/dek/body, reading progress, share action
- Projects: two long-term project narratives
- About: concise personal statement
- Shared shell: header, footer, typography, spacing, rules, focus states

## Implementation mapping
- Hero scale from selected concept → large serif H1, no image dependency
- Olive signal → links/active nav/progress/section slash only
- Editorial index → rows divided by 1px rules; no cards
- Project presentation → two-column typographic split on desktop, stacked on phone
- Reading surface → max measure ~46rem, Chinese serif body, >=18px mobile

## Asset manifest
No external imagery required for v2. This is intentional: typography and spacing must carry the design. No external font or image URL is needed for the frontend candidate.

## Build sequence
1. shared tokens + shell
2. homepage vertical slice at 1440 and 390
3. article surface
4. archive/project/about surfaces
5. interaction + responsive checks
6. browser screenshots
7. user visual approval gate

## Acceptance blueprint
- no horizontal overflow at 1440/390
- all pages have semantic header/main/footer and H1
- nav/button targets >=44px
- article mobile body >=18px
- archive filter and article progress still function
- screenshot comparison must look like the selected third concept: ivory, black, olive, typographic, no card/dashboard regression
- backend remains not authorized until user reviews the real frontend screenshots
