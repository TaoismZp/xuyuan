# DeepWrite × 许愿式交付协同演化：补充指令（2026-11-09）

用户新确认：希望 **DeepWrite 和上游《许愿式交付》同时研究改进**，但不能把两者捆绑升级，也不能为了更复杂的流程牺牲现有成果；任何新模块应可单独试用，不好的能够恢复以前版本。两次真实长书试验的证据必须纳入工作台发展史，但未发表原件仅在私有档案。

**位置与优先级**：此文件补充 `SCOPE_CORRECTION_20261109.md`，优先于 `messages/0001-chatgpt.md` 内过时的单模块测试范围；001历史原件永远不覆盖。首条Codex回复仍用 `messages/0002-codex.md`，不要额外占用Codex编号。

## Codex 首轮扩大任务（仍保留成本约束）

1. 读 `deepwrite/GUARDED_EVOLUTION.md`、`deepwrite/WORKBENCH_RELEASE_CHANNELS.json`、`deepwrite/PROJECT_PIN_TEMPLATE.json`、`deepwrite/qa/release_guard.py`及测试；再读 `wish-delivery/research/DEEPWRITE_FEEDBACK_CANDIDATE_20261109.md`。核验 active `deepwrite/CURRENT.json` 和 `wish-delivery/CURRENT.json`。
2. 独立诊断两次**项目**所暴露的不同失败机制（以实际能访问的私有证据为限，不能在公开回应贴私人书稿）。检查哪些已经被通用v7.6覆盖，哪些必须留在写作域，哪些值得上游通用补丁。
3. 特别审查：`release_guard.py` 仅能做结构验收，不能验证分数是否真实、是否退化；如何减少评估复杂度但仍确保不可覆盖与可回退？如何分阶段用新模块而不静默改变旧项目？先做高收益的小改动、跑真实测试，禁止为了升版本而堆流程。
4. 两层规范分别维持稳定生效指针；新候选只作为 `SHADOW` / `CANDIDATE_OPT_IN` 可选择研究，回滚记录原件、候选文件、SHA、commit及用户评价；项目旧版不强制迁移。
5. 全部真实测试、发现与证据写 `messages/0002-codex.md` 并更新 `STATE.json`。仍由用户通知ChatGPT去看，不支持自动后台轮询。每轮告知用户实际改进、失败/风险和唯一下一步。

**防伪与隐私**：工程PASS≠质量PASS；用户一份稿的约60分不等于整个工作台固定分数；AI互评≠真人独立盲评；公开仓禁止私人全文/具体未发表内容；未授权不得晋升两套 CURRENT。
