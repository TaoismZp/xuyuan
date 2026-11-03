# Backend Workflow Fixture — Personal Site v1

Identity: `backend-workflow-personal-site-v1-2026-11-03-a`
Frontend dependency: accepted Delivery Identity `b82b5bb2496d9b7ccd960f0785e7fde15e86be0a`.

## Owner outcome
The owner does not manage HTML, deploy scripts, or Git commits by hand.

Normal publishing path:
1. Sign in to hosted Pages CMS with the owner's GitHub identity.
2. Open repository `TaoismZp/xuyuan` and the `长文` collection defined by `.pages.yml`.
3. Create or edit title, optional dek, URL slug, date, tags, publication toggle, and longform body.
4. Save the Markdown source to Git.
5. If `draft: true`, the public site does not change.
6. If `draft: false`, repository-owned Actions compile the source into the already-accepted public frontend and GitHub Pages deploys it.
7. The published article appears on the homepage recent list, the archive, its own article URL, RSS and sitemap.
8. Version history remains Git-native; editor replacement must not strand the content.

## Security / privacy truth
- The normal editor must not require storing a long-lived GitHub PAT in the personal site's browser code.
- Pages CMS authorization is a real owner-side OAuth/App gate and cannot be simulated as completed.
- `draft: true` means “not published on the website”, **not private source**. The current `TaoismZp/xuyuan` repository is public, therefore any committed draft source remains visible in GitHub repository history.
- The Pages deployment artifact must exclude the Markdown source directory so drafts are not also exposed as direct website files.

## Must-pass owner loop
- edit/save source
- draft exclusion
- publish generation
- edit regeneration
- unpublish removal from public index/feed/sitemap
- stale generated page cleanup
- no visual redesign of accepted frontend
- no source Markdown served in the Pages artifact

## User-side acceptance gate
Backend Final cannot be claimed until the owner completes Pages CMS GitHub authorization and the real authenticated editor is used at least once. CI may validate every downstream consequence, but it cannot impersonate this login action.
