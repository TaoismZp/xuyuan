# 深写｜DeepWrite 跨对话恢复入口

先读取实际 [CURRENT.json](CURRENT.json) 与[父框架 CURRENT](../wish-delivery/CURRENT.json)，不要凭聊天记忆、候选分支或本页历史版本判断正式身份。未发表正文与私有审稿只从已授权项目恢复档案读取，不进入公开仓库。

## 当前工程任务

2026-11-12接续现有E18/E23/E24，打通工程验证、发布授权、正式激活、实际调用与回退。不是重新开发，也不代表认知能力或整书质量验收通过。

- 状态、未关闭Gate、唯一下一步：[release/STATE.json](release/STATE.json)。
- PR关系、实读身份和测试来源：[本轮盘点](release/evidence/2026-11-12/INVENTORY.md)。
- 现有发布机制：[release/RELEASE_PROCESS.md](release/RELEASE_PROCESS.md)、[release/activation.py](release/activation.py)。
- 开始时正式DeepWrite v0.1、父规范v7.6；PR14尚未合并或激活。后续版本重新读取main CURRENT、发布记录与API。

在具备Python、Git和仓库读取能力的真实执行环境运行：

```sh
python3 deepwrite/release/activation.py --root .
```

该命令解析正式身份；返回WORKBENCH_ONLY_NO_LIVE_AUTONOMOUS_RUNNER时不能说自动写书已启动。普通GPT对话读提示词不等于调用Python引擎。旧项目继续固定私有STATE中的版本，禁止静默升级或覆盖旧稿。

## 未关闭的门

本轮配置写入实际出现403 Resource not accessible by integration；admin:true不是写权限证明。必需CI、自动合并、所有者发布授权、新环境正式运行及正式回退均须真实核验，准确状态见release/STATE.json。

E1自主整书、E2完整作品公平盲评、认知升级的作者和独立读者验收继续开放。工程样例、字节恢复、局部勘误及AI复核不能替代这些门。

## 原协作与真实创作

原联合审查入口仍为[协作桥STATE](discovery-gate/agent-bridge/STATE.json)，本轮工程状态独立；没有覆盖书稿进度、读者范围或作者外发决定。

新书/旧书按[START_HERE.md](START_HERE.md)、[PROJECT_INIT.md](PROJECT_INIT.md)及该项目私有RECOVERY/STATE立项或恢复。原稿保护、隐私隔离和持久检查点先于正文落盘。形成史见[HISTORY.md](HISTORY.md)，隐私见[SECURITY.md](SECURITY.md)。

唯一下一步：root按release/STATE.json完成真实发布链与失败回退验证，回读正式文件、提交和配置后更新；不足权限的步骤明确BLOCKED。
