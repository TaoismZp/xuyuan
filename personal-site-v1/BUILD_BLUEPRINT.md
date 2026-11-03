# Build Blueprint — Personal Site v1 / Frontend

Identity: `blueprint-personal-site-v1-2026-11-03-a`
Vision: `vision-personal-site-v1-2026-11-03-a`
Backend: explicitly out of scope for this phase.

## System decomposition

### Public surfaces
- `/personal-site-v1/` — homepage / Experience mode
- `/personal-site-v1/essays/` — longform archive / Read mode
- `/personal-site-v1/essays/sample/` — representative article reader / Read mode
- `/personal-site-v1/projects/` — books and long-term projects / Experience mode
- `/personal-site-v1/about/` — concise personal context

### Shared frontend system
- `assets/site.css` — tokens, typography, responsive layout, states
- `assets/site.js` — only progressive enhancements: reading progress, mobile nav state, archive filtering; content remains usable without JS
- semantic HTML fixtures for all content; no API, database, auth, CMS, publish workflow or admin

## Reference-to-implementation mapping
- Person-first promise → authored hero statement in real HTML text; never screenshot/image.
- Editorial credibility → semantic essay rows and serif title/body treatment; not card components.
- Decision-notebook character → structural rules, date/category metadata, restrained cobalt signal; no fake terminal or trading chart.
- Projects → large typographic fields with status/progress expressed in language, not generic dashboard cards.
- Mobile → explicit single-column composition and >=44px controls.

## Asset manifest
- No external raster hero assets.
- No generated imagery required.
- System/local font stack only for this first frontend to eliminate font-loading dependence; typography is validated on Apple/WebKit-oriented stacks.
- Minimal inline SVG only if a functional icon is needed; no decorative icon library.

## Capability plan
- Direction: Impeccable `Experience` homepage/projects + `Read` essays.
- Anti-template critique: Anthropic `frontend-design` principles before and after build.
- Micro-craft: Make Interfaces Feel Better after the main visual system is stable.
- Audit: Vercel Web Design Guidelines + automated semantic/responsive checks.
- UI/UX Pro Max: targeted fallback only, not visual-world selector.

## Build sequence
1. Official homepage Vision Fixture (high-fidelity, fixture content only).
2. Screenshot at desktop 1440 and mobile 390; inspect against Must-match.
3. If fixture passes, implement a separate production frontend shell (no verbatim reuse of fixture markup).
4. Implement homepage, archive, article, projects, about.
5. Add progressive enhancement JS.
6. Micro-craft pass.
7. Static/accessibility/responsive audit.
8. Public same-surface deployment and WebKit verification.
9. Independent supervision report; A-class defects return to construction.
10. Frontend Acceptance. Only after frontend ACCEPTED may backend capability procurement start.

## Acceptance blueprint

### Vision / comparative
- First viewport communicates a person before a content product.
- No generic SaaS-card wallpaper, finance cliché, or broadsheet cosplay.
- Longform, projects, about all feel native to one world.

### Functional
- All nav paths work without JS.
- Archive filter degrades to full list without JS.
- Sample article is readable and share/back controls work.
- Reading progress enhancement never blocks reading.

### Responsive
- 390px, 768px, 1440px: no horizontal overflow.
- Tap targets >=44px where interactive.
- Hero/body text do not clip or create orphaned unusable lines.

### Accessibility
- Semantic landmarks/headings.
- Visible focus.
- Contrast appropriate for text/control states.
- Reduced-motion respected.
- No interaction relies on hover only.

### Performance/construction integrity
- No remote runtime dependency required to render core content.
- No reference screenshot/mockup embedded in production.
- Minimal JS and no heavy framework runtime in this phase.

## Delivery surface for frontend phase
Real GitHub Pages public URL under `/personal-site-v1/`, verified with WebKit profiles representing iPhone, iPad and desktop. This is a frontend acceptance surface, not yet the final full product because backend authoring is intentionally absent.
