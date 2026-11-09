# Discovery Gate: Codex CLI login bridge (candidate v0.1)

**Purpose:** Run the existing frozen six-prompt A/B study with the user's *locally signed-in* Codex CLI, without asking them to paste an OpenAI API key into chat. This is an **alternative execution backend**, not a retroactive change to the frozen scientific protocol.

Official commands confirmed in OpenAI documentation: `codex login status`, `codex exec --json --ephemeral --ignore-user-config --sandbox read-only --skip-git-repo-check --model ... --output-last-message ... -`. See [CLI reference](https://learn.chatgpt.com/docs/cli/reference) and [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

## Preflight and permissions

- Use a local machine with authenticated Codex CLI: `codex login status`. Codex using a ChatGPT account consumes the user's plan allowance. This runner **never** accesses, exports, or prints Codex credentials. Never upload `~/.codex/auth.json`.
- The current assistant container has neither Codex CLI nor a signed-in credential. **No real six-run trial was executed here.**
- Use the **original frozen six prompts and manifest**, preserved in the project's private Library; do not regenerate inputs or insert old book manuscripts into the public GitHub repository.
- Choose one eligible Codex model and set it explicitly to keep model identity stable. Availability depends on the signed-in account.

## Local execution

All the generic Python scripts below are in the public GitHub folder, but **the frozen prompts must be sourced from the private archive**. Unpack the private archive into a local folder with `private/prompts/` containing `T01_A.txt` ... `T03_B.txt` and `PROMPT_MANIFEST.json`.

From a folder with the generic scripts and `private/prompts/`, run the packaged helper with one command:

```bash
bash RUN_TRIAL_ON_MY_COMPUTER.sh YOUR_AVAILABLE_CODEX_MODEL
```

Or run the commands individually:

```bash
codex login status
python3 execute_codex_cli.py --manifest private/prompts/PROMPT_MANIFEST.json --prompts private/prompts --out results/real-run-01 --model YOUR_AVAILABLE_CODEX_MODEL --dry-run
python3 execute_codex_cli.py --manifest private/prompts/PROMPT_MANIFEST.json --prompts private/prompts --out results/real-run-01 --model YOUR_AVAILABLE_CODEX_MODEL
python3 trial_harness.py seal --pack private/TOPIC_PACKETS_FROZEN_v0.1.json --manifest private/prompts/PROMPT_MANIFEST.json --inbox results/real-run-01/inbox --out results/sealed-01
python3 trial_harness.py blind --sealed results/sealed-01/SEALED_RESPONSES.json --sealreport results/sealed-01/SEAL_REPORT.json --out results/review-packet-01 --keydir results/private-blind-key-01
```

The `TOPIC_PACKETS_FROZEN_v0.1.json` file is also in the private project archive; its SHA must match `PROMPT_MANIFEST.json` when sealing. **Do not manually modify either input**. The CLI may return invalid JSON or exceed the per-run token cap, in which case the original failed run and logs must be kept, not replaced by retrying.

### Verification boundaries

- A fresh `codex exec` process, ephemeral session and empty workspace **improve** context isolation, but neither the adapter nor an `independent_context: true` field proves the account's hidden state or complete independence. Inspect actual events and execution receipts.
- `--sandbox read-only` disallows model file modifications; this execution supplies only the frozen source descriptions, so neither group should conduct unbudgeted web research. Additional tool calls are flagged as deviations.
- The requested cap of 12,000 total tokens is **checked after** a run, not enforced during generation. Codex may use different internal budgets or cached token counts. This backend must be reported `EXPLORATORY_EXECUTION_BACKEND_DEVIATION` unless observed usage, hidden tool activity, and comparability are independently audited. Do not promote DeepWrite on this basis alone.
- A/B outputs have not been generated or human scored by this assistant. Private raw event streams, credentials and blind mapping must stay out of public GitHub. Only generic code and honest reproducible methods belong there.
- The next genuine external gate is **two independent human readers**, not the same AI wearing two judge personas.
