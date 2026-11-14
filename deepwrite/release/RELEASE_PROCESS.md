# DeepWrite 正式激活与两类发布

正式身份只来自 main 的 `deepwrite/CURRENT.json`，不是聊天记忆或候选分支。工作台规范版本与工程引擎版本独立：保持正式 v0.1 规范时，可以发布只负责身份、装订、检查点与恢复的工程引擎；不能由此默认启用 E18/PR12/E23 认知策略。

当前实际配置与未关闭门见 `STATE.json`；本轮 API 回执见 `evidence/2026-11-12/`。配置请求 JSON 是待执行目标，403 回执不代表设置已生效。

## 唯一执行入口

需要 Git、Python 3.10+、可读的完整 Git 历史及私有输出目录。普通 ChatGPT 对话若没有命令执行能力，只能读取版本、准备愿望和调用具备执行环境的 Codex/Work；不能声称已经运行引擎。

```bash
python3 deepwrite/release/activation.py --root .
python3 deepwrite/release/activation.py --root . --run -- identity
python3 deepwrite/release/activation.py --root . --run -- init /private/project-config.json /private/new-project
```

当前 main 若没有 `active_engine`，第一条如实报告工作台规范，后两条拒绝运行候选。正式合并工程引擎后，入口会核验实际 implementation commit、祖先关系、全部已声明依赖、规范、父版本及不可变发布记录，再真正执行工程 runtime。它不是自主成书质量认证。

新项目自动写 `PROJECT_LOCK.json`、双层 pins、源文件 SHA 和阶段 STATE；私有素材复制进独立目录，不覆盖原件。项目配置最小为 `{ "project_id": "my-book", "wish": "作者愿望", "channel": "STABLE", "modules": {} }`，可加相对配置文件目录的 `sources:[{path,sha256}]`。禁止 `guard:off`，未验收候选不进入稳定项目。

`assemble` 实际调用修复后的 E15 文件门和 PR12 安全装订器，要求审稿清单覆盖所有装订源、外部冻结发现 SHA、真实正文与断言；语义/文学质量仍待作者与读者。`checkpoint` 和 `restore` 调用原有字节恢复工具。每次阶段返回新的 STATE SHA；后续命令须提供该外部 SHA。恢复目标必须是新目录。旧项目 pin 不同则阻断，不能静默升级；使用锁中 activation_commit 检出原正式入口后继续。

## 可自动发布的范围

ENGINEERING_PATCH：实现身份、日志、恢复、装订、已生效规则的执行修复。必须有真实 CI、回归、恢复证据及所有者对精确 PR head 的授权。工作台规范与认知模块不能在此通道改变。

QUALITY_BEHAVIOR_CHANGE：研究视角、问题定义、选择/返工决策、文风或认知提示。除工程证据外还需真实作品比较、失败回归、作者判断和独立读者。当前控制器直接 HOLD 此类自动晋升，不能把 AI 评分、JSON PASS 或一个 owner comment 当成这些证据。

工程发布的不可变记录列出全部 runtime 文件及 SHA、真实 implementation commit、规范与父协议身份和回退提交。代码先提交，再在后续提交中原子更新发布记录和 CURRENT，避免自引用 commit/hash。正式激活必须使用 MERGE 合并保留 implementation_commit 祖先；SQUASH/REBASE 会破坏此身份，不能用于此发布链。

## 单人所有者授权与 CI

仓库目标规则为 main 禁删/禁强推、strict 最新基线、两项必需 Checks（Actions app 15368）：

- `activation-and-runtime-regressions`：对所有 main PR 报告，不用路径过滤使其他 PR 悬空；涵盖 release、guard、packager、E18/E23 工程回归。
- `owner-release-authorization`：由 main 的可信控制器根据真实 API 身份、实际 CI、精确 head 与发布差异生成。新 head 不能继承旧授权。

单人仓库不伪造另一位 reviewer；计划将批准人数调整为 0，以第二项必需检查承担可追踪发布授权。所有者命令第一行：

```text
/deepwrite authorize ENGINEERING_PATCH <完整40位PR-head-SHA> governance
```

`governance` 仅在本次明确授权治理控制代码变更时使用。授权是所有者发布决定，不是独立审稿。`/deepwrite revoke <完整head-SHA>` 撤销。新提交、失败 CI、撤销授权或身份冲突使发布 HOLD。控制器只运行 main 的代码，候选只作为数据检查；它不在高权限 job 中运行候选代码。批准后自动进入 auto-merge，main 合并后的新宿主重读 CURRENT 并实际调用已发布身份。

GitHub 对同一 Actions App 的状态名无法证明运行的是某段特定代码；拥有仓库 write 的恶意主体仍属信任边界。这里不宣称替代独立安全审批。控制器主线、精确授权与公开证据用于避免误发布；质量判断也不能由该脚本证明。

## 首次安装及回退

当前管理 API 写入实际返回 403，auto-merge 为 false，规则仍要求一人批准且无具体 required checks。尚未安装的 main 控制器不能替自己完成首次安装。必须取得该仓库 Administration 写权限，按已归档请求修改并回读设置；首次 bootstrap 授权要绑定完整 head，不能把一次口头授权扩大为未来任意认知发布。此阻断保留在 STATE，不伪造已部署。

每轮结束保存实际命令、commit、CI/check ID、授权评论、CURRENT/record SHA、全新调用、恢复回执。回退是新的授权 PR：恢复旧 CURRENT 及其匹配 runtime，保留失败候选和所有私有书稿；合并后再次读 main 并调用原版本。仅临时 Git fixture 的故障/恢复演练不等于正式 main 发布回退。
