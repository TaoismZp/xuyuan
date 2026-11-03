# Backend Build Blueprint — Personal Site v1

Identity: `backend-blueprint-personal-site-v1-2026-11-03-a`
Workflow fixture: `backend-workflow-personal-site-v1-2026-11-03-a`
Backend capability lock: hosted Pages CMS + Git Markdown + repository-owned static compiler.

## System decomposition
- `.pages.yml`: owner-facing content schema for hosted Pages CMS.
- `personal-site-v1/content/essays/*.md`: durable Markdown source with YAML front matter.
- `personal-site-v1/scripts/build_content.py`: deterministic-ish compiler from source to accepted frontend shell.
- `personal-site-v1/templates/article.html`: article Read-mode template.
- `personal-site-v1/assets/content.css`: Markdown-specific extensions to the accepted frontend system.
- `build-personal-site-content.yml`: source-change compiler + generated-artifact commit.
- `deploy-pages.yml`: public-only staging; source Markdown, CMS config and build internals are excluded from Pages artifact.
- Public outputs: homepage recent list, archive/filter rows, article pages, `feed.xml`, `sitemap.xml`, published-only manifest.

## Content contract
Required: title, slug, date, draft, body.
Optional: dek, tags.
Slug must be lowercase ASCII kebab-case and match the source filename.
Raw HTML in Markdown is disabled by the renderer; core CommonMark is supported.

## Build rules
- `draft: true`: validate source but exclude from every public output.
- `draft: false`: render article and public indexes.
- removed/unpublished slugs: remove stale generated article directory based on the prior published manifest.
- no CMS runtime on reader requests; readers receive static HTML/CSS/JS only.
- no content source is copied into the GitHub Pages artifact.

## Tooling
- `markdown-it-py==4.2.0` for CommonMark parsing with raw HTML disabled.
- `PyYAML==6.0.3` with `safe_load` for front matter.
- GitHub Actions for compilation and delivery.

## Verification sequence
1. Validate `.pages.yml` points at the real content path and fields.
2. Build with the committed draft fixture: draft must not appear anywhere public.
3. In an isolated copy, treat the same fixture as published and render it into the accepted article shell.
4. Browser-check generated article on desktop/mobile.
5. Exercise edit, unpublish and stale-page cleanup synthetically.
6. Release to main; source-change build must generate published outputs before Pages deploy.
7. Verify public Pages artifact contains generated HTML but not content source.
8. Complete real Pages CMS owner authorization and one authenticated edit/save cycle.

## Stop-work conditions
- If Pages CMS requires a browser PAT as the default hosted path, stop and return to capability selection.
- If build changes require a frontend redesign, stop and return to the accepted frontend contract.
- If a draft source becomes reachable through the Pages URL, Delivery FAIL.
- If an edit can publish stale/old generated output, Binding Chain FAIL.
