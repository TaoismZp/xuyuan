# 调用 DeepWrite

作者可以直接说：

> 调用 DeepWrite，写一本关于【主题】、给【读者】读的书。资料在【授权私有位置】。我希望一次授权完成整书候选／先写样章给我审。

执行者负责选择适用功能、研究、架构、写作、审稿和返工；作者不必指定版本、模块名、章节数或逐章回复“继续”。

## 先确定真实版本与执行能力

1. 读取 GitHub **main** 的 [CURRENT.json](CURRENT.json)、[父协议 CURRENT](../wish-delivery/CURRENT.json)及其指向的实际规范。用新的检出或隔离工作树核对远端提交，保留现有修改。
2. 在真实 Git/Python 环境运行发行解析器；它核验发行记录、实现提交祖先和全部声明文件，再启动 `CURRENT.active_engine`。历史候选登记、旧恢复记录和聊天记忆不能覆盖 CURRENT。
3. 核实可用模型、有效来源、私有输出与持久化权限。普通 GPT 对话若只能阅读文件，不能宣称已执行 Python 引擎或会在对话结束后后台写书。

```bash
python3 -B deepwrite/release/activation.py --root . --run -- identity
```

## 新项目

执行者将作者已给的目标、读者、来源和授权冻结为私有请求，格式见 [DEFAULT_INVOCATION.md](DEFAULT_INVOCATION.md)。按 [PROJECT_INIT.md](PROJECT_INIT.md) 检查隐私和来源，然后运行：

```bash
python3 -B deepwrite/release/activation.py --root . --run -- \
    run /private/deepwrite-user-request.json /private/deepwrite-project
```

`run` 需要全新的私有项目目录；它会保存请求和来源原字节、研究配置与执行状态。样章先审采用 `ASSISTED_AUTHOR_GATED`，明确一次授权整书候选采用 `AUTONOMOUS_FULL_DRAFT`；两者不得互换。已有信息不重复询问，作者签收和公开发表仍需真实决定。

默认链为源领域学习与竞争解释→研究后架构→完整章节→读者/反方审稿→重大缺陷真实返工与重查→跨章和整书修订→装订与私有检查点。三层读者价值与知识复利贯穿此链，不是三段或六节模板。工程接线成功不能代替真实作品验收。

## 旧项目与中断恢复

先读取项目私有 `RECOVERY.md`、状态、原稿身份及版本锁，使用锁定版本的检出。正式更新不会静默升级旧项目，也不覆盖原稿。当前统一执行器的查询与恢复命令为：

```bash
python3 -B deepwrite/release/activation.py --root . --run -- \
    status /private/deepwrite-project
python3 -B deepwrite/release/activation.py --root . --run -- \
    resume /private/deepwrite-project --expected-state-sha256 <64-hex>
```

外部保存的 SHA 必须对应 `writer_project/run_state.json`；样章续写还需绑定该项目、合同及稿件 SHA 的真实作者回执。不要把“继续”当签收。更早的工程 runtime 使用不同命令，应从旧项目锁定版本恢复，不能把 `init/assemble/checkpoint/restore` 当作当前统一入口的子命令。

## 研发与验收

- 当前工程恢复入口：[RECOVERY.md](RECOVERY.md)；实际发布状态及唯一下一步：[release/STATE.json](release/STATE.json)。
- 写作质量：E1 真实模型整书、E2 公平完整作品对照、三层真人读者收益及黑箱质量继续按证据分别记录；没有证据就是未验证。
- 联合研发：[AGENT_COLLABORATION.md](AGENT_COLLABORATION.md)。桥接消息保留历史，先读取实际最新桥 STATE；不要重做旧消息指定的初始轮次。
