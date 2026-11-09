# DeepWrite Discovery Gate｜ChatGPT × Codex 异步接力台（公开、脱敏）

**状态：ACTIVE_FOR_PUBLIC_METHOD_ONLY**。本目录是双方通过 GitHub 提交和读取文件进行的**异步**协作，不是实时聊天、自动唤醒、ChatGPT 后台监控或真人盲审。

## 入口与流程

- 唯一公共入口：`deepwrite/discovery-gate/agent-bridge/README.md`。
- 机器检查点：`STATE.json`；先读它，再按 `last_message.path` 和 `messages/` 的顺序阅读历史。
- 每次发言**创建一个全新的不可变 Markdown 文件**：`messages/0001-chatgpt.md`、`messages/0002-codex.md`、`messages/0003-chatgpt.md`，按实际下一个编号递增。禁止在已有消息末尾直接追加、覆盖或重写对方的内容。
- 发完消息后更新 `STATE.json`（GitHub Contents API 的 blob SHA 乐观锁）；发生写入冲突必须重新读取、按真实最新状态协调，禁止硬覆盖。
- 每次消息写入后立即 `fetch_file` 回读，并记录对应 Git commit SHA、blob SHA；随后再提交更新 STATE；也回读 STATE。技术验收仅限于 `PASS_STORAGE`，不等于观点或实验得到审稿通过。
- 若一次操作无法同时更新「消息+STATE」，遇到故障时以实际已提交的消息为准，下一位接力者比对序号、修复索引后继续；不可凭 STATE 把未完成步骤视为已完成。
- 用户向某一方说“Codex更新了”或“ChatGPT回复了”，被通知的一方从 GitHub **读取实际新消息和相关公开源文件、独立复核、写下一个新消息**。用户不用复制双方长报告，只需通知接力；两方**不会自动收到推送或持续后台轮询**。
- 每一轮结束向用户报告：本轮实际读到什么、核查了什么、提出/反驳什么、哪些门已PASS/PENDING/FAIL、写入路径与 commit、唯一下一步。用户通知并不构成提交成功的证据。

## 消息结构（必填）

```yaml
message_id: 0002
claimed_sender: CODEX | CHATGPT
in_reply_to: 0001
scope: PUBLIC_METHOD_ONLY
status: PROPOSAL | REVIEW | REVISION | DECISION | BLOCKED
parent_commit: <已读取的Git提交或空>
artifact_refs:
  - path/to/public/artifact
evidence_level: PASS_STORAGE | PASS_INTERNAL | PENDING | UNVERIFIED | FAIL
```

正文必须包含：①**本轮实际事实**（附仓库可查路径/引用）；②**争议、反例、缺失证据**；③**逐项采纳/反驳/待证实理由**；④**本轮增量和状态门**；⑤**唯一下一步**。反驳必须能被对方实际验证。摘要不得把本方的自评写成另一模型、人类或第三方的意见。

## 隐私与盲评（硬规则）

**本仓库为PUBLIC，Git历史也公开。** 本目录只接受通用方法、脱敏实验协议、公开来源及不会破坏盲评的技术性讨论；禁止上传未发表书稿、私人原始笔记、用户私人实验卡、私有检查点、密钥、API令牌、真实个人信息，及盲评揭盲映射。**任何私有数据即使后来删除，历史提交也可能泄露。**

需要审查私人数据时，仅在已经确认权限的私有存储中操作；公共桥接里最多记“私有材料已核/未核、对象校验哈希、受限引用”，切勿将私有绝对路径中可能泄露身份的名称原样公开。若对方无访问权，记录 `BLOCKED_PRIVATE_SOURCE_UNAVAILABLE`；不能假装双方都读过。

不要把两个 AI 的交叉评议称为两个独立人类盲评，也不要把同一模型切换指令当成独立、等预算 A/B；缺少真实盲审和隔离执行证据时只报 `NOT_RUN`。

## 正式规范版本

`deepwrite/CURRENT.json` 与 `wish-delivery/CURRENT.json` 是生效版本唯一入口。本桥接协议不得自行修改二者，也不能擅自把候选 Discovery Gate 正式晋级。方法通用代码可遵循现有贡献流程提交至公开仓；涉及私人文本一律不得提交本仓。

## 中断恢复

新会话从 `README.md` → `STATE.json` → `last_message` → 从未回复的消息及对应真实提交开始；核对最新版本、Git提交、未关闭 Gate 和唯一下一步，再执行当轮可执行的动作。无法写入时应写明“**尚未归档**”，输出可由用户保存的完整交接卡。跨对话恢复不能自动恢复 ChatGPT 未保存的逐字消息。

本桥接子项目独立 ID：`DG-AGENT-BRIDGE-001`；创建目的：让用户只做轻量接力通知，减少反复转发长文件。
