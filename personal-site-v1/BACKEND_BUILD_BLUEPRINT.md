# Backend Build Blueprint — Personal Site v1

## System decomposition

### 1. Owner editing surface
`personal-site-v1/admin/`
- Sveltia CMS loaded as a static client application.
- GitHub backend.
- v1 authentication: owner-supplied fine-grained GitHub access token entered in the CMS login surface; never stored in repository code.
- CMS visibility restricted to `personal-site-v1` through `root_dir`.

### 2. Canonical content store
`personal-site-v1/content/posts/*.md`

Frontmatter contract:
- `title` — required string
- `summary` — required text
- `date` — required ISO date/time
- `tags` — optional string list
- `status` — `draft | published | archived`, default `draft`
- `featured` — optional boolean, default false
- body — Markdown, required for publication

The Markdown file is the source of truth. Generated HTML is never the source of truth.

### 3. Static renderer
`personal-site-v1/scripts/build.mjs`

Responsibilities:
- parse frontmatter
- reject malformed required fields
- exclude drafts/archived posts from the public surface
- sort published posts newest first
- derive stable slug from filename
- calculate reading time
- render Markdown with raw HTML disabled
- generate homepage recent-essay rows
- generate full essay archive
- generate one article page per published post
- preserve the accepted typography/classes/assets

### 4. Existing static pages
The accepted static pages remain hand-authored:
- projects
- about
- CSS/JS assets

The builder must not redesign them.

### 5. CI / deployment
GitHub Actions:
1. checkout
2. install pinned static-build dependencies
3. run content validation/build
4. browser-check generated homepage/archive/article on desktop + phone
5. upload the repository as Pages artifact after generated pages replace the ephemeral checkout copies
6. deploy to GitHub Pages

## Reference-to-implementation mapping

- Sveltia GitHub backend → `admin/config.yml backend.name: github`
- monorepo isolation → `backend.root_dir: personal-site-v1`
- owner-only simple authentication → `backend.auth_methods: [token]`
- Sveltia blog/news content model → `posts` entry collection with status, summary, date, tags and rich-text body
- accepted frontend Vision Fixture → builder emits the same `.site-header`, `.hero`, `.essay-row`, `.archive-row`, `.article-head`, `.article-body` class vocabulary

## Asset manifest

Required:
- existing `assets/site.css`
- existing `assets/site.js`
- Sveltia CMS client script
- Markdown content files

Optional:
- uploaded media under `media/uploads/`

No stock imagery, charts, dashboard chrome, or decorative CMS assets are required for the public site.

## Capability / skill plan

- Frontend direction: already locked through Taste Skill v2 comparative work and user approval.
- Backend: Sveltia CMS official skill/reference set is the implementation guide.
- Build renderer: deliberately small custom integration layer; it exists only to map repository Markdown into the locked frontend.
- Verification: Playwright browser checks in CI, simpler than the product and focused on the actual publish/read loop.

## Build sequence

1. Add production Sveltia `/admin/`.
2. Add canonical content directory and schema example that remains non-public.
3. Add deterministic renderer and dependency manifest.
4. Add build/validation CI on the feature branch.
5. Verify a synthetic published fixture generated only inside CI: homepage → archive → article.
6. Add production Pages build step.
7. Merge accepted branch to `main` only after independent supervision passes.
8. User-only authentication gate: owner creates/enters a fine-grained GitHub token restricted to this repository.
9. Publish one real acceptance article through the public `/admin/` surface.
10. Verify Git commit → Pages deploy → public article on iPhone/iPad/Desktop.

## Acceptance blueprint

### Functional Reality
- admin loads
- content model exposes all required fields
- a post can be created, edited and saved
- renderer turns a published Markdown file into valid public pages
- draft/archived content never appears publicly

### Delivery Reality
- public `/personal-site-v1/` loads from GitHub Pages
- public `/personal-site-v1/admin/` loads the production CMS
- a CMS save creates/updates the canonical Markdown file in GitHub
- deployment runs from that same content commit

### Experience Reality
- owner editor is usable at 390px without horizontal overflow
- long-form body editor works with touch
- public article remains readable on iPhone/iPad/Desktop

### Perceptual / Comparative Reality
- generated pages remain visually the same product grade as the accepted third minimalist frontend
- backend integration adds no dashboard visual language to the public surface

### Construction Integrity
- no token/credential committed to source
- no generated HTML treated as canonical content
- evidence must bind to the candidate commit being accepted

## User-only blocker boundary

Creating/entering the owner’s fine-grained GitHub token is the first legitimate `BLOCKED_USER` action. Everything before that must be completed without asking the user to handle infrastructure or choose between implementation details.
