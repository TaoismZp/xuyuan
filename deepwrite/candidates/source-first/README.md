# DeepWrite Source-First × 知识复利可试用工程候选

> 候选身份：PR #18，依赖未合并的 PR #14；2026-11-14；**CANDIDATE_OPT_IN / SHADOW ONLY**。工作台正式 `deepwrite/CURRENT.json` 仍 v0.1。这里的“可试用”指在有本地执行环境与已授权的模型凭据时可**显式选择候选运行**，不代表正式发布、验证整书质量或已接入一般ChatGPT对话的默认写作通路。

## 解决的真实故障

之前E18需要提前给出 `chapters`，之后才让模型做原生研究，导致原学科的发现无权改变目录；只写好`RESEARCH_LOOP.md`并不能阻止机器继续按不正确的章目批量生成。另有读者标准只写NOVICE/PRACTITIONER/EXPERT，却没有实际检验读者能否把一章学到的知识用于新题。

新增强制的**可选路径**：已冻结原始源资料 → 原生研究文本 → 两个不同的研究方向/争论及选择理由 → 临时书结构与源概念独立映射 → E18真实写作/模型审查 → 章节新情境迁移复核（知识复利）→ 必要返工/停机。所有新文件都在持久化项目目录；私有书稿不进公开方法仓库。

## 如何实际运行（需 Git/Python3.10+/已授权真实模型）

1. 检出本 PR #18 的固定候选提交或分支。**不要从 `main` 的 v0.1 入口猜测能调用它**。先在独立私有项目准备 config、原始素材及一份源学科研究记录，全部计算 SHA256 并声明在 `config.sources`。
2. 在原 E18 已要求的 `config` 上启用以下键；其余项目、真实作者授权、来源 pin、模型、字数预算、源概念前置合同、章节表等请按 `deepwrite/tools/tests/test_writing_loop_experimental.py` 的 `config` 最小 fixture 及 `deepwrite/candidates/e18-writing-loop/README.md` 的契约设置（测试凭据不是真实作者授权）：

```json
{
  "channel": "CANDIDATE_OPT_IN",
  "modules": {"e18_loop": true, "source_first_architecture": true},
  "module_policy": {"e18_loop": "CANDIDATE", "source_first_architecture": "CANDIDATE"},
  "module_commits": {
    "e18_loop": "<pinned 40-hex implementation commit>",
    "source_first_architecture": "<pinned 40-hex implementation commit>"
  },
  "reader_prior_knowledge_contract": {
    "schema": "deepwrite/reader-prior-contract/v1",
    "known": [],
    "unknown": ["<source knowledge the target reader has not learned>"],
    "concepts": [{"id": "<id>", "first_explained_in": "<chapter_id>", "first_used_in": "<chapter_id>", "prerequisites": []}],
    "knowledge_compounding": {
      "enabled": true,
      "transfer_goal": "<the different problem readers should solve after this chapter>"
    }
  },
  "source_first_architecture": {
    "schema": "deepwrite/source-first-architecture/v1",
    "project_id": "<same project_id>",
    "status": "PROVISIONAL_NOT_AUTHOR_APPROVED",
    "source_study": {"path": "sources/native-study.md", "sha256": "<sha256>"},
    "source_concepts": [{
      "id": "native_concept_01", "source_path": "sources/original.md",
      "quote": "<8+ character verbatim anchor from the source>",
      "causal_mechanism": "<8+ character explanation of the original mechanism>",
      "counterinterpretation": "<8+ character serious competing explanation>",
      "transfer_limit": "<8+ character limit of the analogy>"
    }],
    "rival_directions": [
      {"id": "direction_A", "source_question": "<8+ chars>", "reader_problem": "<8+ chars>", "tradeoff": "<8+ chars>"},
      {"id": "direction_B", "source_question": "<8+ chars>", "reader_problem": "<8+ chars>", "tradeoff": "<8+ chars>"}
    ],
    "selected_direction_id": "direction_A",
    "why_selected_over_rivals": "<8+ characters of grounded argument>",
    "book_design": {
      "status": "PROVISIONAL",
      "why_these_chapters_not_source_outline": "<why the chapters are different from number of source lessons>",
      "chapter_contributions": [{
        "chapter_id": "<must match a config.chapters[].artifact_id>",
        "source_concept_ids": ["native_concept_01"],
        "distinct_reader_change": "<reader judgment that this chapter uniquely enables>"
      }]
    }
  }
}
```

以上是**结构片段而非完整独立可运行 config**，必须与原 E18 的冻结来源、权限、预算、`pins` 对齐（`pins.modules` 中每个启用候选模块都需要对应的提交ID）。源研究记录必须绑定 `sources` 清单和其精确内容；模块只验证字节和引用，不会鉴别研究文本是否真正先于章节计划产生。上面尖括号是说明占位符，不能照原样用于正式写作。

3. 在可信任的本地或 Codex 执行环境调用：

```bash
python3 -B deepwrite/tools/writing_loop_experimental.py /private/config.json /private/project
```

续跑必须提供上一次 `run_state.json` 外部验证 SHA：

```bash
python3 -B deepwrite/tools/writing_loop_experimental.py /private/config.json /private/project --expected-state-sha256 <64-hex>
```

以上是候选执行**原生代码入口**，不是 `main` 上尚未发布的 `activation.py --run` 正式入口。要保留模型请求/响应、真实文件改稿、差异与checkpoint，才能判断此次试用是否真的执行。无法进行provider认证应按BLOCKED记录，不模拟真人签收。

## 质量门与明确的局限

- **PASS_ENGINEERING_ONLY**：源真实SHA、引文、研究图/章节图区分和后续模型迁移审查结构已接线；没有这些证据拒绝起稿。
- **PENDING**：读者三层真正受益、王路六维知识复利在陌生读者中的表现、写作品质与对旧版增益。
- **NOT IMPLEMENTED**：完全自动从源研究动态确定书的最终章数与章序；无监督首次成书质量至少不弱于逐章；真正独立洞见新视角与人类盲评。
- **不可推断**：源码结构PASS不能证明模型提出了真实的新假说，或声称由未知题材独立完成写作；源研究文档存在也不能证明研究时间顺序。
- 正式 `CURRENT.json` 升版只能走已批准工程及质量发布流程；不得把PR#18 draft作为main有效版本。

## 正负回归

GitHub Actions `.github/workflows/deepwrite-activation.yml` 对本分支运行：
- 新 `test_source_first_gate.py` 11个源研究/来源身份/独立章数约束的正负样例；
- 扩展E23 reader tests：缺少迁移探针HOLD、UNVERIFIED触发返工，模型结果不可冒充人类；
- E18实际mock写入、返工、checkpoint和恢复，以及 source-first 模块真实加载。
- 旧release/guard/packager/E23/E18必须无退化。完成测试后仍标 `ENGINEERING_FIXTURE_ONLY_NOT_LIVE`。

请以PR#18最新实际 Actions check 和 GitHub Blob 回读为准。**安全侧：不含私人作者原稿、私人聊天、秘钥。**
