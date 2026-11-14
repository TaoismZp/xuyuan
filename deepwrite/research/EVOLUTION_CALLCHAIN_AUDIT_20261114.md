# DeepWrite 2026-11-14：全历史与真实调用链独立审计（脱敏公开版）

> 状态：ACTUAL_GITHUB_FILES_READ / ENGINEERING_CANDIDATE_REVIEW；**不是**自动升版、真实模型写书、作者质量验收或全部私人聊天恢复。时间基准 2026-11-14。独立项目真实原文、作者反馈和私有实验细节只在相应私有仓库。

## 1. 把四种身份分开

- **正式规范**：`TaoismZp/xuyuan/main:deepwrite/CURRENT.json`，main commit `6b81a45d8576aa0636d29950f9a2d86f2a5cf8b1`，`active_workbench_version=v0.1`，Git blob `f57402a510e051d53d04a59d17e6f09720130650`，没有 `active_engine`；`automatic_full_book_generation=NOT_IMPLEMENTED`。父规范 `wish-delivery/CURRENT.json` 生效 v7.6，blob `2a253140bbd097b05b273a1a4634669991c2fde9`。不得把作者评价某份稿约80分、项目阶段R4、候选v0.2当正式发布版本。
- **候选规范**：`deepwrite/candidates/v0.2.md` / `RESEARCH_LOOP.md` / `EDITORIAL_LOOP.md`，定义研究方向的竞争、源领域与章节图分离、章间独占贡献、真正返工和保持合理KEEP；不是ACTIVE。
- **候选引擎**：PR #14 `experiment/deepwrite-activation-rail-20261111`，head `42d8d6a54e1ab73bd026660bf6bf76069ab97888`，有真文件执行与合成 CI。入口 `deepwrite/release/activation.py` 会在 main 无 active_engine 时停机，合理防止把候选当稳定版。E18写作器 `deepwrite/tools/writing_loop_experimental.py` 仍为候选。
- **内容作品证据**：历史首轮/二轮真实可读书稿、章节审稿、原件回读及作者批评，既不是正式版本，也不能被机器测试解释为书稿“通过”。未来仍须陌生题材作品、独立读者与作者质量验收。

## 2. 起源演化时间序列（来自 main 的 HISTORY / CHANGELOG、PR提交与真实文档）

| 阶段 | 发现的真实故障 | 学到的机制 | 尚未证明的事 |
|---|---|---|---|
| H0 批量一次成书 | 单次生成目录和多章，篇幅完整≠独立新知 | 一次授权≠一次推理，须多轮内循环 | 自主黑箱不弱于逐章 |
| H1 逐章提升又漂移 | 单篇好观点逐章污染其余原生概念 | 先独立研究原领域，不对后续章投喂唯一结论 | 可自动避免路径依赖 |
| H2 概念图重建 | 源概念结构与书的读者章节结构混同 | `CONCEPT_MAP != BOOK_BLUEPRINT`，可合并/删章/重排 | 固定章数合理 |
| H3 章内和跨章对抗 | 重复母题，局部准确取代思想发现 | 反方、实质返工、跨章对照、原稿保护 | 自审足以替代真实读者 |
| H4 断档恢复 | 聊天窗口唯一承载产物导致风险 | 私有档案/状态/哈希/唯一下一步 | 修复平台窗口/自动导出旧聊天 |
| H5 DeepWrite v0.1 发布 | 规范与包器可用，但无真正整书执行器 | 官方CURRENT区分原型、实体作品和作者验收 | E1/E2 |
| H6 第二新书试验 | 文本完整、校对合格却仍缺可买的独到价值 | 思想发现与读者效益单独验收 | 机械QA自动提高文学水平 |
| H7 渐进升级 | 补丁越来越多造成复杂性与质量回退 | STABLE/SHADOW/CANDIDATE_OPT_IN/ROLLBACK | 某一项目成功即可全域发布 |
| H8—H10 独立研究/迁移实测 | 两种干预不稳定增益，读者理解未证明改善 | 做真实对照、允许拒绝复杂化 | 新模块必然赢 |
| H11 真实整书编辑 | 论证和现金流可核缺陷在稿中存在 | 结合实际正文局部修订，原件保全 | 局部返工≠全书认可 |

以上为可核的**历史检查点摘要**；没有完整逐字私人聊天证据，不能宣称穷尽所有未持久化历史。

## 3. PR #12—#18：实际能力台账（截至本审计）

- [#12](https://github.com/TaoismZp/xuyuan/pull/12)：v0.2研究/编辑候选、真实安全打包改良；未合并，自动写书与陌生完整作品盲评未完成。
- [#13](https://github.com/TaoismZp/xuyuan/pull/13)：E15审稿缺陷不得只记录不影响正文，只有结构回归证明；修复代码被#14候选复用。
- [#14](https://github.com/TaoismZp/xuyuan/pull/14)：E18 + E23真实文件调用链、研究、来源、读者审稿、返工、重查、跨章、前后文、封装、恢复。GitHub CI `43403926705` 真实成功，工程回归数目 release73/guard42/packager15/E23-reader51/writer47；后来真实正向临时Git stable profile 49项。**所有这些仍是 synthetic/temporary Git engineering evidence。** provider实际401、模型创造/人类盲评未通过，未更改正式 CURRENT。
- [#15](https://github.com/TaoismZp/xuyuan/pull/15)：故意失败CI→修复的负控制PR，标明 **DO NOT MERGE**。
- [#16](https://github.com/TaoismZp/xuyuan/pull/16)：跨域前先教源知识；读者初学/熟练/专家三层文档候选，无执行代码（#14另实现 reader_source_gate）。
- [#17](https://github.com/TaoismZp/xuyuan/pull/17)：独立洞见 blind-pre-reveal / author-guided 两模式以及概率化 paired-research 模块；工程90/90测试仅证明结构与身份，不证明认知新发现；依赖#14不可独立合并。
- [#18](https://github.com/TaoismZp/xuyuan/pull/18)：**本次新工程候选**。基于#14 stack：真实 E18 入口增加 opt-in native-source-first preflight，且 reader_source_gate 增加知识复利新情境迁移检查与阻断；模块身份、正文位置、来源哈希实际绑定。**工程测试和CI按最新head观察，未通过则FAIL；仍非ACTIVE**。

## 4. 最危险的真实执行链断层

### A. 正式入口空缺
新项目从 `main/CURRENT.json` 读取 v0.1，`activation.py` 不发现激活engine就拒绝调用写书器；候选分支规则再好也不会进入主调用链。这是版本和功能有效性的主故障，不能再改名解决。

### B. 目录比研究更早被确定
#14 E18 `_validate_config` 在任何研究角色调用之前要求 `chapters` 和完整 `reader_prior_knowledge_contract`；研究之后可以生成 plan.md，但没有安全机制真正改变 book chapter topology。对于“ source governs book ”尤其致命。#18先以独立源研究摘要、源章区分、竞争问题及逐章来源依赖作为**opt-in前置条件**阻止没有证据的先定目录；但模块目前**仍不支持完整自动从源发现重编章节数**，需后续单独实现双阶段动态立项与真正质量实验。

### C. 模型审阅与知识复利不等于读者会用
只有三层读者标签与定位的模型QA不代表初心者读懂、熟手有独到收益、专家不觉简单。#18所加 `knowledge_compounding_probe` 要求从文章出发给未知新题、先修知识、预期推论、失败边界并绑定正文段落；缺失/UNVERIFIED会阻断。它仍是**模型内部评估，不是人类迁移测验**；不可把 `MODEL_INTERNAL_REVIEW_RECORDED` 晋升为作者或读者 PASS。

### D. 正式治理堵点
最新规则集 `27040989`（实际GET）：main需1名PR批准；必需CI列表为空，strict=false；repo allow_auto_merge=false。此前PR14设置写入 REST 403（integration token缺Admin endpoint许可），未能回读正式生效的要求。**仓库元数据admin=true不等于拥有admin API token写权。** 不伪造独立审批、不绕过保护合并，未获真实质量/用户授权也不改 `deepwrite/CURRENT.json`。

### E. 无法把成绩评价当版本号
历史稿件“60/80分”、候选文件R4、原生研究成功等都不能当工作台 `v0.4`、`v4` 或 `v1`。工作台版本只来自可回读CURRENT，候选可由 commit+schema 唯一固定并以 project opt-in 使用。

## 5. 本轮具体补丁与验收目标

1. 新 `deepwrite/candidates/source-first/source_first_gate.py` 与测试：研究原文真实字节、源场景引文、反例、跨域失效边界、至少两个竞争方向、独立书章节依据。无证据则 BLOCKED。功能只检查声明证据，不做事实语义或真实时间先后证明。
2. 接入 `deepwrite/tools/writing_loop_experimental.py` 正式被选中的候选E18调用链：可选module flag、读写实际来源bytes、模块receipt、run_state；STABLE未经发布拒绝新候选。
3. 增补 `reader_source_gate.py` 的knowledge-compounding transfer probe：CHAPTER/BOOKWIDE审稿绑定正文；缺失证据HOLD、UNVERIFIED/REWORK返工；不强制6个标题和评分，不用模型冒充真实人类。
4. 新旧回归CI必须包含 source-first gates，保留E15/E23/E18已有测试；真实GitHub日志和最终head状态作为唯一工程成绩证据。
5. 发布为 **opt-in canary** 候选，不重写ACTIVE指针；待更多合法provider/陌生作品测试与作者授权后另开 engineering-only/research-based promotion 工作。

## 6. 保密、未关闭Gate与唯一下一步

**PASS**：本轮实际源文件、PR状态、规则集和CI日志读取；#14先前工程 fixture 回归证据真实存在；#18代码写入候选分支（最后以远端blob回读确认）。

**PENDING/UNVERIFIED**：本轮最终head CI、PR #18审查/合并，模型真实provider调用，自动发现章节拓扑，独立思想创新，陌生受众六维知识复利迁移，自动全书E1、质量不低于逐章E2、作者认可、正式CURRENT升级。

**STOP**：本分支不得以任何书稿内容进入公开库；#15绝不可合并；#17不能独立于#14激活；不以书稿对照的AI自评替代真人。

**唯一下一步**：令 #18 全工程CI对准最终head实际PASS并远端回读；若PASS，则先通过授权/治理与真实新书质量canary，再决定正式独立升版，不能误报v0.1已退役。所有正式发布须单独履行 `GUARDED_EVOLUTION.md` 与父版v7.6的许可/验收。
