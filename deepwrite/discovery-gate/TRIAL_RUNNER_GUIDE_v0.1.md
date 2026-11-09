# Discovery Gate 三题 A/B 实验执行器 v0.1

**状态：通用工具可运行 / 正式生成 NOT_RUN / 真人盲评 NOT_RUN。** 本目录只有通用代码和示例命令，**不含任何作者私人书稿、实验答案、私有匿名映射、API密钥**。DeepWrite `CURRENT.json` 生效版本不受本工具影响。

## 核心实验约束

- 原有预注册（不可静默修改）：每题两组互不读到对方输出，每组最高 **12,000 total tokens**；A沿旧思考法，B沿Discovery Gate；相同冻结题包、模型、工具权限；每组每题3张700—1100汉字思想卡；总计18张。
- 一次调用只含一个 A 或 B 题目和自己的方法提示；`execute_responses.py` 使用6个**全新无状态**请求，`store:false`，不传会话ID、不传此前回答，随机执行顺序，记录原始响应ID及token usage。来源资料以同一个冻结包传给双方；没有额外浏览工具，避免研究预算差异。
- 真实A/B只有在模型API凭证由**执行环境的安全环境变量**提供时才能运行。本工具**不存储密钥，也不能在无凭证环境自发运行**；运行会产生真实API费用。不要在聊天或公共仓库中传输密钥。
- 六份模型输出必须都保留，即使某份出错、长度不足或质量差；不得选择性重跑并弃掉差稿。如果收到不完整JSON，将失败回执存档并停止为 `PROTOCOL_DEVIATION`。
- `seal` 校验模型与提供方一致、SHA对应冻结提示词、每份3张卡、核心字段、汉字数量、token预算等，但**模型返回的执行回执仅能证明表面合规**；运营方需要独立核查实际请求/账单。
- `blind` 输出18张匿名阅读卡和另一**独立秘密目录**中的分组映射，任何评委只能看到阅读卡，不允许看到映射、prompt或原始模型运行日志。
- `aggregate` 要求两份独立评委文件，18张全覆盖、每题五维0—4、具体原文引用和读前/读后决策；结果仍标记 `PROVISIONAL_SELF_ATTESTED_EXTERNAL_AUDIT_PENDING`，**代码不能证明评委是真人或相互独立**。
- 结果阈值为原预注册：B至少两题均分高于A，三题平均净增≥2/20分，事实可信度差值不低至−1/4。仅三题是探索性，不证明可推广。

## 运行方法（在有权限且可联网的执行环境）

在本地安全路径放入**预先冻结的** `TOPIC_PACKETS_FROZEN_v0.1.json` 和原预注册 SHA 记录。不要把私人题包直接提交到公开GitHub。

```bash
python3 trial_harness.py prepare --pack /private/TOPIC_PACKETS_FROZEN_v0.1.json --out /private/prompts
python3 -m unittest -q test_trial_harness.py

# 先只检查命令，不调用 API：
python3 execute_responses.py --manifest /private/prompts/PROMPT_MANIFEST.json --prompts /private/prompts --out /private/inbox --model YOUR_PINNED_MODEL --dry-run

# 只有具备安全环境变量 OPENAI_API_KEY 后且确认费用/权限，才可实际运行：
python3 execute_responses.py --manifest /private/prompts/PROMPT_MANIFEST.json --prompts /private/prompts --out /private/inbox --model YOUR_PINNED_MODEL

python3 trial_harness.py seal --pack /private/TOPIC_PACKETS_FROZEN_v0.1.json --manifest /private/prompts/PROMPT_MANIFEST.json --inbox /private/inbox --out /private/prompts
python3 trial_harness.py blind --sealed /private/prompts/SEALED_RESPONSES.json --sealreport /private/prompts/SEAL_REPORT.json --out /private/reviewer_packet --keydir /private/secret_key
# 先分别取得两名独立真人的盲评 JSON，方可运行以下聚合：
python3 trial_harness.py aggregate --packet /private/reviewer_packet/REVIEWER_ANONYMOUS_CARDS.json --key /private/secret_key/SECRET_BLIND_MAP_DO_NOT_SEND.json --reviews /private/reader_01.json /private/reader_02.json --out /private/PROVISIONAL_SCORE_REPORT.json
```

冻结包应与预注册 SHA `7317b2dd47c8ea300fbc5076b5d423fc3c49e3f23af4b5e01b6bb0fa9a669813` 一致。若不同，立即 `BLOCKED_SOURCE_CHANGED`，先做带版本号偏离记录；不要直接在原实验中替换题目。

## 实施边界与已发现风险

- 当前对话模型已见题包，自己提供A/B观点会违反clean-room，因此不计实验结果。
- 用同一模型API进行6个`store:false`独立请求可以隔离**会话输入**，但仍需审计账号级设置、模型版本变化、工具权限和实际令牌；不同采样结果是随机性的，不可单次实验判定稳定优势。
- 原FAO家庭农业页面可能HTTP 403；其官方同题报道/出版目录可核出处，但**不改变已经冻结的URL**。任何给两组增加的补充全文材料必须在生成前同样冻结并记录协议偏离。
- 不得让同一模型使用三种角色冒充真人评审；不能由结构测试证明观点真的深刻。没有独立两名真人和执行账单，结果是`BLOCKED_EXTERNAL`。

## 检查点恢复

必备 `TOPIC_PACKETS_SHA + PROMPT_MANIFEST_SHA + 原始模型响应+usage + SEALED_RESPONSES_SHA + 盲码映射单独保密 + 两份盲评原始回执 + 预注册总分报告 + 每一步日期/操作者/版本`。任何未完成状态明确写 `PENDING/NOT_RUN`。
