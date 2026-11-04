# Agent Skills 信息损失与可移植性审计（2026-11-04）

## 结论

当前 GitHub 版的**文本传输一致性已核验**，但它不是原始两个私有 Skill 的完全等价副本，也还没有真实独立的 Codex/Claude/Copilot 行为对照结果。

- **苏格拉底**：GitHub `socratic-review/SKILL.md` 是从既有实践重建的操作方法；原始本机文件在本次执行环境没有挂载，**逐条原版对照 UNVERIFIED**。
- **精英思维**：私有文件库存在一份约 **185,794 字节**的原始《现代思维工具100讲》技能资料；可检索到它含**十大板块**及逐模型“何时调用、机制、Agent 程序、诊断问题、边界与输出”等细节。但本次接口仅允许检索片段，完整全文读取和原始字节导出都未成功。因此不能说完成了 100 工具全量迁移。
- 原先 GitHub `elite-thinking` v1.0 仅有十项精选模型路由。v1.1 在不复制私人长篇内容的前提下，增加十大**领域路由**，修复了模型选择阶段的部分覆盖漏洞；逐模型详细程序仍不完整。

## 验收矩阵

| 维度 | v1.0 | v1.1 | 证据/界限 |
| --- | --- | --- | --- |
| GitHub 传输可读 | PASS | PASS | GitHub 原文件回读 |
| Codex、Claude Code、Copilot 的三份目录镜像一致 | PASS | PASS | 四个对应文件 SHA256 三份匹配 |
| YAML 技能识别字段可读 | PASS | PASS | 静态检查 |
| 简易模型路由 | 10 个候选情境 | 保留 | `MODEL_ROUTER.md` |
| 原稿的十大问题领域 | **覆盖不足** | **十大领域入口具备** | `DOMAIN_ROUTER.md`；不等于逐模型能力完整 |
| 原稿每个模型的 Agent 程序/诊断问题/边界 | 缺失大部分 | **仍未恢复** | 原文无法完整读取；不可宣称原版全量 |
| 其他 AI 独立盲测 A/B/C | PENDING | PENDING | `STRESS_TESTS_V2.md` 是可执行测试规格，未有真实第三方输出 |
| 原版苏格拉底 1:1 一致 | UNVERIFIED | UNVERIFIED | 本机原稿未取得 |

## 实际成功测试：静态完整性

Workflow: https://github.com/TaoismZp/xuyuan/actions/runs/41852234657

- 检查脚本：`scripts/check-agent-skills.mjs`。
- GitHub Actions：**SUCCESS**。两份 SKILL.md + 两份模型路由文档，共四类文件 × 三种目录位置，内容一致；元数据可解析；十大领域/十条新压力测试覆盖检查通过。
- **注意：该 CI 从未调用任何 AI 模型。** 它证明文件及分类结构存在，不证明其他 AI 的推理质量或真实 Skill 自动加载。

## 为什么没有在 GitHub Actions 直接调 GitHub Models

GitHub 官方在 2026-07-01 宣布，GitHub Models 包括模型目录、推理 API 等，于 **2026-07-30 全部退役**：https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/

2026-11-04 时该接口已不应作为可用的独立模型测试环境，故本轮没有创建一个注定失败的 GitHub Models workflow，也没有假称调用了 Claude/Codex。真实外部模型测试需要经授权可用的客户端/模型服务，不允许私自开启付费服务或捏造运行。

## 下一步验收规格（唯一未闭环核心）

用 `STRESS_TESTS_V2.md` 的题目，在**同一实际客户端/同一模型版本**盲评：
1. A：不加载 Skill；
2. B：加载原 v1.0 精简 Skill；
3. C：加载新 v1.1 十领域路由；
4. 保留全文输出、独立评分、自动加载证据和差异分析。

若要测试**原始 100 工具版 D**，须先在授权环境取得原稿全文、确认版权/隐私边界、只在私有环境运行，不能将原稿直接推入公开仓库。

## 来源纪律

本审计只公开方法结构、可检验事实、Git 提交与静态测试链接。**没有**把私有 Skill 原稿、本地私密路径、账户资料或版权课程正文公开。
