# 调用 DeepWrite｜统一默认调用契约

> 用户愿望：“只要说调用 DeepWrite，就能自动使用以前完成的所有适用功能，而不必知道版本、PR号、候选模块或自己决定目录。”

## 人类用户如何调用

在已连接 GitHub、具有可执行环境的 Codex 或 ChatGPT Work 中，直接说：

> 调用 DeepWrite，写一本关于【题目】的书。原始资料在【私有资源位置】。以【读者和目标】为准。希望一次性完成整书候选／先写样章给我审。

**不要求读者知道** E15/E18/E23/PR号、source-first/insight-source modules、章节数或具体研究流程。系统负责获取真实素材、检查现有项目恢复入口、冻结授权、选型、保存真实产物并回读。

在仅提供文本和公共GitHub浏览权限、不能执行本地Python或合法模型API的ChatGPT会话里，这句话**不是后台执行的证明**。不得答复“已经调用真实DeepWrite引擎”而只是在聊天中写了一个大纲。环境能力不足时必须记录 BLOCKED、可审原稿和唯一下一步。

## 默认完整执行流（一个作者愿望，不是一次模型输出）

1. 恢复：先核对 `deepwrite/CURRENT.json`、`wish-delivery/CURRENT.json`、项目私有 RECOVERY/STATE 和实际文件SHA；新书才立项，旧书不覆盖。
2. 来源：冻结私人原始资料、来源授权和原话，默认读者不知道源领域；禁止把课程目录照搬成章节目录。
3. 先研究：源学科原生机制、错误的常见理解、反证与多个研究问题（PR17结构性原生问题竞争）；区分作者明确投喂的视角与未经揭示的模型提议，不将前者记为独立发现。
4. 再架构：用读者知识依赖图生成临时章数、章序、每章独占读者变化，允许合章与删章；不是固定12章、13章或源课篇数。图一旦进入写稿要冻结为可核状态。
5. 作者授权：`ASSISTED_AUTHOR_GATED` 仅首章先写并停在样章验收；`AUTONOMOUS_FULL_DRAFT` 可在明确授权范围内内部完成各章、全书复核，但不等于作者同意发表。两者不能混用，作者本人新授权需要外部来源。
6. 写章：E18实际生成可阅读Markdown文件；源领域先解释其重要性及前置误区，目标领域重新推机制；逐章完整论证，严重源错误和审稿 MAJOR/CRITICAL 必须真的修改正文并重查，内容过度缩短触发保全审查。
7. 读者质量：要求对新手、熟手、高手的实质认知变化审稿，不强行三段模板。王路“知识复利”的结构率、折旧率、门槛长度、可压缩性、外溢性、正负符号用于审稿判断；必须提出跨章节或陌生情境迁移问题，不能让读者只会复述例子。
8. 跨章与整书：对每章核心发现是否独占、案例/论证同构重复、数学与因果、前后文声音和结构做检查；G6/G7整体返工，序尾、正文、必要来源附录，原件版本只读。对于全书候选，新增一次有证据的结构重审：可以合理KEEP；确需改变章数或顺序时，建立新的私有派生项目重新运行E18，旧稿保持不变。模型不能自行证明改稿更好。
9. 交付与恢复：书稿、返工diff、来源与原稿SHA、审稿、配对对照、实施模型/成本、独立验收状态、唯一下一步保存在有权限的私有项目。**保存后重新读取**，若不能持久化标“尚未归档”并交接。公开xuyuan仅允许通用方法与模拟测试。

## 可执行单入口（具备 Git / Python / 模型授权）

在已经正式部署并选择为STABLE的Git checkout上，统一通过发行解析器：

```bash
python3 -B deepwrite/release/activation.py --root . --run -- \
    run /private/deepwrite-user-request.json /private/deepwrite-project
```

查询正式项目也经过同一发行解析器：

```bash
python3 -B deepwrite/release/activation.py --root . --run -- \
    status /private/deepwrite-project
```

恢复先核验项目的版本锁，使用锁定版本检出；提供**外部保存的 `writer_project/run_state.json` 实际 SHA**，而不是让模型自行宣布已取得作者批准：

```bash
python3 -B deepwrite/release/activation.py --root . --run -- \
    resume /private/deepwrite-project --expected-state-sha256 <64-hex>
```

样章审过后，追加外部作者回执 `--author-approval-receipt /private/approved.json --author-approval-sha256 <64-hex>`，回执必须绑定**精确项目、执行合同SHA、首章稿件SHA与非模型的作者决定**；没有则继续等待而非自动同意。

上述命令由执行环境发起，**在ChatGPT普通聊天里读到命令不等于已运行**。

## 最小作者请求（样例不包含私人材料）

用户无需选模块。真实项目只提供目标、素材、读者与明确授权方式，例如：

```json
{
  "schema": "deepwrite/one-call-author-request/v1",
  "project_id": "new-book-2026-01",
  "wish": "从原学科知识出发，独立研究再写一本让读者形成新判断能力的书",
  "working_title": "待研究的新书暂名",
  "reader_goal": "新手有趣、熟手有新理解、专家不觉简单，并让概念形成知识复利",
  "source_files": ["/private/source-course.md"],
  "adapter": "codex",
  "model": "an-explicit-available-codex-model-id",
  "mode": "ASSISTED_AUTHOR_GATED",
  "authorized_scope": "FIRST_SAMPLE_AFTER_DISCOVERY",
  "min_chapters": 1,
  "max_chapters": 20,
  "discovery_token_budget": 20000,
  "token_budget": 150000,
  "per_call_output_tokens": 5000,
  "max_revision_rounds": 3
}
```

作者明确一次授权全书时，才使用 `mode=AUTONOMOUS_FULL_DRAFT` 且 `authorized_scope=ALL_CANDIDATE_CHAPTERS`；不要将用户的“继续”误当签收或新增整个项目的授权。原始request文件只能由有权限的人在私人工作区提供，CLI保存原字节及SHA；**请求文件存在不等于加密身份鉴真。**

## 能力与证据分层

|能力|执行状态|仍需外部检验的边界|
|---|---|---|
|源学科独立研究和竞争解释|模型调用阶段已接线；脚本模型工程回归通过|是否得出真正好的发现UNVERIFIED|
|不预定章数、研究后动态生成章节|真实阶段顺序/配置接线；模拟PASS|章数/章序是否合理、结构重编是否改善全书UNVERIFIED|
|E18章节真实文件生产/源码优先/审稿返工|真实文件工程样例PASS|实际合法provider长书闭环未完成|
|两种作者模式|模拟样章停机和一次性写作PASS|真实作者身份与签收不由模型判|
|读者三层和六维知识复利|真实章节审稿门/新情境探针PASS（结构）|真实新手/熟手/高手的增益和迁移UNVERIFIED|
|独立洞见 vs 作者指导|源问题竞争与作者来源归类已接入默认链|“真正原创”/盲揭示仍不能靠模型自己证明|
|跨章深审/整书修订/失误闭环|合成文件、原稿保护与检查点PASS；现有全书重查后可KEEP或在证据支持下派生新目录并完成E18第二次全书候选（模拟PASS）|改稿效果、真人比较及实战一次成书不劣于逐章UNVERIFIED|
|盲评A/B与外部人类评分|`deepwrite/evaluation/blind_reader_trial.py` 实际封存作品A/B、分离映射密钥并采集真实读者答卷；工程测试PASS|真人样本/公平等预算对照未做，不能用AI评分代替真人|
|统一入口与版本恢复|发行解析器核对CURRENT/record及实际入口；新main调用已有工程证据|实际版本每次重读CURRENT；不自动把能力注入所有普通GPT会话|

## 思想来源与读者目标

“新手看得懂、熟手有纠偏、高手能检查机制与边界”是同一篇可读叙事的目标，不是三个固定小节或三项自评分。新手需要理解源场景并处理变式，熟手需要实质认知修正，专家需要可检验机制和反例；实际收益须另验。

R4 的积极反馈来自作者引导下的一章，可作为私有回归参照，不能记为模型自主发现或跨主题成功。请求若含已知作者指导，应将其保存在 `source_files`，用可选的零基 `author_guidance_source_index` 固定对应来源；执行器记录 `AUTHOR_GUIDED`、`USER_SUPPLIED_PERSPECTIVE` 和 `count_as_autonomous:false`。未揭示的模型建议仍为原创性待验，不因自报“独立”而通过。

## 正式身份与历史工程回执

每次调用先读取远端 main 的 CURRENT，用新的检出或隔离工作树核实提交，再由 activation 验证真实引擎。仅候选分支存在不生效；新正式版本也不静默升级旧项目。候选试用须有项目级授权和独立私有目录。

PR #21 合并后的固定工程证据：main `dae2c7de1bcda8c3f511bc05d690c4269deae4c2`，[Actions 43583578870](https://github.com/TaoismZp/xuyuan/actions/runs/43583578870)，312项工程测试成功，全新 main 的正式身份调用成功。它不是真实模型整书或读者质量验收。后续版本以 CURRENT 及其 release record 为准，本段不定义“最新版”。

此前 RC2/PR20/247或312项候选测试及“main仍v0.1”的说法属于当时记录，见 [UNIFIED_RELEASE_CANDIDATE.json](UNIFIED_RELEASE_CANDIDATE.json) 的历史字段。当前发布与治理门见 [release/STATE.json](release/STATE.json)：现有管理 API 403、必需检查配置或 auto-merge 缺口不能因入口已激活而改记 PASS。
