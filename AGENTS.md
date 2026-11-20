# Repository task routing

When the user asks to use, maintain, or release DeepWrite, first read
`deepwrite/CURRENT.json`, `wish-delivery/CURRENT.json`,
`deepwrite/AGENTS.md`, and `deepwrite/START_HERE.md`.
Resolve the actual main release rather than a remembered version or old PR.
Use `deepwrite/release/activation.py` to verify and invoke its selected engine.
Reading these instructions alone is not evidence that the engine ran.

For an existing book, read its private recovery files and preserve its engine
and manuscript pins. Never put unpublished manuscripts or private reviews in
this public repository. Engineering tests do not certify book quality.

For other tasks, follow the instructions and entry points for that project;
DeepWrite is not the default workflow for the FIN·TYPE application.

## Mandatory DeepWrite MASTER AUDIT route (book-review tasks)

When the request is **总审 / 全书总审 / DeepWrite总审 / 完整书稿审稿 / master audit** (including a restart/continue), this is **NOT** just another writing invocation. Before reading a chapter, load `deepwrite/master-audit/MASTER_AUDIT_POLICY_v1.md`, the active CURRENT files, and the private project's actual STATE/RECOVERY/source identity. The policy's source-byte coverage + real per-chunk receipts + whole-chapter understanding + cross-chapter issue ledger are all required. In CLI-capable environments invoke `deepwrite/master-audit/audit_gate.py`, which fails closed on missing evidence.

Default batch for audit is **three whole chapters (~10–20 source chunks)**, flexibly adjusted by complexity and context with a written downsizing reason. Do not ask the author to reply “继续” after every three chunks. Changed chapters must be delivered as the entire revised chapter. Preserve the same issue IDs across passes. Do not claim “full-book audit PASS” from a manifest or a few chapter reports; do not claim CLI/CI ran when only manual checks were possible.

A candidate branch or a file being present is not proof this master audit route has reached stable main, and ordinary ChatGPT chats do not automatically read repository AGENTS instructions.
