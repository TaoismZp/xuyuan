# Durable Task State — Personal Site v1

- status: LIVE / DISTRIBUTION_METADATA_ACCEPTED
- last_good_checkpoint: `01c51bae552b142d03ddcb483cfaad1b8eb957e3`
- public_acceptance: GitHub Actions run `41767849763` — **PASS** (public HTTP + iPhone/iPad/desktop WebKit)
- latest_accepted_public_surface: https://taoismzp.github.io/xuyuan/personal-site-v1/
- first_published_essay: 《天才交易员为何注定陨落》 — https://taoismzp.github.io/xuyuan/personal-site-v1/essays/genius-trader/
- original_article_source: `/作者第二大脑/01_成稿原文/天才交易员为何注定陨落_用户原稿_2026-10-22.md`; source_sha256 `312cf1ebad852621edd72078d7cce2f653da6e5072f12e0199787e823e5e23b4`
- production_markdown: `content/posts/genius-trader.md`; do not edit original essay as part of infrastructure changes.
- live_distribution: canonical / Open Graph / Twitter summary / RSS `feed.xml` / sitemap `sitemap.xml`; only published articles enter the public feed and index.
- frontend_vision: third user-selected minimalist direction (warm ivory, near-black, restrained olive); preserved.
- current_gate: OWNER CMS AUTHENTICATED WRITE (user-only).
- unverified_step: first real Sveltia login and save using owner's restricted GitHub token; cannot be simulated by connector-based publication.
- owner_secret_rule: token must only be entered in CMS login UI; never sent to ChatGPT, files, or commits.
- privacy_rule: GitHub repository is public, so a `draft` markdown commit is **not** private even though draft pages are omitted from the public site, RSS and sitemap.
- delivery_boundary: Pages artifact ships allowlisted public pages/assets only; no canonical Markdown, build scripts or internal reports.
- next_executable_action: owner tests authenticating at `/personal-site-v1/admin/` and editing one published essay; verify token-authenticated commit → Pages → actual public page, or continue preparing more authorized longform publications via connected GitHub.
- updated_at: 2026-11-04
