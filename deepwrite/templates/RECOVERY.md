# DeepWrite 项目恢复入口模板

> 复制到**已经核实隐私级别的项目存储**。此文件是空白模板，不是新项目实际检查点。

- PROJECT_ID: \`REPLACE\`
- 工作名: \`REPLACE\`
- 目标读者: \`REPLACE\`
- 当前阶段: \`PROJECT_CREATED\`
- LAST_GOOD_CHECKPOINT: \`PENDING\`
- 真实可读原稿: \`NONE\`
- 当前候选版本与文件SHA: \`NONE\`
- 最近审核状态: \`UNVERIFIED\`
- 隐私等级与GitHub仓库可见性: \`PRIVATE_REQUIRED / UNVERIFIED\`
- 上级规范: \`wish-delivery/CURRENT.json\` 实际生效版本
- 深写工作台: \`deepwrite/CURRENT.json\`
- 唯一下一步: **读取现有素材并建立原生概念图，未通过隐私门不可写私人内容到GitHub**。

## 接班执行

1. 读取同目录\`STATE.json\`、真实原稿和最新审核证据；核版本与SHA。
2. 检查未关闭Gate，不得继承旧稿PASS。
3. 按\`next_executable_action\`直接工作；需作者本人决定的发布、付款、不可逆操作除外。
4. 每轮存档并重新读取验证；无法写入则明确\`NOT_ARCHIVED\`并生成可复制交接卡。
