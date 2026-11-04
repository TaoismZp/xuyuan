# Home Editorial v3 — Execution and Acceptance

## Product problem

The live personal site had exactly one real essay, 《天才交易员为何注定陨落》. The homepage displayed it as a plain title/date row; the reader could not understand why it was worth opening. Improve *author recognition* and the first longform reading path while preserving the third user-approved minimalist direction.

## Vision guardrails

- `VISION_FIXTURE_V2.md` is the accepted appearance contract: warm ivory, near-black ink, muted olive, oversized Chinese serif, hairline dividers.
- Keep the original hero title “长期交易，长期写作。” and the two project descriptions.
- Identity phrase “我把钱放进市场，也把判断写下来。” is taken from the earlier author-first vision fixture, not fabricated article prose.
- No dashboard, cards, images, gradients, market charts, badges, trackers, external CSS packages or invented articles.

## Implementation

- In `scripts/build.mjs`, only posts with `status: published` enter the home, archive, RSS and sitemap.
- Pick the newest published post with `featured: true`, otherwise the newest published post.
- Render that article **once** as an editorial text-led entry: real title, real frontmatter summary, existing tags, source date, reading estimate and link.
- Up to three remaining articles stay ordinary essay-index rows; the feature never appears in that list.
- Provide a simple text link to all published essays and a count from canonical Markdown.
- If the published collection is empty, preserve a truthful empty state without a fake feature.
- Existing CMS, archive filter, article text, article section navigation and Pages artifact allowlist remain unchanged.

## Evidence

- Candidate SHA: `3cc289c4da9a51f99edf1445ee719b80b5249288`.
- Independent supervision: GitHub Actions `41817976473`, success.
- Backend and mobile/desktop Chromium build verification: `41817976780`, success.
- GitHub Pages deployment: `41818190430`, success.
- Public iPhone/iPad/desktop WebKit and HTTP acceptance: `41818252467`, **PASS**, same candidate/delivery SHA.
- Acceptance artifact: `personal-site-v1-acceptance-41818252467`.
- Public homepage screenshots were inspected after actual Pages publication: only one real featured essay remains; synthetic `ci-published` fixture exists in test runs only.

## Known boundaries

- A saved draft in the public GitHub repository is NOT private, even if it is excluded from the website.
- Owner-authenticated Sveltia CMS login/edit/save is not yet tested because the owner's token must not be shared with the assistant.
- This iteration improves editorial discoverability, not search ranking or engagement measurement.
