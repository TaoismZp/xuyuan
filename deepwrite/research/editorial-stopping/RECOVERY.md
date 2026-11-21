# DeepWrite｜有效改稿 vs 版本冲动：编辑收束门候选（2026-11-21）

**状态：CANDIDATE_OPT_IN / FORMAL_RELEASE_BLOCKED / HUMAN_QUALITY_UNVERIFIED.**

## PR #29 独立复核与续作

原候选冻结为 `b86d2d8732105d2423eec1f363e93167621a0ef0`。审查发现，模型能以 `reader_` ID 或 `computable` 类型跳过原证据门，轻微开放意见可能搭载硬问题改稿，同一缺陷用重叠引文可换名重提，两次软返工上限未跨审稿范围累计。恢复时同一冻结审稿会重算不同的回执。原专用 CI 通过。正式 CI 因 `ACTIVE_RUNNER_BYTES_MISMATCH` 失败，所有者检查返回 `NOT_READY_MAIN_PR`。主分支规则 API 显示 `required_status_checks=[]`、`strict=false`，实际保护仍低于发布协议要求。[原候选专用 CI](https://github.com/TaoismZp/xuyuan/actions/runs/44864055132) · [正式 CI](https://github.com/TaoismZp/xuyuan/actions/runs/44864055136) · [主分支规则](https://github.com/TaoismZp/xuyuan/rules/27040989)

改后，首次对原文、来源与时序提出候选问题，重大主张由新模型调用重新核对原文和损害。精确唯一引文可恢复段落编号，歧义和引文缺失留待复查。一般风格偏好可 KEEP。原回执、改稿尝试及跨阶段软返工计数在私有工作区冻结。候选须明确请求、检出原提交并核对运行文件，恢复期间同一项目加执行锁。修改后对比整章前后、邻章、来源和新增故事冗余，保留旧稿、候选及实际 diff。局部证据可复核，语义判断仍由模型作出。独立人类阅读和作者判断均待取得。

首次真实对照用 `gpt-6.2-sol` 复跑原候选与 `4632a011cf0bf2b987e8a6d5c483c245bc4e5c83`。两边都首轮发现后见信息误用及单一路径收益不能证明策略有效；修正版独立列出并再次定位来源给出的两类可用行动。两边的无重大缺陷样稿均 2/2 KEEP，自动改稿均 0。原候选共 55,314 输入、1,124 输出 token；修正版含额外核对共 71,671 输入、2,540 输出 token。固定每次请求上限 4,200，CLI 事后计量。本对照只测首次审稿和改稿前决定，拦截实际 revise。重复 B 使用两份新审稿会话。样本不足以证明更高的发现率、更少的误报或书稿质量增益。

复跑脚本 `deepwrite/tests/editorial_live_trial.py` 只含公开可复用的虚构材料和本地运行说明。精确候选工程入口回归使用 `python3 -B -m unittest discover -s deepwrite/tests`。需另外执行全书真实模型、完整公平作品对照和独立读者盲评，保留真实失败状态。`PASS_ENGINEERING` 指工程测试，`PASS_SCOPED` 指复核范围内的结论，`KEEP_NO_CHURN` 指本次无足够理由改稿，`HOLD_UNVERIFIED` 指材料不足或待明确的缺陷。作品质量继续标 `PENDING_HUMAN_READER`、`PENDING_AUTHOR` 或 `FAIL`，视实际验收而定。

真实单章写书试跑在下笔前发现来源审阅漏交了 15 个定位，冻结实现 `30ba3196ffd15974d5b914189fc677c53f93428a` 的完整运行因此 `HOLD_UNVERIFIED`。同一稿不重写，专门补一次实际引文位置。候选现在把应复核的概念与维度明确列出，保留第一份审阅，请模型对同一冻结文字补核一次。假引文、未解决的实质问题和其他证据异常仍由原门阻拦。第二次定位也失败则保留 HOLD。工程全链测试覆盖了漏交一次位置、保存原回执、补核成功、真正修正算术并完成装订；结果为 `PASS_ENGINEERING`。此处不能据此认定真实全书完成。

实际复核在同一冻结稿补齐了 15 个定位。后续全链重跑通过来源审阅并写出首章，章节读者复查又暴露了来源输入缺失。修复把相同冻结原始来源或明确标记的可定位摘录传给章节与全书复查，明确允许的严重度，并在装订回归中验证实际收到了原始来源。另用一条虚构对话偏好伪装成文学性 P2，原候选发出修改请求，修正版单独核对后保留原文。这些均为规定范围内的模型或工程结果。

发布类型为 `QUALITY_BEHAVIOR_CHANGE`。先完成候选作品质量证据审查，再由所有者通过正式协议处理授权、保护配置与发布身份。保留草稿，两个 CURRENT、正式记录和现有项目的钉住原样保留。

下文保留原候选的设计和当时的运行证据。

权威正式指针：`main:deepwrite/CURRENT.json` 在开发前核实为工作台 v0.3、引擎 v0.3.1；上游 `main:wish-delivery/CURRENT.json` 正式 v7.6。**本分支不修改两个CURRENT，也不覆盖任何私人稿。** 当前项目完整恢复入口是本文件，`deepwrite/RECOVERY.md` 是上层目录。

## 问题与目标锁

一套带返工循环的长书系统，如果没有停止机制，会把“每次继续都会提出一个新的改善点”误当成提升质量。首次16/16整书阅读可以真实完成，却不等于事前信息约束、跨章文学体验与读者价值都已受审；算术PASS不等于核心推理PASS。已有改稿又会产生新冗余，下一轮再修自己带来的重复，造成连续多个“质量提升”假象。

**目标是两种能力同时提高**：
1. 第一遍就尽可能发现真正的重大缺口：源知识独立解释、当时信息/经济决策、数学事实、读者误解路径、跨章增量、文学节奏，同轮审查。
2. 可靠拒绝无价值迭代：没有可定位伤害就KEEP；风格偏好不产生新R；旧问题无新证据不得换名重开；不能自己修完自己验收就宣称读者受益。

这不是要求完稿“零问题”，而是**没有值得现在再改、证据又充分的关键缺陷，就应该停**。作者/真实读者对文学增益保留最终决定权。

## 改稿前的证据门（接真实调用链，不是新表格替代正文）

候选模块：`deepwrite/tools/editorial_stop_gate.py`；真实执行循环 `deepwrite/tools/writing_loop_experimental.py:review_cycle` 在任何`revise` 模型调用以前，检验`edit_case`、记录留存与身份；成功改稿后再检测是否真的改变了非空白实质文字，之后仍用现有E15及三层读者复核。不能用`semantic_quality=UNVERIFIED`自称思想质量PASS。

需要的依据字段（仅OPEN MAJOR/CRITICAL模型审稿）：
```json
{
  "classification": "FACT_OR_MATH_ERROR | EX_ANTE_CAUSAL_ERROR | SOURCE_MECHANISM_MISSING | READER_CAUSAL_GAP | STYLE_ONLY",
  "baseline_quote": "必须是对应原文段落中真实存在的片段",
  "reader_harm": "旧文究竟会导致什么错误认识或遗漏",
  "minimal_remedy": "最小必要修正与验证方式",
  "regression_risk": "改稿可能损失的机制、声音、推导或节奏"
}
```
模型填一套貌似完整的字段并不构成事实核实或独立盲读；机器只验证**字段、段落真实存在、是否重复提案、是否有实质文本改动**。确切来源真实性、逻辑深度和“更好看”仍要单独审校。

- `FACT_OR_MATH_ERROR`、`EX_ANTE_CAUSAL_ERROR`：真实影响理解与决策的可核问题，尽早修复。
- `SOURCE_MECHANISM_MISSING`、`READER_CAUSAL_GAP`：有明确读者损害的候选深修；需先比较旧稿/新版，不凭模型满意度宣称收益。
- `STYLE_ONLY`：自动降为有记录的KEEP，不为了改而改。
- 找不到对应原文、空洞的伤害说明、缺少最小修法：**HOLD**，而不是让模型假装发现大问题或轻描淡写为通过。
- 相同书稿片段、相同artifact的提案重复出现：**HOLD_REPEAT**；如果真的重新出现新事实，应经独立外部证据另行确认，不能靠模型改ID。**同一冻结章节/同一审稿ID/相同文件SHA的断线恢复重放**不是新一次修改，应被识别为 `REPLAY_SAME_FROZEN_SCOPE`，继续原状态，不重复计数；新的审稿scope仍须阻断旧问题翻案。
- `NOTE/MINOR/KEEP` 及已有独立reader gate不因本模块升级为强制改稿；已有内容保全、源头审查、人工授权仍不受影响。纯源洞见/读者解释类型的P2自动返工上限为**两次**；仍有未解决的关键问题则`HOLD_P2_ONLY_REWRITE_BUDGET_EXHAUSTED`，保留候选、等待作者或独立读者裁决，不自动继续刷版本；事实、算术及事前因果硬错误仍按原有重大缺陷规则处理。
- 事实/数学修复仍不能保证全书文学风格更好，需记录改稿代价。

## 真实可调用模式与版本边界

作者现有默认 `deepwrite/deepwrite.py run ...` **不受本候选修改影响**。未来若正式发布应通过release record＋CI＋真人质量实验；本候选阶段需要在私有新实验项目、明确试验授权下的请求JSON增加：

```json
"experimental_editorial_stop_gate": true
```

这只能在**已检出本候选分支、并具备Git/Python/模型/私有目录的授权执行环境**直接调用候选`python3 deepwrite/deepwrite.py run ...`；不得借正式stable activation冒用新模块，不能直接替旧项目改模块、稿件或项目钉住的引擎。请求文件必须保留原始SHA和合法作者范围。候选入口自动把工程通道标 `CANDIDATE_OPT_IN`，并在项目私有状态/配置钉住代码提交和模块身份；运行失败留可恢复证据。

**停止原因不是胜利宣言。** 如果因缺真实证据而HOLD，标记`REVIEW_INCOMPLETE`/作者或独立读者PENDING；不能把没有发现的问题默认为“全书出版质量PASS”。

## 测试与防止流程膨胀

- 负控：数学无错但事后信息误导（应可提案）、用根本不存在的原文取证（HOLD）、空洞理由（HOLD）、把风格偏好升为重大缺陷（KEEP）、同一错误改名重复出现（HOLD）、没有重大问题（无强制修稿）、空白改写（HOLD）。
- 代码/身份：在真实writer的review和revision调用点有hook，writer_config冻结选用的模块，老项目不因脚本升级而静默变更。
- 工程回归：`python -m unittest discover -s deepwrite/tests -p test_editorial_stop_gate.py -v`（28项候选负控，包含中断安全重放与P2返工次数上限）。PR Action `.github/workflows/editorial-stop-gate-candidate.yml` 测试。**测试结果必须以真实Actions run、实际pass/fail和SHA为准。**
- 质量对照：同样素材/模型/预算下，冻结一本稳定旧稿，比较(1)无门禁旧流程；(2)启用候选。通过两类考试：
  - **抓漏**：包含事前/事后偷换的隐含逻辑缺陷能否在**首次**全书审稿抓出，而非第30轮；
  - **停手**：无明确重要缺陷的版本能否理直气壮地KEEP，是否减少错误翻案和自己引入冗余。
- 盲对照应把“修正真实错误”与“新增文学好处”分开，并记录模型/人工时间、成本、全书连续阅读负反馈、原始稿和候选稿SHA；3个未用于设计的陌生题材不能被熟悉材料的高评分替代。
- 任何三层真实读者和作者评分未获得前：`ENGINEERING_ONLY`，不要声称已经证明质量提高。若提升不够而流程成本更高，则删掉/简化本模块。

## 可靠身份与下一唯一关卡

- 试验代码位于GitHub候选分支 `deepwrite/editorial-no-churn-gate-20261121`。不能直接合并或晋级`main:deepwrite/CURRENT.json`。本公共仓只保存抽象规则/虚构测试，不保存私人书稿、旧项目差异、秘密或真实读者身份。
- 已查GitHub Actions在已提交候选HEAD `fa78029dc25a93ee5a12feba44ec941959e6e235` 上的历史工作流：[`editorial-stop-gate-candidate` run 44863796732](https://github.com/TaoismZp/xuyuan/actions/runs/44863796732) 的 `Compile candidate runtime` 与 `Execute editorial negative controls` job **SUCCESS**（测试文件24项）；同次可见 `owner-release-authorization` job **FAILURE**，不得仅按工作流总体conclusion“success”声称所有发布门通过。
- [`DeepWrite activation rail` run 44863796797](https://github.com/TaoismZp/xuyuan/actions/runs/44863796797) **FAILURE**，失败步骤为 `Resolve CURRENT as the unique source of current engine identity`：候选修改了被正式v0.3.1 release record钉住的文件，而正式CURRENT未发布新SHA，因此不允许冒充stable运行。这是**正式发布身份门阻断**，不是此候选已完成发布或作品质量验收；不能绕过CI或静默更新CURRENT。
- 最新**28项候选负控**实际执行证据为测试代码commit `dd9c049e512a856d2be5108fe9d675b4f6b79f08` 的 [Actions run 44863981156](https://github.com/TaoismZp/xuyuan/actions/runs/44863981156)：`editorial-stop-gate-negative-controls` 的Python语法编译、测试步骤均**SUCCESS**，包含真实review_cycle模型调用前阻断测试、断档同scope恢复与两次P2软修上限；**这只是候选工程PASS_SCOPED，不是真人阅读质量PASS**。
- 当前能证实的是 **候选28项工程负控和Python编译PASS_SCOPED**；全链正式回归 **FAIL/BLOCKED**，实际合法provider完整写书E1、三个陌生题材公平质量E2、作者/真人盲评均 **PENDING**。
- 唯一NEXT：**保留PR #29草稿；对Release rail与owner-authorization阻断进行正式工程/所有者审批，不擅自合并或更新CURRENT。在隔离私有实验上执行真实候选run与交叉reader guard，补真实首次查错与停手对照；通过完整正式回归、合法release签名和作者决定后才讨论晋级。任何人类阅读质量改善无证时不得宣称正式DeepWrite已经具备质量停止能力。**

