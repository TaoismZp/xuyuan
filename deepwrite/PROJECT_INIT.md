# 深写：每本新书独立立项（不得跳过）

> 本文用于书籍项目。本体方法迭代应另建方法 PROJECT_ID、STATE、RECOVERY 与四件套；仅公开方法和明确合成的测试可用公开目录，不得混入真实私人书稿。已有书籍项目先恢复，不重复立项。

## 项目命名
- 为每本书生成稳定ASCII slug \`book-<short-slug>\`，另记录中文工作名；不得用新对话/新版本换项目ID。
- 最好为每本书创建独立的**私有**GitHub仓库 \`<owner>/deepwrite-<slug>\`；如已有已核实的私有项目仓库，可将项目存其隔离目录。公开仓库只放非私人演示/通用模板。
- 创建后立即将可读的 \`RECOVERY.md\` 与机器可读 \`STATE.json\` 提交到项目库。不要以“已经制定目录”冒充立项成功。

## 冷启动按序执行

1. 读 \`deepwrite/CURRENT.json\` 和 \`wish-delivery/CURRENT.json\` 实际生效规范。
2. 检查 GitHub 当前权限及项目仓库的 \`visibility\`，明确私密等级。
3. **先建档**：\`PROJECT_ID\`、书名候选、目标读者、交付物、现有原稿清单、隐私、禁止项、质量样本、唯一下一步、时间戳。
4. 写入四件套：\`VISION.md\`（读者/可感知结果）、\`BLUEPRINT.md\`（概念与全书能力图）、\`SUPERVISION.md\`（质量证据）、\`ACCEPTANCE.md\`（各门状态）。没有证据就标 \`PENDING\`。
5. 每次写成章节或重大决策后，保存派生稿、原稿哈希、审稿、出处及当前 \`STATE.json\`；重新读取文件和提交身份再判 PASS。
6. 更新项目索引但仅存**不敏感的最小指针**；私有内容和审稿全文都留在可授权的私有存储。
7. 发生超时/中断：标 \`INTERRUPTED\`，下一次执行 \`RECOVERY.md\` 内唯一 \`next_executable_action\`，不要重头问作者。

## 当前 GitHub 工具能力边界

能力必须在当前运行环境实查。下述私有文件库是**条件替代路径**，不是工具保证：只有实际存在可授权、可写、可重新读取的私有库，才能记录已归档。没有时标 `DURABLE_STORAGE_PENDING` / `NOT_ARCHIVED`，交付可导出的本轮候选与恢复卡；工作区临时文件或附件不能自动证明跨对话持久存储。GitHub 仓库 PENDING 与文件库已归档是两个独立状态。

截至2026-11-08，本次连接可读写已有仓库，但**没有可调用的新建仓库动作**。因此不能声称“每次都自动建新的私有仓库”已经实现。

如果新仓库不能创建：**在 ChatGPT 私有文件库建立项目专用独立文件夹并归档原稿、审稿、STATE与RECOVERY，使用 \`GITHUB_PRIVATE_REPO_PENDING\` 状态，绝不上传到公开仓库**。有能力或用户创建并连接私有项目仓库以后，再迁移并按SHA验收。不要因为欠缺私有GitHub仓库就推断私人文件已公开或丢失。

## 项目建议目录（仅在确认私有后用于实际项目）

\`\`\`text
README.md
RECOVERY.md
STATE.json
vision/VISION.md
blueprint/CONCEPT_MAP.md
blueprint/BOOK_BLUEPRINT.md
chapters/01/v1.md
chapters/01/audit-v1.md
chapters/01/ledger.json
book/assembled-v1.md
references/SOURCES.json
qa/CROSS_CHAPTER.md
qa/ACCEPTANCE.json
history/DECISION_LOG.md
\`\`\`

模板：[RECOVERY](templates/RECOVERY.md) · [STATE](templates/STATE.json) · [ACCEPTANCE](templates/ACCEPTANCE.json)。

## 私有仓库确认

读取仓库元数据 \`visibility=private\` 并核对写入权限后，方可上传原稿。仓库公开→ \`STOP_WORK_PRIVACY\`。新建私有仓库本身也不能保证外部系统数据不出意外，应有独立私有备份。
