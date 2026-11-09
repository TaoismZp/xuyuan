# 可选候选：本地字节检查点 v0.1

**能真实使用：snapshot / verify / restore。证据仅限本地字节，不是写作质量保证。** 不安装新框架；Python标准库，Linux原子无覆盖发布依赖libc `renameat2`（Windows使用拒绝覆盖的rename）；能力缺失返回BLOCKED。使用当前正式DeepWrite v0.1和父协议v7.6，不修改二者CURRENT。其他版本兼容未测。

## 0004新增的有限恢复前检查（仍为显式自愿候选）

字节命令现在明确输出 `project_resume_gate=NOT_RUN`、`complete_project_recovery=UNVERIFIED`。如果项目事先冻结了必需文件、双层版本与候选选择，另运行只读 `qa/resume_check.py` 检查漏存和pins/config候选冲突；通过仅为 `PASS_DECLARED_RESUME_CHECKS_ONLY`。没有清单的旧快照仍可字节恢复，不能据此获得继续执行项目的验收。示例、F1/F2失败样本、正常STABLE/opt-in对照和停用办法见 [0004实测](../2026-11-09-resume-boundary/REPORT.md)。清单完备、声明真实性、全部配置正确和持久性仍未验证。

## 选择启用与依赖

新项目默认稳定流程。只有明确自愿试用时，在项目记录 `checkpoint_restore`、**包含 `deepwrite/qa/checkpoint.py` 的完整Git commit**、双层协议实际version/commit/spec blob SHA，以及 `EXPERIMENTAL_LOCAL_BYTES_ONLY`。不能以本说明的候选版本取代正式工作台。工具代码在公开仓；真实原稿、配置、pins、快照和恢复目录必须在授权私有存储。

先读取真实CURRENT及对应版本，把 `PROJECT_PIN_TEMPLATE.json` 的占位符解析为实际值；旧项目仍沿用自己已有pins，不能重新跟随最新CURRENT。工具校验 `project_id` 相同、两协议version非占位、commit/spec_sha的40位格式，**不验证Git对象存在、它曾经正式生效或作者授权**。本轮演练额外从固定commit真实导出两份规范并验证Git blob身份；日常项目也应归档这些字节。

配置JSON应明确模块开关与具体候选commit。快照强制包含作品、pins、配置；其他所有恢复所需文件（章节、研究来源、审稿、项目STATE、两规范正文等）用 `--file` 加入。工具不能知道文件清单是否完整，也不能替代质量审稿。先暂停本项目写入再快照；逐文件读取不是数据库式多文件事务。

## 三个命令

以下 `PRIVATE_*` 和 `MANIFEST_SHA` 是须由执行者替换的本地路径/值；不是已创建的私有存储。工具路径可由公开仓clone取得。

```bash
python3 deepwrite/qa/checkpoint.py snapshot PRIVATE_PROJECT PRIVATE_NEW_CHECKPOINT \
  --project-id PROJECT_ID --artifact book.md --pins pins.json --config modules.json \
  --file STATE.json --file protocols/deepwrite.md --file protocols/wish-delivery.md
```

返回 `manifest_sha256`；将它另存到项目受限恢复索引，不要恢复时从可被一起改写的manifest临时重算并当作已知身份。**身份锚和快照都必须有私有耐久备份。** 本地成功不等于上传/跨环境恢复成功。首次启用须在所选私有存储上传后下载回读校验；没有真实存储就记录阻断，不将私稿传入本公开库。

```bash
python3 deepwrite/qa/checkpoint.py verify PRIVATE_CHECKPOINT \
  --expected-manifest-sha256 MANIFEST_SHA
python3 deepwrite/qa/checkpoint.py restore PRIVATE_CHECKPOINT PRIVATE_NEW_RECOVERY \
  --expected-manifest-sha256 MANIFEST_SHA
```

先校验整个manifest与每个对象，再发布新恢复目录。已有目录、缺文件、哈希不符、穿越路径、符号链接都拒绝。恢复目录含 `RESTORE_RECEIPT.json`；`PASS_BYTES_ONLY`说明保存过的字节已恢复，原稿、试验分支和快照仍保留。工具不更新全局CURRENT，也不自动把恢复目录变成活动项目。

## 停用候选与继续生产

1. 质量出现明确损失时停用试验。选择**此前已经记录**的可靠checkpoint及外部manifest SHA；不要用当前坏稿新做的快照冒充旧基线。
2. 恢复到新目录，核对稿件、双层pins、原配置模块关闭状态、审稿是否仍绑定对应稿；在新的项目决定记录里写明损失理由、失败分支引用和恢复receipt。
3. 显式从恢复目录继续。恢复出的旧STATE只作为历史事实；当前时间/下一步/回退原因须形成新的工作状态，不把旧的ACTIVE或下一步不经核对直接执行。
4. 若仅停用此检查点工具，原稳定工作流程和已有快照保留；可在固定旧工具commit执行恢复。没有备份或校验失败时记 `BLOCKED_NO_VERIFIED_CHECKPOINT`，不覆盖任何现存版本。

尚未排除的风险：选择了质量较差的基线、漏存关键章节/外部资源、快照时并发编辑、伪造语义正确的pins、外部身份锚一起遗失、配置虽复原但外部服务未复原。工具不恢复未保存聊天、模型随机状态、网站线上部署/数据库/外部服务，也不证明还原的作者/读者评价真实。没有耐久跨机器私有恢复实测或整书质量对照，不称完整生产回滚已验收。

## 本轮可复跑证据

```bash
python3 -m unittest discover -s deepwrite/qa -p 'test_*.py' -v
python3 deepwrite/tests/test_packager.py
python3 -m unittest discover -s deepwrite/discovery-gate -p 'test_*.py' -v
python3 deepwrite/experiments/2026-11-09-system-review/replay_drill.py
```

最后一个命令只创建临时合成项目，退出时清理自己生成的材料；不触碰真实项目。分别恢复写作小稿和本地HTTP静态页：源删除后全部6文件相等、失败分支保留、模块配置回旧、两层实际规范和pins复原、篡改/覆盖被拒绝。HTTP仅验证恢复前后响应字节相同，不包含浏览器交互、线上URL、部署或用户体验验收。相邻 `ENGINEERING_RECEIPT.json` 是本轮真实运行结果。
