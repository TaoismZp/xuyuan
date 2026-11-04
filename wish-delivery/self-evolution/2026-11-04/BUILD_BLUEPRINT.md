# Build Blueprint — Protocol Self-Evolution 2026-11-04

- Reference: \`VISION.md\`，其冻结规范为 \`wish-delivery/versions/v7.6.md\` blob SHA \`955bdde3d332283ff6ccc89f943555824f741d59\`。
- Primary Artifact: \`wish-delivery/candidates/v7.8-self-evolution-rc1.md\`；附一个少于常规项目复杂度的独立边界引擎和对抗样本。
- Delivery Surface: GitHub 可读的候选协议及 Actions 可复核测试结果；不是站长个人网站或聊天室里的计划。
- System decomposition: Job/Gate0 → Privacy/Integrity → Artifact/Delivery → Owner/Auth → Aftercare → Self-promotion guard。
- Dependencies: Node.js 标准库；无需外部 npm、权限令牌或浏览器才能运行对抗测试。
- Build order: 锁 v7.6 → 候选协议 → 决策器 → 反例测试 → GitHub CI → 手册/监督 → 归档 → 真实任务观察。
- Limit: 引擎只检测输入字段与规则冲突，**不能代替真实工况、用户真实完成或独立审稿**。
- Stop work: CURRENT 指针/旧版本被改、伪造 PASS、私稿意外进公开库、合成用例失败，均立即 FAIL；不得主动晋级 ACTIVE。
- Acceptance blueprint: 静态检查现行规范 SHA 未变、CURRENT 指针未变、无秘密数据、所有正反用例全绿；相同输入可复现；正式晋级 Gate 保持 PENDING_EXTERNAL。
