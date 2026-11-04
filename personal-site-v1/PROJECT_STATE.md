# Durable Task State — Personal Site v1

- status: READER_FLOW_V2_LIVE / PUBLIC_EVIDENCE_RECHECK
- last_released_commit: `f0dcad44fc925fdea7752a810b8d19aa310446e3`
- latest_webkit_acceptance: GitHub Actions run `41815812731` on the released commit (initial automated PASS).
- manual_evidence_inspection: desktop real-article ending screenshot matched; iPhone ending screenshot was captured during a competing smooth-scroll animation despite the numeric scroll-position PASS.
- current_gate: strengthen iPhone/iPad/desktop WebKit end-of-article proof, checking final paragraph and end navigation are actually visible before screenshot; re-accept the final deployed commit.
- publicly_published_article: 《天才交易员为何注定陨落》, `content/posts/genius-trader.md`, https://taoismzp.github.io/xuyuan/personal-site-v1/essays/genius-trader/
- reader_features: desktop sticky 4-section outline, mobile native disclosure, fragment navigation, active-section marking, article-end navigation and shared canonical link.
- original_source_provenance: `/作者第二大脑/01_成稿原文/天才交易员为何注定陨落_用户原稿_2026-10-22.md`; source SHA-256 `312cf1ebad852621edd72078d7cce2f653da6e5072f12e0199787e823e5e23b4`.
- vision: approved third minimalist Taste direction; paper/ink/olive palette retained and original essay not modified.
- construction: Markdown is canonical; site output built by CI; Pages deploy allowlisted artifact; retries use per-attempt artifact naming.
- owner_auth_pending: only owner can validate Sveltia authenticated author edit/save with restricted GitHub token. Never ask to send token in chat.
- privacy: GitHub repository is public; draft status hides site pages but does not make committed Markdown private.
- updated_at: 2026-11-04
