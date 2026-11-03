# Vision Fixture — TaoismZp Longform v2

Identity: `vision-longform-v2-2026-11-03-a`

## Primary perceptual goal
A personal publication, not a generic blog template. The first screen should feel like a quiet, expensive printed journal translated to the web: strong typography, generous whitespace, almost no chrome, and a clear sense that the writing is the product.

## First-impression contract
Within 3 seconds the reader should understand:
1. this is one author's longform publication;
2. the newest essay is the primary object;
3. reading, not navigation, is the dominant activity;
4. the site is deliberate, calm, and editorial rather than social-media-like.

## Visual language
- Warm paper background, near-black ink, restrained accent only for interaction and metadata.
- Chinese-first typography with system fonts; no decorative webfont dependency.
- 68–76ch article measure on desktop; larger line-height and generous paragraph rhythm.
- Strong editorial hierarchy: masthead → issue/date → headline → deck → body.
- Hairline rules, small caps/letter-spacing for metadata, no cards-with-shadows UI kit aesthetic.
- Motion limited to subtle hover/focus transitions and reading progress.

## Home screen
- Masthead: `TaoismZp / 长文`.
- One featured essay occupies the visual center.
- Below: a clean chronological archive, tags only as secondary metadata.
- A small `写作台` entry exists for the owner but never competes with the reading surface.

## Article screen
- Headline is the largest object.
- Deck, date, reading time, tags are readable but quiet.
- Sticky top progress line.
- Body supports headings, blockquotes, lists, code, horizontal rules, links.
- End matter: published date, tags, copy/share, next/previous essay.

## Authoring screen
- Feels like a publishing desk, not an admin dashboard.
- Explain the one-step publish path clearly.
- Draft fields: title, subtitle, tags, body.
- `发布到 GitHub` opens the repository's publish form with prepared content where browser support allows; otherwise the form remains the canonical secure path.

## Responsive target
- iPhone Safari: no horizontal scroll; 20–22px body size; safe-area aware; tap targets >= 44px.
- iPad Safari: article measure stays narrow enough to read; side gutters expand.
- Desktop: no over-wide text; archive uses available width without becoming a dashboard.

## Anti-goals
- No Medium/Substack clone styling.
- No dashboard/sidebar layout.
- No fake engagement counters, comments, likes, trending badges.
- No hero stock imagery.
- No gradients, glassmorphism, excessive rounded cards, or template-like component chrome.
- No dependency on localhost, JS frameworks, external fonts, or a build service for reading.

## Acceptance anchors
- A first-time reader can open the public URL and reach an essay in <= 2 taps.
- The page remains useful with JavaScript disabled except for search/filter conveniences.
- The primary essay remains readable at 320px width and 200% text zoom.
- Publication path never exposes a GitHub token in browser code.
