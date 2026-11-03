# Frontend Skill Bakeoff Report — Personal Site v1

## Evidence identity
- Bakeoff branch: `personal-site-frontend-bakeoff`
- Candidate commit: `d955295522c256f6cc98c2f19be003646718dd4b`
- Screenshot workflow run: `41586602900` — PASS
- Evidence artifact: `13207614328` (`personal-site-frontend-bakeoff-41586602900`)
- Same content and functional scope were used for all candidates; desktop 1440px and mobile 390px captures were generated from the exact commit.

## Static review

### Baseline / no external skill
Useful as control only. It produces a clean, legible portfolio/blog, but the default card grammar and generic role-stack hero do not create a sufficiently specific personal identity.

### Anthropic `frontend-design`
Strengths: subject-grounded design, strong anti-template checks, typography as personality, restraint, explicit self-critique before coding. The spike creates an editorial intellectual identity and the strongest longform credibility.
Risk: if applied literally, it can itself converge on the editorial/broadsheet style that the skill warns against. Use as an anti-slop constraint, not as the sole visual world.

### Impeccable
Strengths: explicit surface modes (`Experience`, `Read`, `Operate`, `Persuade`), rendered-result verification, new-work direction contract, separate critique/finish review, production-minded craft. The spike is the clearest at communicating a person first, with longform and projects as evidence of the person rather than the product itself.
Risk: the first spike spends too much visual force in the oversized role lockup and outer blue frame. Those are proof of distinctiveness, not final motifs.

### UI/UX Pro Max
Strengths: broad searchable design-system and UX database, accessibility/touch/responsive priorities, stack-specific guidance.
Risk: catalog selection encourages pattern assembly. In this representative task the output became rounded cards + dashboard-like grouping, the weakest match for a personal intellectual site even though it is structurally competent.

### Make Interfaces Feel Better
Not a direction competitor. Strong as late-stage micro-craft: optical alignment, hit areas, type wrapping, motion restraint, icons, shadows/radii, interaction state review.

### Vercel Web Design Guidelines
Not a direction competitor. Strong as a final independent web-interface/accessibility audit.

## Weighted head-to-head

| Criterion | Weight | Baseline | Anthropic | Impeccable | UI/UX Pro Max |
|---|---:|---:|---:|---:|---:|
| Personal identity / first impression | 25 | 15 | 22 | 24 | 17 |
| Personal site, not blog, IA | 20 | 14 | 18 | 19 | 14 |
| Longform editorial credibility | 15 | 10 | 15 | 13 | 10 |
| Visual craft / typography | 15 | 10 | 14 | 15 | 11 |
| Mobile / touch | 10 | 8 | 9 | 8 | 10 |
| Accessibility / restraint | 5 | 4 | 5 | 4 | 5 |
| Future extendability | 10 | 7 | 8 | 9 | 9 |
| **Total** | **100** | **68** | **91** | **92** | **76** |

## Representative evidence findings
- Baseline: legible and responsive, but visually interchangeable with many generic personal/blog templates.
- Anthropic: strongest editorial credibility and mobile reading rhythm; headline and essay list feel authored rather than assembled.
- Impeccable: strongest identity and clearest Experience-mode personal-site framing; desktop hierarchy is memorable and projects feel like part of the person. Mobile remains coherent, but role typography is too poster-like to keep verbatim.
- UI/UX Pro Max: best touch/system discipline, but rounded card repetition makes the person feel secondary to a generic UI system.

## Minimum high-gain stack lock

1. **Primary direction / world:** Impeccable — use `Experience` for homepage and project surfaces; `Read` for essay archive/article surfaces. Use new-work direction contract and finish-reviewer logic.
2. **Distinctiveness / restraint constraint:** Anthropic `frontend-design` — every visual choice must be grounded in the subject and must pass an anti-template critique before implementation.
3. **Micro-craft pass:** `make-interfaces-feel-better` — only after the main direction is built.
4. **Independent audit:** Vercel `web-design-guidelines` — final web/accessibility review.
5. **UI/UX Pro Max:** **not in the default stack**. Retain as a targeted lookup tool only if a specific accessibility/touch/stack gap appears; do not let its catalog choose the visual world.

## Direction constraints for the official Vision Fixture
- Preserve Impeccable's person-first hierarchy, but remove the poster gimmicks: no giant three-word overlap, no thick decorative frame.
- Preserve Anthropic's editorial legibility, but avoid broadsheet cosplay and generic `BOOK / IN PROGRESS` labels.
- The memorable element should be one authored statement or spatial idea, not a decorative effect.
- Longform is a first-class module, not the homepage identity.
- Projects/books, about, and future notes/media must have equal architectural legitimacy.
- Mobile is a first-class surface, not a collapsed desktop.

**Capability/Skill Proof Gate: PASS. Minimum stack locked.**
