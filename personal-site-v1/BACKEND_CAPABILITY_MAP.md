# Backend Capability Map — Personal Site v1

## Core user loop

Owner opens a browser on phone or desktop → signs in → creates/edits a long-form post → saves/publishes → content lands in the canonical repository → site rebuilds → the article appears in the existing minimalist frontend.

## Satisfaction variables

1. **Owner publishing friction** — usable from iPhone/iPad, not just a developer terminal.
2. **Preserve the locked frontend** — CMS must not dictate the public-site design.
3. **Content ownership and reversibility** — articles should remain portable files, not be trapped in a vendor database.
4. **Security** — only the owner can publish; no GitHub secret is embedded in the public site.
5. **Operational simplicity** — smallest number of services and moving parts that can satisfy the loop.
6. **Long-form fitness** — Chinese long-form, Markdown/rich text, tags, summaries, draft/publish metadata, media.
7. **Deployment fit** — works with a static public site and repository-driven deployment.

## Candidates

### Sveltia CMS + GitHub
- Official AI skill exists at `sveltia/ai-tools/plugins/sveltia-cms/skills/sveltia-cms/SKILL.md`.
- Static single-page admin; CMS itself needs no database or application server.
- GitHub backend writes content files directly to the repository.
- For a single technical owner, restricted access-token login is the smallest remote-auth path; OAuth can replace it later without changing the content model.
- `test-repo` backend enables representative UI/config testing before auth exists.
- Fit: **very high**.

### Decap CMS + GitHub
- Mature Git-based CMS and close conceptual fit.
- GitHub production login normally requires an OAuth server / hosted Turbo / Netlify auth path; local testing can use `test-repo` or a local proxy.
- Adds one more authentication dependency than Sveltia token login for a one-person site.
- Fit: **high**, but more moving parts for this specific owner-only case.

### Payload CMS
- Excellent full admin, auth, drafts, versions and media.
- Requires a Node runtime plus a compatible database and hosting.
- Solves materially more than the current site needs and would force a larger architecture change.
- Fit: **medium**; capability-rich but overbuilt.

### Sanity / Tina
- Strong hosted editing experiences.
- Introduce an external content platform/account/project as the source of truth.
- Weaker match for the goal of keeping essays as simple repository-owned files.
- Fit: **medium**.

### Custom Supabase admin
- Maximum control.
- Requires designing auth, schema, editor, storage, CRUD and deployment ourselves.
- Highest engineering surface with little benefit for a single-author publication.
- Fit: **low for v1**.

## Representative task

Same task for Sveltia and Decap:

> On a 390px mobile viewport, open the CMS, create a post with title, summary, tags, publish date and a multi-paragraph Chinese body, and reach a valid save/publish state without changing the public frontend.

## Initial hypothesis

Sveltia is the leading candidate because it preserves Git as the canonical content store while adding only a static `/admin/` interface. This is a hypothesis until the representative spike is run.
