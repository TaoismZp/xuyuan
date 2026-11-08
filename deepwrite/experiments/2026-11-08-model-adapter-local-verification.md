# DeepWrite Model Adapter – Experimental protocol check (2026-11-08)

This is a **generic** public engineering method, not a private manuscript or a completed autonomous-book claim.

- Active DeepWrite workbench remains **v0.1**; this is an experimental adapter, not a promoted release.
- Uses the OpenAI Responses API with explicitly configured model and an environment-provided key, and defaults to `store:false`.
- Restricts non-test requests to the official HTTPS endpoint. Explicit loopback mode is a **local protocol fixture**, never live-model evidence.
- Project-specific execution, request/response content, manuscript files, and private checkpoints are NOT hosted in this public repository.
- In a private experiment, eight isolated adapter local tests and six existing recovery regression tests passed. A real model call was attempted but blocked because this runtime had no API key. Therefore **live model: UNVERIFIED**, **autonomous full book: NOT TESTED**, **independent A/B: NOT RUN**.
- Independent evidence and the original unpublished manuscript remain only in a private project storage area.
- Next gate: obtain a properly authorized private runtime with an actual model service, perform a limited real call with response ID and usage accounting, crash/restart recovery, then complete full-book and independent review gates.

**Security:** Never commit API keys, raw request bodies containing unpublished text, or any private response receipt to this public repository.
