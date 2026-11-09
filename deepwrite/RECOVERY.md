# 深写｜DeepWrite 工作台接班入口

## 当前真实身份

- GitHub public method repo: \`TaoismZp/xuyuan\` / \`deepwrite/\`。
- 工作台名称：**深写｜DeepWrite**。
- 当前版本：读取 [CURRENT.json](CURRENT.json)，不要从本页猜；初始v0.1。
- 上级《许愿式交付》：读取 \`../wish-delivery/CURRENT.json\` 实际生效规范。
- 状态：\`WORKBENCH_PROTOTYPE\`，不是 \`AUTONOMOUS_WRITER_PASS\`。
- 形成史：[HISTORY.md](HISTORY.md)（脱敏），隐私：[SECURITY.md](SECURITY.md)。
- 复用入口：[START_HERE.md](START_HERE.md)，项目初始化：[PROJECT_INIT.md](PROJECT_INIT.md)。
- 工具：[tools/book_packager_v0.1.py](tools/book_packager_v0.1.py) 和 [tests/test_packager.py](tests/test_packager.py)。

## 最近可靠检查点

公开仓库内文件提交、当前版本和已读取的SHA以 GitHub 真实返回为准。私人源项目原始稿和审稿不在这里，不得因缺少权限而猜测。

## 尚未关闭的门

- \`E1_AUTONOMOUS_FULL_BOOK: NOT_IMPLEMENTED\`
- \`E2_UNSEEN_TOPIC_BLIND_AB: PENDING\`
- \`PRIVATE_REPOSITORY_CREATION_TOOL: UNAVAILABLE_IN_THIS_CONNECTOR\`
- \`COLD_NEW_CHAT_BOOTSTRAP: PENDING_REAL_TEST\`
- \`HUMAN_QUALITY_VALIDATION: PENDING\`

## 唯一下一步

当前会话是工作台联合研发：读取 `discovery-gate/agent-bridge/STATE.json` 的实际 `last_message`、最新提交与 `next_action`，由所列下一位执行交叉审查。2026-11-09首轮诊断和工程增量见 `experiments/2026-11-09-system-review/REPORT.md`；候选字节恢复不等于E1/E2或私有持久恢复通过。不要执行本入口历史上已过时的下一步。

若任务是作者另行发起的真实写书项目，则从该项目自己的私有RECOVERY/STATE及固定双层版本恢复；新项目按 `START_HERE.md`、`PROJECT_INIT.md` 立项。E1、E2继续按 `EVALUATION.md` 保持未验收，不以本轮小样替代。

如果没有自动新建私有GitHub仓库的能力，**先在私有文件库完成新项目隔离与可恢复检查点，标注 GitHub 私有repo PENDING，绝不把新书原稿放进本公开目录**。下一次先从本页和项目STATE接班，不重复建新的无关项目。
