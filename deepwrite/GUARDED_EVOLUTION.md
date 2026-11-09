# DeepWrite x Wish Delivery｜受保护的持续演化协议（候选，不自动生效）

**适用范围**：完整 DeepWrite 写书工作台与上游通用《许愿式交付》。状态 `PROPOSED_OPT_IN_AVAILABLE`；本文件是对既有有效版本的**可选补充**，不是修改 `deepwrite/CURRENT.json` 或 `wish-delivery/CURRENT.json` 的许可。发布前实时读取两个 CURRENT 的实际生效指针。

## 1. 继承和反向反馈

`wish-delivery/CURRENT.json` 是通用交付合同（目标、能力栈、施工、独立监理、同表面验收、可恢复状态）。`deepwrite/CURRENT.json` 是写书专用合同（认知发现、研究证据、知识地图、章节结构、写作/重构、全书一致性、质量审读）。**DeepWrite 是特化者，不是上游的等价替换物。**

反馈从 DeepWrite 向 Wish Delivery 提交时，必须把问题写成与书写无关的可复用失败机制，并给出另一个非写作领域的代表性测试。示例：「字数合格并不代表有价值」的抽象问题是 `Primary Artifact Exists != User Value/Experience Pass`，上游 v7.6 已有相近约束，不能为同义概念无故升级；「读者看不到完整书稿」则可归入 `Delivery Surface + User Acceptance`。写作独有的「原创思想、主题漂移、AI编辑腔」只留在 DeepWrite。

每一条反馈要记：`source_project_id(private)` / `sanitized_failure` / `affects` (UPSTREAM|DEEPWRITE|BOTH) / `already_covered_in_active` / `proposed_delta` / `reproduce` / `expected_user_value` / `side_effects`。如果正式规则已经覆盖且只是执行不到位，应修工具或验收，不要加同义新规则。

## 2. 两轮实测的证据等级与负教训

- **项目A，原生知识迁移型全书**：初期批量出文质量低，后又遇到局部结论污染全书与目录/知识图混同。后续按源领域重建、逐章独占任务、跨章比对，产生可核的20章候选和多轮恢复点；作者及独立全文验收未通过。早期“34个对话”属于作者回忆，不是完整原始会话重放证据。
- **项目B，普通人财富题材非虚构长书**：完成10章约5万汉字合流稿、技术SHA回读及编辑分支。作者反馈质量约60分；这个分数是作者对**该份稿**的主观质量评价，不是全系统稳定分数，也不是盲评。经验是：修正错误、填足章节和归档PASS，仍可能损害思想新颖性、声音与阅读价值。
- 两项目是**两个项目回合**，不是 `DeepWrite v1 / v2` 正式版本号。正式工作台仍以 `deepwrite/CURRENT.json` 为准。公开本文件只保留脱敏过程概括，真实原稿、审稿、作者评价和哈希在各自受限私有恢复档案，不拷贝公开仓库。

## 3. 双轨 + 模块化激活

- `STABLE`：默认走 `deepwrite/CURRENT.json` + `wish-delivery/CURRENT.json` 当次真实指针。没有发布证据时新项目只能默认此模式；不是承诺既有稿质量已经达到出版标准。
- `CANDIDATE_OPT_IN`：在单个**新**项目的 `PROJECT_STATE` 明确固定 `resolved_deepwrite_version`、`resolved_parent_version`、`module_flags`、完整候选 Git commit/Blob SHA 及证据（可为 PENDING），再启用一个或少量候选模块。此模式交付必须标识 `EXPERIMENTAL`；不得冒称正式版。
- `SHADOW`：使用同一冻结目标材料，让候选仅生成平行输出，正式输出仍按稳定通道；不能将额外资源的效果冒称公平比较。
- `ROLLBACK`：切换项目下一步使用的已核稳定指针与功能配置，恢复经过 SHA 验证的旧版**稿件/检查点**作为工作基线，保留所有候选、失败和评审记录。旧稿不覆盖；回滚不等于自动恢复未归档聊天或重新生成完全相同文本。

任何项目必须**显式固定两层有效版本**，上层新版本不得静默传播到旧项目；跨版本升级要先检查兼容和隐私。项目可一直用稳定版，不必等研发完成；候选模块完成一项就可在独立项目自愿试用，无法通过验收则撤销。

## 4. 质量回退的硬规则

一项新改进先提交 `change_hypothesis`（解决哪项真实失败、具体对比谁、增加什么复杂度）。至少在一篇代表性章节/片段上用固定原始输入做**三方比对**：`原素材`、`旧工作流产物`、`新工作流产物`；不只测文件或公式，还测读者理解、具体思想增量、论证、事实、文风与可用性。人工主观评分需姓名或受限可核身份、稿件SHA和评分依据，不能由AI换角色冒充独立人类。

保护策略：

1. 无原始稿与可复核旧版 → `BLOCKED_NO_BASELINE`，不能声称改善。
2. 仅校验工具通过 → `PASS_ENGINEERING_ONLY`，不能声称内容提升。
3. 候选在任何**硬性安全/事实/隐私门**退化 → `REJECT_CANDIDATE`，保持旧默认。
4. 作者或两名真正独立读者明确认为思想价值、文风或可用性整体显著退化 → `HOLD_ROLLBACK_RECOMMENDED`，保留证据，不盲目平均；允许快速返回旧指针。
5. 质量不升、复杂度持续增加 → `STOP_WORK_SIMPLIFY_OR_DELETE_MODULE`；不要把流程膨胀当成进步。
6. 候选仅在一个项目表现好 → `CANARY_ONLY`，不能宣称跨题材稳定提升。
7. 正式升版需有：受控对比、至少三个未参与设计的题目、各自原稿/结果SHA、独立读者实审、作者同意、迁移与回滚验证；没有则 `PENDING_PROMOTION`。

曾得到约60分的项目B原稿是**回归测试基线**而非「系统保底60分」。不能把个别 AI 自评差异当真实升降；不同题材难度不一也不能直接按分数排序。

## 5. 回滚、审计与最小化发布

每个发布对象用不可变 `candidate_id + git_commit + source_sha + artifact_sha + evaluation_sha` 锁定身份。最新 `CURRENT` 不是唯一历史：Git tag/commit、历史文档与私有稿原件都要保留。变更 `CURRENT` 之前输出可逆 `release_record`（父版本、变更列表、迁移、数据兼容、回退到哪个 commit、用户采用项目清单、验收凭证）；发布不触发旧项目自动升级。

`RELEASE_GATE` 至少分 `ENGINEERING`、`CONTENT_QUALITY`、`AUTHOR_ACCEPTANCE`、`EXTERNAL_VALIDATION`。任一缺证据只能是 `PENDING`。工具可以检查 JSON 字段和校验和，**不能自动证明人的评分或事实正确**；这里的测试程序仅负责防止误晋级。真正的回滚是一个带证据的新决定，不覆盖过去。

## 6. 每个增量都可用

默认调用 **「使用当前稳定 DeepWrite 写一本新书」**。试验调用 **「使用稳定 DeepWrite，但本项目试用 [候选模块+commit]，保留稳定基线与回退入口」**。回退调用 **「停用本项目候选模块，恢复最近校验通过的稳定稿/规则，再继续」**。三个操作分别写项目 STATE、保存新检查点，并回读确认。

独立研发不阻塞正在写作的项目。若候选短期不改善作品，先改写作/研究或删减模块，不因追求版本号强制推动所有项目迁移。

## 7. 异步协作

ChatGPT / Codex 通过 `deepwrite/discovery-gate/agent-bridge` 留下不可变编号消息和受限摘要，项目范围整个 DeepWrite 及必要的上游《许愿式交付》；公开 GitHub 不写私人完整原稿、未发布章节、私有评审、盲码与密钥。双方一次交替写文件并在用户提示后读取，不是自动后台运行。由 Codex 优先评估本候选的有效性及是否需要**任何上游通用改动**，按已有 STATE 编号接力，不抢占 0002。
