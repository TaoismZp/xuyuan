# Reading Experience v2 — Implementation and Acceptance Contract

## Product problem

The v1 long-form page supported reading progress and sharing, but did not expose any chapter navigation. Its sidebar text `阅读模式` was not an actual interactive mode. A 15-minute essay with several H2 sections should allow the reader to quickly jump back to earlier arguments without adding dashboard-style visual clutter.

## Locked visual direction

Preserve the selected third minimalist direction: warm paper, restrained olive accent, near-black type, hairline separators and narrow article measure. Do not rewrite source essays, introduce promotional cards, change the CMS or modify the content files.

## Implemented reader flow

1. Static generator gives each Markdown `##` heading a deterministic `section-01`, `section-02`, etc., using Markdown-it tokens, not unsafe raw HTML.
2. Desktop and tablet: quiet numbered outline at the left, aligned with the essay body; current-section state follows the reader using passive scrolling.
3. Phone: native accessible `<details>` chapter menu, closed by default, with 44px tap target; selecting a chapter closes the menu and navigates to an ordinary fragment URL.
4. At article end, return to the entire archive; if there is a following, older published article, the builder also inserts a next-essay link.
5. Source Markdown, titles, content provenance, canonical URLs, RSS/sitemap, CMS and publishing permissions remain unchanged.
6. Reduced-motion preference disables the smooth-scroll effect.

## Gates

- Static CI: generated chapter IDs, internal links, mobile/desktop outline, end-of-article link, no misleading read-mode label.
- Browser CI: 390px mobile can expand and jump to a section; desktop 1440px can navigate; both retain reading font sizes and no horizontal overflow.
- Independent supervisor: ensure style remains the approved editorial visual class vocabulary and no synthetic article leaks.
- Public WebKit: iPhone, iPad and desktop follow the same actual public article and verify chapter jump, touch-target size, end link, and old full-article scrolling.
- Delivery: all browser and HTTP checks must match the deployed commit SHA. No authenticated CMS-write assertion, since only the owner's token can perform it.

## Explicit exclusions

No visual redesign, no rewrite of `genius-trader.md`, no new article invented for the public site, no tracking service, no local-storage reading history and no unverified claim about user-owned CMS login.
