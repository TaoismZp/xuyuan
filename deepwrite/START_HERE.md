# 新对话启动｜深写 DeepWrite

## 统一调用入口（工程集成待发布）

作者最新目标不是“挑选一个候选模块”，而是**直接说“调用 DeepWrite”就执行全功能默认工作流**。实现和作者可读契约：[DEFAULT_INVOCATION.md](DEFAULT_INVOCATION.md)，执行程序：[`deepwrite.py`](deepwrite.py)。它在完成正式发布后成为由 `release/activation.py` 唯一校验的默认 engine，而不是要求用户手工打开E15/E18/E23和知识复利等模块。

**版本防误报**：本文件存在不代表已经发布；每次先读 GitHub **main** `CURRENT.json`。只有主线指向并验证 `deepwrite/deepwrite.py` 时，才报告新默认引擎已生效。否则本分支只属于工程RC，主线仍可能是v0.1。项目原稿不覆盖、私有材料不公开、真人作者验收不由工程CI代替。

---


## 最短调用

**启动深写：** 我想写一本【主题】的书，给【核心读者】读。我的素材在【文件/连接或无】；我不想要只有目录的大纲，想要序言、完整章节、尾声、必要附录的可连续阅读候选书稿。请先立项、找真实有效的私有存储；以当前生效的《许愿式交付》及深写 CURRENT 执行。一次任务内自行研究、反驳、返工和跨章审稿；不要让我每章都回复“下一步”。遇到执行能力或持久存储限制，给出真实状态和唯一下一步，不虚报完成。

## 执行者必须先做

1. 实读 \`deepwrite/CURRENT.json\`，以及 \`wish-delivery/CURRENT.json\` 和其实际生效版本；不要读候选规范当正式版。
2. 确认任务范围、读者已知/未知、Primary Artifact、原稿只读、隐私、验收比较基线。已给的信息不要反复询问。
3. **先立项**：运行 \`PROJECT_INIT.md\`，创建真实可恢复的 \`PROJECT_ID\` / \`RECOVERY.md\` / \`STATE.json\`；必要时新建私有仓库，能力缺失则将书稿放进私有文件库并记录 \`GITHUB_PRIVATE_REPO_PENDING\`。绝不把私人稿件写进本公开仓库。
4. 原生概念图→章节能力图→两篇代表样章竞争性校准；未达标不得批量成稿。
5. 章内完成思想推演、第二次发现、目标域原生重建、事实公式核验；每3—5章作跨章碰撞审稿。
6. 全部章节完成后再制作序言、尾声、附录/来源表，并做全书连读；不能用单章内部PASS替代读者验收。
7. 绑定证据与文件身份，保存外部Checkpoint并重新读回；下次从最近可靠检查点继续。
8. 若任务过于庞大而无真实长任务执行器，不能许诺用户离开后持续后台写作。应交付本轮能完成的实物和明确的未关闭门。

## 中断后恢复

**断档重生：深写／【项目名称】**。优先读项目专属的 \`RECOVERY.md\`、\`STATE.json\` 和已归档原稿与审稿证据；绝不依靠原聊天或模型记忆来猜进度。若有多个候选项目，按作者指定名称匹配，不替作者选择。

## 一次性交付意味着什么

一次请求/一份完整作品，是**目标形式**。内部可以多次循环，不是“从目录开始按顺序吐完就成功”。DeepWrite v0.1 尚未验证自动完成全书的能力，新项目必须记录真实执行路径与阻塞。

## 工作台本身的迭代（非用户写书任务）

当用户要求 ChatGPT 与 Codex **共同研究和升级 DeepWrite 本身**时，进入 `deepwrite/AGENT_COLLABORATION.md`；通过 `deepwrite/discovery-gate/agent-bridge/README.md` 和 `STATE.json` 以 GitHub 文件进行异步接力。该目录路径沿用历史命名，但范围覆盖整个 DeepWrite，不只 Discovery Gate。公开协作仅放脱敏通用方法；未发表私人材料保持私有。候选改进不得擅自升级 `deepwrite/CURRENT.json`。

## 稳定版与逐项试用（防回退）

**默认可继续调用现有稳定工作台，不必等待下一版研发完成。** 每个真实新书项目读取并固定当次 `deepwrite/CURRENT.json` + `wish-delivery/CURRENT.json` 的有效版本，旧项目不因GitHub更新静默升级。若用户明确要求试用候选模块，则按 `deepwrite/GUARDED_EVOLUTION.md` 的 `CANDIDATE_OPT_IN` 固定具体候选commit、原稿哈希和回滚点。怀疑变差时选择 `ROLLBACK` 恢复旧的已核稿件及配置，保留试验失败记录，绝不覆盖原稿。候选功能质量未经独立实测，不冒称已改善作品。


## 真正执行入口与版本锁

每次新建书先从 **main** 获取真实 CURRENT，在有 Git 与 Python 的环境执行：

```sh
python3 deepwrite/release/activation.py --root .
python3 deepwrite/release/activation.py --root . --run -- identity
python3 deepwrite/release/activation.py --root . --run -- init /private/project-config.json /private/new-project
```

第一条解析规范和工程引擎身份；后两条只有正式 active_engine 已合并、实际提交与全部声明文件核对通过才运行。若 main 仍返回 WORKBENCH_ONLY_NO_LIVE_AUTONOMOUS_RUNNER，必须如实报告没有已激活的工程入口。候选 PR 的 CURRENT 提案不是正式状态。

工程 runtime 负责自动锁定版本、原素材身份、阶段状态、强制实际文件审稿关闭检查、装订与检查点恢复，不默认执行 E18/E23 候选认知提示，也不证明自动成书质量。普通 GPT 对话若不能执行命令，应交由连接了执行环境的 Codex/Work 真正调用；阅读本页不能冒充运行。

旧项目读取 PROJECT_LOCK 的 engine、父协议和 activation_commit；不同身份时阻断，不能静默覆盖旧稿。详细命令、两类发布与真实授权见 [RELEASE_PROCESS.md](release/RELEASE_PROCESS.md)，未关闭的门见 [release/STATE.json](release/STATE.json)。工程补丁与认知升级分别验收。
