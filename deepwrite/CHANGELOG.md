# DeepWrite Changelog

## v0.1 · 2026-11-08
- 正式命名为**深写｜DeepWrite**，约定新对话“启动深写：...”与“断档重生：深写／项目名”。
- 将原先私有文件库内“一次许愿、多轮内循环”的候选结构整理为公开可移植工作台入口。
- 存档脱敏形成史、8道质量门、项目立项模板、独立A/B与实际能力缺口。
- 引入\`deepwrite/CURRENT.json\`作为工作台自身版本入口；不改动\`wish-delivery/CURRENT.json\`及其active v7.6。
- 公开通用哈希验证装订工具；禁止把原始未发表稿、聊天、私人检查点写入公开仓库。
- **E1自主整本成书**：NOT_IMPLEMENTED；**E2独立盲审比较**：PENDING。
- GitHub当前连接未暴露“新建repo”写操作：每本书必须独立立项；没有私有仓库创建能力时只能暂以私有文件库及显式未关闭门保存，不能暗用公开库。

## 候选工程增量 · 2026-11-09（不升正式版本）

- 恢复实际CURRENT：DeepWrite v0.1、父协议v7.6；未修改指针。
- 核验旧release_guard九项测试只验结构；新增畸形输入/严格布尔拒绝及能力标识。
- 增加显式自愿启用的本地checkpoint snapshot/verify/restore；原件与失败候选保留，全新目录恢复，外部manifest SHA固定身份。私有耐久存储与完整作品质量回滚未验证。
- 系统诊断、两项目证据分级、三原则构造性反向检验及实际字节恢复证据：`experiments/2026-11-09-system-review/`。不是独立盲评，不关闭E1/E2。
- 修复研发恢复入口过时下一步，接力事实以agent-bridge STATE与不可变消息为准。

## 0004候选工程收尾 · 2026-11-09（不升正式版本）

- 实跑0003的F1漏文件/F2稳定声明却开启候选负例，保留字节PASS与项目检查BLOCKED的区别。
- 新增显式自愿、只读的resume_check：按独立冻结清单检查漏存、双层pin值与候选ID/commit冲突；稳定功能和合法opt-in对照通过。不是完整项目、授权或耐久验收。
- 字节命令及receipt显式标注project_resume_gate NOT_RUN、complete_project_recovery UNVERIFIED。旧manifest/恢复接口保留，无静默迁移。
- 回执、复跑命令、格式限制和停用说明：`experiments/2026-11-09-resume-boundary/`。E1/E2及真实作品质量门继续开放。
