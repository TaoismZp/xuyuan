# Backend Capability / Skill Proof — Personal Site v1

## Capability gap

The accepted frontend is a static personal website. The missing capability is an owner-only publishing surface that works on iPhone/iPad, stores long-form content durably, and updates the existing frontend without redesigning it.

## Candidate search and actual reading

Candidates reviewed: Sveltia CMS, Decap CMS, Payload CMS, Sanity/Tina-style hosted CMS, and a custom Supabase admin.

The official Sveltia CMS skill/reference set was read from `sveltia/ai-tools`, including the backend/authentication and content-modeling references. The relevant supported architecture is GitHub backend + repository-owned Markdown + optional `root_dir` for monorepos + access-token or OAuth authentication.

## Static review

- **Sveltia CMS** — static admin, Git-backed, official AI skill, no CMS database/runtime, GitHub token auth available, `root_dir` fits this monorepo.
- **Decap CMS** — Git-backed and mature, but production GitHub authentication generally introduces an OAuth/helper path and its mobile editor is less well adapted to this task.
- **Payload CMS** — strong admin/auth/versioning, but requires runtime + database; overbuilt for a one-author long-form site.
- **Sanity/Tina** — good editing UX, but introduces an external content platform as a central dependency/source of truth.
- **Custom Supabase admin** — maximal control, but requires us to build auth, schema, editor, CRUD and media management ourselves.

## Representative spike

Same task on a 390×844 mobile viewport:

1. Open CMS.
2. Enter the content library.
3. Create a Chinese long-form entry with title, summary, tags, date and multi-paragraph body.
4. Save/publish it.
5. Return to the collection and verify the title exists.

### Sveltia

- Test-repo login rendered correctly.
- Content library rendered correctly.
- New-entry editor was a true single-column mobile layout.
- No horizontal overflow in the editor.
- Representative entry saved successfully and appeared in the collection.

### Decap

- After stabilizing manual initialization (`load_config_file: false`), the content library rendered correctly.
- Representative entry also saved successfully after exercising the two-step Publish → Publish now action.
- The 390px new-entry editor retained a desktop/two-pane geometry and produced substantial horizontal overflow while composing the article.

## Head-to-head decision

**Winner: Sveltia CMS + GitHub.**

Reason: both candidates can persist the content, but Sveltia satisfies the actual owner experience on the target mobile surface with materially less layout friction while keeping Git/Markdown as the canonical content store. It also requires fewer production moving parts for a single technical owner because access-token login can be used without standing up an OAuth service.

## Minimum stack lock

1. Sveltia CMS static `/admin/` surface.
2. GitHub backend targeting `TaoismZp/xuyuan`.
3. `root_dir: personal-site-v1` so the CMS sees only this site.
4. `auth_methods: [token]` for v1; no token is ever committed or embedded in the public site.
5. Markdown/frontmatter files under `content/posts/` are the canonical article store.
6. A deterministic Node static builder renders the accepted public frontend from those files.
7. GitHub Actions builds and deploys the public surface.

This is the locked backend stack for v1. Any replacement now requires new representative evidence, not preference.
