# Backend Capability / Solution Bakeoff Report — Personal Site v1

## Evidence identity
- Accepted frontend delivery: `b82b5bb2496d9b7ccd960f0785e7fde15e86be0a`
- Backend bakeoff representative commit: `0eb4d1b6d224bd13ff08555b210f166dfeecd03b`
- Representative spike run: `41590484877` — PASS
- Common task: one Chinese longform entry with title/dek/slug/date/tags/draft/body, Git history, and a content path consumable by the accepted static frontend.

## Candidate findings

### Pages CMS hosted — WINNER
Pages CMS is explicitly built for GitHub repositories and static/content sites. The hosted version can be used without operating the Pages CMS server/database ourselves. A `.pages.yml` collection can edit Markdown files directly in `personal-site-v1/content/essays`, so the accepted frontend does not need a framework migration. Public real-world Pages CMS configs demonstrate the same collection + rich-text + Markdown pattern for essays.

Auth/operations: the hosted product uses its maintained GitHub authentication path rather than asking the site to store a long-lived browser PAT. The Pages CMS repository is actively maintained; the current 2.1.x release line contains GitHub auth/access fixes. A real owner sign-in/repository authorization is a user-side one-time gate and cannot be faked in CI.

Draft/version model: `draft` is modeled in content and the site build excludes drafts. Every edit lands in Git, so source history and rollback remain repository-native even if the editor service changes later.

### Sveltia CMS — strong runner-up, rejected as default
Sveltia is an excellent lightweight Git-backed CMS and fits static HTML without migration. It also provides a true `/admin`-style experience. The problem is GitHub auth: Sveltia's own current source explicitly says GitHub PKCE authorization is unsupported. Its official authenticator README recommends a personal access token for technical-only GitHub users; a smoother OAuth experience requires deploying a Cloudflare Worker, registering a GitHub OAuth app, managing its client secret, and restricting allowed domains.

That is more auth/operations surface than the product itself needs. Sveltia remains the fallback if owning the admin UI under the site becomes more important than operational simplicity.

### TinaCMS — capable, wrong center of gravity
Tina is Git-backed, has strong schema-driven editing and visual editing, and keeps Markdown/MDX/JSON in Git. Its own Skill says the strongest path is Next.js/React, with Astro support and framework-agnostic usage but reduced visual-editing value. Typical production setup also introduces TinaCloud or a self-hosted serverless backend plus client ID/token configuration.

For this project, adopting Tina would make the already-accepted static frontend bend around the CMS. The representative task does not justify that migration.

### Payload CMS — excellent full CMS, too heavy here
Payload has first-class auth, drafts/versions, rich text and granular access control, but it is a Next.js-native application/backend with a database and deployment runtime. The official one-click production paths pair it with Vercel/Neon/Blob or Cloudflare Workers/D1/R2.

Those features are valuable for a multi-user dynamic application; they are unnecessary operational surface for a single-owner personal site whose durable content should stay in Git Markdown.

### GitHub Issue + Actions — control/fallback
The existing `publish-longform.yml` proves a zero-extra-service publishing transport: owner GitHub identity, Actions, Git commits. It is operationally robust but ergonomically poor for longform authoring, drafts, preview, editing and unpublish flows. It remains an emergency/fallback transport, not the owner-facing CMS.

## Weighted head-to-head

| Criterion | Weight | Pages CMS | Sveltia | TinaCMS | Payload | GitHub Issue |
|---|---:|---:|---:|---:|---:|---:|
| Owner mobile authoring UX* | 25 | 21 | 20 | 20 | 20 | 11 |
| Fits accepted static frontend | 20 | 20 | 20 | 11 | 5 | 20 |
| Secure owner auth / no default browser PAT | 15 | 14 | 7 | 12 | 15 | 15 |
| Draft/edit/version/rollback | 15 | 14 | 13 | 14 | 15 | 9 |
| Operational burden | 10 | 10 | 6 | 6 | 3 | 10 |
| Markdown / structured content | 10 | 10 | 10 | 10 | 5 | 9 |
| Future expansion | 5 | 5 | 5 | 5 | 5 | 3 |
| **Total** | **100** | **94** | **81** | **78** | **68** | **77** |

\*The third-party authenticated editor itself cannot be exercised in CI without the owner's GitHub authorization. These UX scores remain provisional until the real owner connection is completed. This limitation is recorded rather than faked.

## Minimum high-gain backend stack lock
1. **Owner editor/auth:** hosted Pages CMS.
2. **Durable content source:** Git-backed Markdown in `personal-site-v1/content/essays/`.
3. **Content model:** title, dek, slug, date, tags, draft, body.
4. **Build/publish engine:** repository-owned deterministic static build on GitHub Actions; drafts are excluded; published Markdown is rendered into the already-accepted frontend shell.
5. **Version/rollback:** Git history remains source of truth; Pages CMS is replaceable.
6. **Fallback transport:** existing GitHub Issue/Actions path stays separate and is not the normal authoring UI.
7. **No production Sveltia/Tina/Payload runtime** unless a later requirement changes the bottleneck.

## Next gate
Backend construction is authorized. It must now add the root Pages CMS schema, content source, deterministic build, draft exclusion, archive/home regeneration, RSS/sitemap metadata where appropriate, tests, and a real deployment loop without visually redesigning the accepted frontend.

The backend cannot receive final acceptance until the owner performs the unavoidable GitHub authorization for Pages CMS and the real authenticated authoring surface is exercised. Everything before that user-side gate should be completed first.

**Capability / Solution Proof Gate: PASS. Backend stack locked.**
