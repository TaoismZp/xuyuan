# Durable Task State — Personal Site v1

- status: PUBLIC_READER_AND_LOCAL_COMPOSER_ACCEPTED / OWNER_AUTH_PENDING
- last_delivered_site_sha: `317c53ec032f6b37d65a82c7aab50a485c337046`
- last_public_acceptance: GitHub Actions run `41827098391` — **PASS**, candidate SHA and delivery SHA identical, iPhone/iPad/desktop WebKit + public HTTP.
- deploy_run: `41827027397` — SUCCESS.
- independent_supervision: `41826675293` — SUCCESS.
- representative_browser_ci: `41826675494` — SUCCESS (320/390/1024/1440px, Markdown preview, clipboard, .md export, local import and no external requests).
- public_main_website: https://taoismzp.github.io/xuyuan/personal-site-v1/
- new_local_writer: https://taoismzp.github.io/xuyuan/personal-site-v1/write/
- existing_sveltia_admin: https://taoismzp.github.io/xuyuan/personal-site-v1/admin/
- accepted_vision: `VISION_FIXTURE_V2.md` — minimalist ivory/ink/olive; reader pages and existing essay not rewritten.
- new_writer_scope: local-only text/metadata preparation, Markdown-it@14.1.0 preview, filename-only GitHub Create new file handoff; user confirms Commit in GitHub using own signed-in session.
- author_publication_gate: **PENDING_OWNER**. A browser test of local Markdown and a GitHub URL is not evidence the author actually authenticated, created a commit or published a post through the new path.
- sveltia_auth_save_gate: **PENDING_OWNER**, separately.
- privacy: drafts saved to PUBLIC GitHub are publicly readable; the local writing page does not persist or upload drafts before owner commit. Refresh may lose unsaved content; download .md first.
- original_essay: `content/posts/genius-trader.md` (《天才交易员为何注定陨落》), unchanged in this iteration; no fake public article committed.
- artifact_contract: `WRITE_ASSISTANT_CONTRACT.md`
- next_executable_action: owner may open `/write/`, paste an intended real public essay, preview/download/copy, then submit a GitHub-native file to main; verify GitHub commit -> Pages -> publicly readable article.
- deployment_identity_rule: doc-only follow-up commits do not trigger a new Pages deploy; latest delivered SHA remains the recorded Pages delivery SHA rather than latest repo HEAD.
- updated_at: 2026-11-04

## Conversation-independent recovery (2026-11-04)

- recovery_entry: `personal-site-v1/RECOVERY.md` — the single starting point for a fresh ChatGPT conversation; does not require the broken chat.
- machine_checkpoint: `personal-site-v1/recovery/state.json` — explicitly binds the locked Vision and Blueprint blob SHAs, last public release commit, deploy/verification run IDs and unresolved gates.
- recovery_validator: `node personal-site-v1/recovery/check.mjs` — checks source integrity without depending on chat memory.
- automatic_guard: `.github/workflows/personal-site-v1-recovery.yml` — runs on relevant changes and checks online reader/writer/admin entrypoints separately.
- initial_guard_evidence: GitHub Actions run `41834775760`, SUCCESS on commit `badff9d202695bb987f651b2afc133ccfe50dd8a`; this is a recovery/HTTP check, not a new Pages deployment or authenticated owner-publication PASS.
- safety: do NOT upload ChatGPT history, private drafts or tokens to this public repository.
- continuation_rule: every accepted site-development milestone must update both the machine checkpoint and this canonical status with evidence and one next action. The latest repository HEAD must never be confused with the last independently accepted Pages release.
- remaining_blocker: real owner-authenticated article commit/publication remains PENDING_OWNER.
