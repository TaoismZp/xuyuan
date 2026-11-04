# 可移植 AI Skills：苏格拉底审题 × 精英思维

面向可以读取 GitHub 文本或本地工作目录的 AI Agent。按照 [Agent Skills 规范](https://agentskills.io/specification)组织，每个 Skill 的 **SKILL.md 独立可运行**；不会因为文件出现在 GitHub 就自动被所有 AI 加载。

## 文件入口
1. [苏格拉底审题 / socratic-review](socratic-review/SKILL.md) — 澄清概念、找枢纽假设、反证与最小验证。
2. [精英思维 / elite-thinking](elite-thinking/SKILL.md) — 定义目标与约束，1 主工具 + 至多 3 辅，输出行动和更新条件。
3. [精选模型路由表](elite-thinking/references/MODEL_ROUTER.md) — 按问题选模型，而非滥用全部理论。
4. [测试用例](TEST_CASES.md) — 可复制到另一个 AI 检查是否真的按规则做。

## 最快使用方式
有 Agent Skills 支持的 AI：将两个目录复制/安装到该产品的 Skill 发现目录（例如项目的 .agents/skills/）；按具体产品文档启动/刷新。Codex、Claude Code 与其他 Agent 的全局安装位置可能不同，不要假装所有客户端会自动扫描这个 GitHub 路径。

没有自动 Skill 机制的 AI：先读取对应 SKILL.md 全文，遇到模型选择问题时再读取 references/MODEL_ROUTER.md，然后用以下指令：

> 阅读并执行 socratic-review/SKILL.md 和 elite-thinking/SKILL.md。先独立形成初步判断；用苏格拉底审题找会推翻判断的关键假设与反例，再用精英思维选 1 个主模型（最多 3 个辅助）运行机制，给可执行下一步、真实证据和更新条件。不得把提问、模型名称、报告数量冒充任务完成。

单独调用：
> 只使用 socratic-review 审查以下方案，给 1 个最大前提漏洞和 1 个最小验证动作：[方案]

> 只使用 elite-thinking 分析以下选择。先给结论，再写 1 个主模型、反证、下一步和停止条件：[问题]

## 组合工作顺序
任务原始输入 → 独立初判 → 苏格拉底：定义/前提/反例 → 精英思维：主工具/机制/行动 → 反向审查模型是否偷换目标 → 真实执行与验收（若已授权） → 记录失败与更新条件。

## 来源、适用边界与版本诚实性
- 精英思维是基于用户私人原稿的**精简原创适配版**，没有把原始长篇教材全文放到公开仓库，也不宣称包括所有一百个工具。
- 苏格拉底 Skill 来源于已留存的审题实践和六类方法；同名 Mac 本地原始 SKILL.md **尚未核对**。所以当前标记 RECONSTRUCTED，不冒充 ORIGINAL VERIFIED。
- 版本 1.0.0 代表此处的 GitHub 可使用文件，不代表私人原稿的版本。
- 两个 Skill 均为文本操作规范，不自动取得浏览器、外部仓库、用户文件或执行权限；关键事实需另行核实。
- 公开仓库不得保存私人素材、凭据或未经授权的长篇原稿。
- GitHub 中生效的《许愿式交付》请单独核对 [CURRENT.json](../../wish-delivery/CURRENT.json)（若相对链接无法解析，请使用仓库根部的 wish-delivery/CURRENT.json）；此处 Skill 不改写该规范。

## 验收约定
**PASS**：文件真实存在并可复读、frontmatter 结构合规、文件内调用示例完整；
**UNVERIFIED**：其他 Agent 是否能够自动发现/按要求执行，须在该 Agent 上实际测试；
**PENDING**：本地原版苏格拉底 Skill 与此重建版的逐条比较。

内容变更应新增版本说明和测试证据，不要把“创建文件成功”升级成“所有 AI 都已兼容”。
