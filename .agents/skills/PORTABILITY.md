# 使用 / 安装指南（Codex · Claude Code · Copilot · 其他 AI）

> 这些是符合 Agent Skills 目录约定的**文本执行规范**，不是可执行程序；提交 GitHub 并不等于你正在使用的 AI 会自动加载。是否发现及执行，必须在具体客户端验证。

## 方式一：在本仓库中使用（项目级 Skill）

| 工具 | 本仓库扫描路径 | 你应当看到 |
| --- | --- | --- |
| OpenAI Codex | `.agents/skills/{socratic-review,elite-thinking}/SKILL.md` | 可选择的 `socratic-review`、`elite-thinking` |
| Claude Code | `.claude/skills/{socratic-review,elite-thinking}/SKILL.md` | Skill 列表/匹配触发 |
| GitHub Copilot（支持 Agent Skills 的 VS Code / Agent 环境） | `.github/skills/{socratic-review,elite-thinking}/SKILL.md` | 对应可用 Skill |

**检查实际调用，而不仅仅看文件**：在目标 AI 会话中请求“仅使用 socratic-review 回答 TEST_CASES.md 的 S1”，确认它识别 Skill 并输出正确行为；然后运行 E1、X1、F1，保存输出。工具版本、权限、Skill 开关、会话启动时机都会影响是否生效。

官方资料：
- Agent Skills 规范：https://agentskills.io/specification
- OpenAI Codex：https://learn.chatgpt.com/docs/build-skills
- VS Code 对多种 Harness 的目录约定：https://code.visualstudio.com/docs/agent-customization/agent-skills
- Claude Code：https://support.claude.com/en/articles/14554000-claude-code-power-user-tips

## 方式二：在其他项目/全局重复使用

将**一个 Skill 目录整体**复制到目标工具支持的位置，保留所有子目录，尤其 `elite-thinking/references/MODEL_ROUTER.md`。

- Codex 全局：`~/.agents/skills/socratic-review/` 和 `~/.agents/skills/elite-thinking/`。
- Claude Code 全局：`~/.claude/skills/socratic-review/` 和 `~/.claude/skills/elite-thinking/`。
- GitHub Copilot 项目级：`<target-repo>/.github/skills/<skill-name>/`。不同 Copilot 产品/模式支持范围不同，以本机文档和实际显示为准。
- 其他没有 Agent Skills 自动加载能力的 AI：让它先读取 `SKILL.md` **全文**，如果用精英思维选择模型，再读取模型路由表；直接用下一节的调用指令，不要谎称“已安装”。

## 复制即用的任务指令

**仅苏格拉底**

```text
请读取并按 socratic-review/SKILL.md 行事：
[你的实际问题]
请给出当前判断、最大枢纽假设、最强反例及最小验证动作。不要机械连问。
```

**仅精英思维**

```text
请读取 elite-thinking/SKILL.md 和 references/MODEL_ROUTER.md：
[你的实际问题]
只选择一个真正改变决策的主模型，最多三个辅助模型。指出反证、行动、观察量及更新条件。
```

**交叉审查**

```text
请分别读取 socratic-review/SKILL.md、elite-thinking/SKILL.md 和精英思维的 MODEL_ROUTER.md。
先独立判断，再用苏格拉底审题审查枢纽假设、证据和反例，
然后用精英思维解释机制、选择下一步，
最后反向检查模型是否偷换目标或把报告当成果。
遇到简单问题直接回答，不强行触发 Skill。
```

## 同步与来源纪律

- 规范源：`.agents/skills/`；Claude、Copilot 目录是**相同内容镜像**。
- 编辑某个 SKILL.md 或参考文件后，必须把相同修改同步到另外两个目录；比较文件内容或 blob SHA，发现差异不得声称同步完成。
- `TEST_CASES.md` 与运行记录目前以 `.agents/skills/` 为规范位置，无需三份复制。
- 公开仓库不放私人原稿、完整聊天、未授权稿件或账户信息；GitHub 精简版不等于未经核对的私人“原版”。
- 每个 AI 客户端自己决定工具权限；Skill 本身不授予访问/执行/写入权限。
- 代码安装与镜像复制均不代表已通过真实模型行为测试。

## 验收最小流程

1. 验证目标客户端是否发现了 Skill（不是文件仅能被手动浏览）。
2. 从 `TEST_CASES.md` 运行 S1、E1、X1、F1，保存输入、完整输出、客户端/版本和实际加载方式。
3. 按 rubric 判断 PASS / FAIL；若仅本模型自己评分，标记 SELF_ASSESSED，不算第三方独立 PASS。
4. 发现失败时修规范源，维护三目录一致；保留上一版本与新增测试记录。
