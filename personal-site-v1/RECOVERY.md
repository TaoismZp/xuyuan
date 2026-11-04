# 个人长文网站 — 无旧对话接班入口

> **打开本文件即能接班。** 本文及 `recovery/state.json` 是公开项目档案，不是完整 ChatGPT 聊天记录。适用「许愿式交付 v7.5」的 Execution Continuity / Binding Chain Gate。

## 一分钟接班

新对话只需说：

**请从 `https://github.com/TaoismZp/xuyuan/blob/main/personal-site-v1/RECOVERY.md` 接手我的个人长文网站。先读取 `recovery/state.json`、`PROJECT_STATE.md`、锁定的 Vision/Blueprint 和 GitHub Actions 证据；验证最新已交付 commit 与线上版本的身份链，识别未完成 Gate，从最近验收点继续按《许愿式交付 v7.5》施工。不要要求我重述旧对话，不要把计划或 CI PASS 冒充真实站长发文。**

不需要能打开损坏的旧聊天，也不需要导出全部聊天才能恢复**已归档的项目状态**。

## 可打开的真实成品

- 阅读网站：https://taoismzp.github.io/xuyuan/personal-site-v1/
- 本地文章准备/预览/导出：https://taoismzp.github.io/xuyuan/personal-site-v1/write/
- 原有可选 CMS：https://taoismzp.github.io/xuyuan/personal-site-v1/admin/
- GitHub 仓库：https://github.com/TaoismZp/xuyuan

## 唯一可信的工作记录

1. **规范**：`wish-delivery/versions/v7.5.md`，不可用旧聊天的解释代替。
2. **机器恢复点**：`personal-site-v1/recovery/state.json`，包括 Vision/Blueprint Git blob SHA、上次已验收的发布 commit、GitHub Actions run IDs、未关闭 Gate。
3. **人工项目总控**：`personal-site-v1/PROJECT_STATE.md`。两份状态不一致时停止宣布完成，先查仓库历史和 Actions，再修复档案。
4. **设计锚点**：`personal-site-v1/VISION_FIXTURE_V2.md`（用户选的第三版极简方向）和 `personal-site-v1/BUILD_BLUEPRINT_V2.md`。
5. **事实核验**：GitHub Actions 的部署、独立监理和公网 WebKit 验收记录。它们只证明其**对应 commit** 的状态，不能跨版本搬运 PASS。
6. **真实文章**：`personal-site-v1/content/posts/genius-trader.md`；严禁为了验收虚构用户已发表文章。

## 接手后必须执行的顺序

- 读取 state.json + PROJECT_STATE.md，验证重要 Git blob SHA。
- 读取当前 Git HEAD 和工作流结果；区别「最新仓库 commit」与「最新已部署并验收的成品 commit」。仅改档案不会自动变成新站点版本。
- 比对真实公网首页 / 编辑入口和 GitHub Actions 同一发布身份；如果无法核验，标记 **UNVERIFIED**，不得宣称正式完成。
- 检查下一项硬 Gate。当前仍待本人真实发文验收：文章准备 → GitHub 登录并 Commit → Pages 部署 → iPhone/iPad Safari 公网文章核验。
- 每轮已验收施工完成后更新 `PROJECT_STATE.md` 与 `recovery/state.json`，记录 commit、run、未关闭问题和**唯一下一动作**，原始记录不覆盖。
- 重启/换对话时再次从此入口开始，不要求用户复述旧聊天。

## 预防故障：能防什么，不能防什么

- **能防**：旧对话加载失败后项目进度、选定设计、代码、验收证据、施工入口无法恢复；只依赖聊天摘要导致重新做一遍。
- **不能防**：ChatGPT 自身发生 `ConversationDetailError`、授权故障或没有保存的聊天细节消失。完整逐条历史需要账号所有者通过 ChatGPT 设置申请数据导出。
- **不能冒充**：新对话恢复成功 ≠ 旧聊天恢复；公网 URL 可打开 ≠ 已完成站长发文。
- **隐私**：仓库公开。不要放个人聊天数据导出、未发布私稿、访问令牌、账号邮箱或敏感调试日志。

## 可重复的恢复检查

在 checkout 仓库根目录运行：

```bash
node personal-site-v1/recovery/check.mjs
```

GitHub Actions 的 `Verify personal site recovery checkpoint` 在相关 GitHub 修改时自动运行，也支持手动执行。它检验档案、设计绑定 SHA 和关键路径的一致性；公网 URL 检查是独立步骤。**自动检查不能代替真实站长登录验收。**

## 恢复包本身的交付边界

Primary Artifact：本 GitHub 接班入口 + 结构化状态 + 机器检查 + CI 工作流。
Core Loop：新聊天打开入口 → 定位上次可靠验收点 → 对照真实 Git/部署身份 → 从未关闭 Gate 继续。
Delivery Surface：GitHub 浏览器及新 ChatGPT 对话；线上网站是被恢复的项目成品，不是本恢复包的替代。
验收：仓库文件可读取，机器检查 PASS，工作流独立 PASS；**实际新聊天无历史接班演练**是单独的使用层验证，未做不得虚称完成。
