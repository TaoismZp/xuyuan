# Durable Task State — Personal Site v1

- status: PUBLIC_READER_AND_LOCAL_COMPOSER_ACCEPTED / OWNER_AUTH_PENDING
- last_delivered_site_sha: `d8f7e41a631ff9de9914cbdb29e00a2042a66f07`
- last_public_acceptance: GitHub Actions run `41839357165` — **PASS**, delivery SHA `d8f7e41a631ff9de9914cbdb29e00a2042a66f07` matched exact post-deployment iPhone/iPad/desktop WebKit + public HTTP.
- deploy_run: `41839299091` — SUCCESS, delivered commit `d8f7e41a631ff9de9914cbdb29e00a2042a66f07`.
- independent_supervision: `41839298835` — SUCCESS, independent backend/browser integration checks on delivered commit; separate from post-deployment WebKit.
- representative_browser_ci: `41839298835` — SUCCESS (320/390/1024/1440px, clipboard handoff guard, stale-copy regression, Markdown preview/download/import and no external requests).
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

## 2026-11-04 · value-gate cross-audit and verified writer handoff release

- change_review: https://github.com/TaoismZp/xuyuan/pull/8 — merged; final production release `d8f7e41a631ff9de9914cbdb29e00a2042a66f07`.
- process_revision: `wish-delivery/candidates/v7.6-value-adoption-gate.md` is **CANDIDATE / NOT ADOPTED**, not a replacement for v7.5.
- code_scope: disabled GitHub handoff until Markdown copy has succeeded (or the author explicitly confirms manual copying); editing after copying re-locks the handoff. Manual Markdown download remains available. No local auto-save, no Token, no article modification, no visual redesign.
- predeployment_integration: GitHub Actions `41839298835` PASS at exact release SHA; candidate PR/push runs `41838941461` / `41838933369` PASS at parent candidate SHA `5519e17efa2d75c740d37f8ec66057690c9a9eaf`.
- deployment: GitHub Pages `41839299091` SUCCESS at `d8f7e41a631ff9de9914cbdb29e00a2042a66f07`.
- public_http_and_webkit: GitHub Actions `41839357165` PASS at `d8f7e41a631ff9de9914cbdb29e00a2042a66f07`; this is independent post-deployment public browser verification, not real iPad owner sign-in.
- evidence_rule: `recovery/check.mjs` now requires explicit `headSha` equality for every claimed PASS. `personal-site-v1-recovery.yml` separately queries GitHub Actions APIs to confirm each run ID actually concluded success on the delivered commit, rather than trusting the manifest's self-description.
- caveat: the historical supervision run `41826675293` applied to the older release and is not reused for this commit.
- owner_gate: **PENDING_OWNER** — no authentic author GitHub login/Commit/publication through the writer or CMS has been performed in this run.
- unique_next_action: owner uses an already-intended public essay in `/write/`, copies/down-loads, submits a native GitHub commit with their own login, then we compare commit, deploy and public article on their device.
- cross_chat_evidence: `personal-site-v1/reviews/2026-11-04-cross-audit.md`; the private global checkpoint exists in ChatGPT Library at `/跨对话恢复中心/SITE_AUDIT_CHECKPOINT_2026-11-04_v1.md`.
