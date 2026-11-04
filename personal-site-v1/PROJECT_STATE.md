# Durable Task State — Personal Site v1

- status: AUDIT_REMEDIATION_CANDIDATE / OWNER_AUTH_PENDING
- last_good_checkpoint: `8aca78c69be6da6328c5ce9cd4f5ae02f82cf1c0` (pre-remediation public site)
- candidate_ref: `personal-site-v1-audit-remediation-20261104` (resolve HEAD after checkout, no self-referential commit SHA)
- current_gate: branch browser CI + automated supervision; next: same-SHA main promotion + public WebKit verification
- next_executable_action: run candidate CI on all mobile breakpoints; inspect screenshots; promote only after PASS. Owner login/save remains a separate user-only task.
- owner_auth_gate: **PENDING_OWNER**; instructions `OWNER_ACCEPTANCE.md`; no real owner Token submitted to assistant.
- frontend_vision_identity: `VISION_FIXTURE_V2.md` — warm ivory, near-black, restrained olive, accepted third concept.
- acceptance_blueprint_identity: `BUILD_BLUEPRINT_V2.md`; backend blueprint is a separate technical specification.
- scope: correct iPhone/about/projects/archive two-line title wrapping; correct reference hashes; stop documentation-only commits retriggering Pages; clarify status as READER_SURFACE_ONLY; reconcile the active wish-delivery spec pointer without changing normative versions.
- original_essay: `content/posts/genius-trader.md`; no edits authorized or made.
- status_commit_rule: documentation may record the last actual deployed production SHA, which is not required to equal the latest repository SHA after documentation-only changes.
- privacy: draft Markdown in public GitHub is readable through GitHub even when hidden from public Pages.
- updated_at: 2026-11-04
