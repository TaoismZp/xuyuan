# 许愿式交付｜CHANGELOG

> 说明：v1.0–v7.0 为根据实际项目事故与迭代过程整理出的历史脉络；从 v7.1 起，每次实质迭代都必须在 GitHub 产生不可变版本文件。

## v7.1 — Git Persistence
**触发事故**：系统规则只存在于聊天/记忆中，长期项目容易出现“已经约定但无法恢复”的问题。

**新增硬规则**：
- 每次实质迭代必须创建 `versions/vX.Y.md`；
- 旧版本不覆盖；
- README 指向当前版本；
- CHANGELOG 记录触发事故、根因与新增约束；
- GitHub 提交完成才算系统迭代真正落地。

## v7.0 — Silent Finished Reality
**触发事故**：即使产品尚未满足“可玩性极强”，系统仍不断向用户汇报 Gate、测试通过和下一阶段计划。

**新增硬规则**：
- Silence Contract；
- Process Leakage 视为系统失败；
- Anti-Fake-Final：只要还存在明确“下一阶段”，就不能交 Final；
- Intent → Silent Execution → Finished Reality。

## v6.x — Working Reality & Delivery Surface
**触发事故**：截图、ZIP、本地 HTML 被误当成产品交付；真实 iOS/浏览器入口不可用。

**新增硬规则**：
- BUILD → LIVE → VERIFIED → USER-ACCESSIBLE；
- Delivery Surface Contract；
- Same-Surface Verification；
- Localhost 通过不能替代真实入口通过。

## v5.x — Execution Environment Sourcing
**触发事故**：GitHub 一条路径受阻时，系统反复让用户排查权限，而不是自己寻找替代执行环境。

**新增硬规则**：
- 不只选择 Skill，也选择执行环境；
- ChatGPT / Codex / GitHub Actions / Work / 插件按能力分工；
- 单一工具失败自动寻找替代路径。

## v4.x — Design Quality & Independent Evaluation
**触发事故**：FIN·TYPE 前端“能运行”但美工差；生产者自己定义 rubric、自己打高分，形成自证循环。

**新增硬规则**：
- Reference-first Design Quality Gate；
- Producer 不能成为唯一 Evaluator；
- “反模板”不等于“好看”；
- 设计必须对标真实成熟产品和用户偏好。

## v3.x — Artifact Contract & Capability Sourcing
**触发事故**：币圈大富翁、金融 MBTI 只交规划、题库和 PRD，没有真实产品。

**新增硬规则**：
- Artifact First；
- PRD ≠ 产品，规则书 ≠ 游戏，题库 ≠ 测试产品；
- Capability Gap Analysis；
- 主动搜索 GitHub / Plugin / Skill；
- 候选 Skill 必须与裸模型及其他候选实测后才能采用。

## v2.x — Quality Constitution & Source Fidelity
**触发事故**：《弱者的活法》V4 结构更干净但作者性、场景、物件、粗粝感和发现过程被压掉，形成“正确的通识说明书”。

**新增硬规则**：
- Quality Constitution；
- Source Fidelity Contract；
- Living Material Ledger；
- Comparative Regression Gate；
- 用户整体否定视为 Evaluator Failure，而非普通局部修改。

## v1.x — Autonomous Completion
**触发事故**：长项目需要用户不断说“继续推进”，系统把用户当成流程时钟。

**新增硬规则**：
- 成熟目标默认自治推进到成品；
- 用户不负责反复确认中间步骤；
- 除重大方向问题外，不中断生产链；
- 目标从“协作过程”转向“终稿交付”。

## 永久失败样本
- Planning-as-Delivery
- Summary-as-Authoring
- Screenshot-as-Product
- Localhost-as-Live
- Delivery Surface Substitution
- Producer-as-Judge
- Process Leakage
- Retry-as-Workflow
