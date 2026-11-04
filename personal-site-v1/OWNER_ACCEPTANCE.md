# Owner Acceptance — iPhone CMS Save / Publication

## What is and isn't already verified

Public article reading, GitHub Markdown generation, GitHub Pages deployment and mobile-friendly CMS *login entrance* have automated evidence. **Owner-authenticated Sveltia login, edit, save and live publication are NOT TESTED**. Do not promote a public-reader PASS to full authoring PASS.

## Safe user-side validation

1. On a trusted iPhone/iPad, open https://taoismzp.github.io/xuyuan/personal-site-v1/admin/.
2. Create a short-lived, **fine-grained** GitHub token restricted to only `TaoismZp/xuyuan`, with Contents: Read and write. GitHub token scope is repository-wide, **not** limited to `personal-site-v1`. Never send the token in chat, an email, or a Git commit.
3. Sign in inside Sveltia's token login dialog and confirm that the existing 《天才交易员为何注定陨落》 record appears and opens.
4. To prove saving, publish the owner's next **genuinely intended public article**. Do not make up a dummy public post, do not put personal or sensitive drafts in this public repository, and do not alter the existing author's real essay simply to satisfy a test.
5. Check the saved Markdown commit in GitHub, Pages deployment run, and the article's **real public URL**. Read the article at the top and bottom using iPhone Safari.
6. Edit the newly published article only with a legitimate correction. Verify its new version is deployed; do not consider deletion as erasure from Git history.
7. If a permission, login, rendering, or saving issue appears, capture the **error message only** and ask for debugging help; never reveal token material.

## Acceptance record

- `OWNER_LOGIN`: **PENDING_OWNER**
- `OWNER_EDITOR_SAVE`: **PENDING_OWNER**
- `AUTHOR_GIT_COMMIT`: **PENDING_OWNER** (the prior GitHub connector commit does not substitute)
- `PUBLIC_PAGES_POST_UPDATE`: **PENDING_OWNER**
- `PUBLIC_READER_SURFACE`: independently verifiable by GitHub Actions.
- `PRIVATE_DRAFTS`: **NOT SUPPORTED** in the public repository.

Scope boundary: without the owner's local authentication, no automated assistant or CI runner can truthfully mark the owner workflow PASS.

## Alternative without an extra Token

There is now a safe, local-only composition and handoff page:

https://taoismzp.github.io/xuyuan/personal-site-v1/write/

It prepares published Markdown from title, summary, date, tags and body with an on-device preview using the same pinned Markdown-it renderer, offers a local .md backup and copies full Markdown to the clipboard. It opens GitHub's native **new file** interface with only a filename in the URL. Existing GitHub web session authentication is still required to make the commit.

This is a **manual, owner-controlled fallback**, not a claim that the Sveltia authenticated write path has been verified. Never commit secrets or unpublished private drafts in the public repo.

- `LOCAL_COMPOSER_PREVIEW/COPY/DOWNLOAD`: automated browser evidence only.
- `NATIVE_GITHUB_LOGIN_AND_COMMIT`: **PENDING_OWNER**.
- `PUBLISHED_PAGES_AFTER_OWNER_COMMIT`: **PENDING_OWNER**.
- `SVELTIA_TOKEN_LOGIN_AND_SAVE`: **PENDING_OWNER**, separate route.
