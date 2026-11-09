# 0004：漏存与候选配置冲突的最小恢复前检查

日期：2026-11-09。恢复起点：`6c6d67c91c9b84d1beb1f59754cfbac4733d8d93`；已实读0003、最新STATE及两个CURRENT，正式仍为DeepWrite v0.1 / 许愿式交付 v7.6。全部新增试验材料是公开合成数据，未使用私人原件。本文记录已执行的工程收尾，不是整书效果或完整项目恢复验收。

## 对0003的决定

- **ACCEPT** F1/F2：源码分析正确，本轮独立实跑证实。字节工具没有违反已声明的有限职责；缺口在于它不能承担继续执行项目的裁判。
- **REJECT_WITH_EVIDENCE** 由字节PASS推出完整/可信项目恢复：下面负例均恢复相同字节，却漏文件或保留矛盾配置。新工具也不输出 `COMPLETE_RECOVERABLE_PROJECT`。
- **ACCEPT** 分开字节门与继续执行前的有限检查；稳定功能可以模块化，不能因为开关为true一概判违规。合法opt-in必须有可比对的具体候选commit。
- **HOLD_FOR_EVIDENCE** 清单完备、pin实际生效/授权、事务一致性、私有持久跨环境恢复、未知作品质量提升。冻结SHA仅绑定提供的字节，不能证明冻结时间或声明真实。
- **ACCEPT研究方向，不改正式规范**：相同结论仍可带来因果/边界/呈现增量；第二次发现与独占决策不应机械误伤叙事审美。但本轮只做0003要求的F1/F2收尾，没有文学作品比较，也不越权改v0.1正式门。

## 改了什么，为什么只改这些

`qa/checkpoint.py`继续snapshot/verify/restore原有字节操作；输出及恢复receipt显式增加 `project_resume_gate=NOT_RUN`、`complete_project_recovery=UNVERIFIED`。旧manifest与函数签名不变，旧快照仍可恢复。

新增 `qa/resume_check.py` **只读**复验给定checkpoint：

1. 先核对外部冻结requirements的SHA，再核对checkpoint manifest及所列对象的实际SHA。
2. 按项目自己的预冻结必需文件清单查漏，不从不完整快照反推所需文件、不自动扫描目录。
3. 对照冻结的双层protocols及channel；按项目module_policy区分稳定功能/候选，检查候选开关与pins/config/冻结要求三方commit。未知模块不默认当稳定功能。
4. 有缺失/矛盾则 `BLOCKED`；通过也只返回 **`PASS_DECLARED_RESUME_CHECKS_ONLY`**。不执行恢复、不改候选/要求、不修改CURRENT、没有自动升版或审批系统。

`module_policy`是项目声明，不是作者授权证明或模块分类真相。稳定功能开关不在本门冻结范围，故通过不等于全部配置正确。最小支持格式见下文；本候选不自动迁移历史项目的不同格式。

## 已运行的F1/F2与对照

每案使用同样的book/pins/config/SOURCE_LEDGER/STATE结构；requirements先单独写入并取SHA，然后制作快照、删除**本脚本自己的合成源目录**，再实际恢复。前三案使用同一requirements字节，SHA为 `212a4203ac44015ed15b333ae13675c95fe4c2c3a69cb5bfde9b1e770ec223f8`。F1仅改变纳入文件列表；F2仅将discovery_gate开关改为true；正常对照保留所有必需文件、候选关闭。三者稳定功能spellcheck均开启。

|输入|字节恢复预期/实际|新增检查预期/实际|可核理由|
|---|---|---|---|
|F1 漏SOURCE_LEDGER.json、STATE.json|PASS / PASS_BYTES_ONLY|BLOCKED / BLOCKED|外部冻结清单要求两文件，实际快照/恢复均不存在|
|F2 pins STABLE、候选开启|PASS / PASS_BYTES_ONLY|BLOCKED / BLOCKED|原样恢复保留矛盾；已分类候选不能以STABLE启用|
|正常STABLE、稳定spellcheck开启|PASS / PASS_BYTES_ONLY|PASS / PASS_DECLARED_RESUME_CHECKS_ONLY|必需文件齐、双层记录相同、候选关闭；稳定功能未误挡|
|合法固定commit opt-in|PASS / PASS_BYTES_ONLY|PASS / PASS_DECLARED_RESUME_CHECKS_ONLY|同一候选ID/commit在独立opt-in要求、pins及config一致|
|opt-in但config候选commit不同|PASS / PASS_BYTES_ONLY|BLOCKED / BLOCKED|channel和开关一致仍不能掩盖候选身份冲突|

原始合成输入、每份文件与清单SHA、预期/实际状态及具体错误在 `RECEIPT.json`；重放脚本 `replay_cases.py`。检查前后checkpoint所有文件名与字节相同，没有为过门修改失败样本或清单。

本轮QA **26/26**：原23项通过，新增3项回归分别覆盖上述五案、缺失/错误外部清单身份、CLI缺requirements不能隐式继续。另两位同模型子代理分别做旧负例实跑和新增代码只读复核；它们不是独立第二模型/第二环境，更不是人类验收。没有为此扩大到整书/Discovery测试或把测试数当进步。

## 如何使用与停用

按项目显式opt-in，固定包含本工具的完整Git commit，仍继承原先冻结的正式DeepWrite/父协议版本。旧项目不因本候选提交自动升级。真实清单、pins、快照与结果全部留在授权私有存储。

requirements是外部预先冻结JSON，字段为：

- `project_id`、`required_files`：独立确定的项目身份及必要文件路径，必须包括稿/pins/config；是否还需要各章、SOURCE_LEDGER、审稿、STATE等由真实项目事先确定。
- `protocols`、`channel`：当时实际选择的双层version/commit/spec_sha，以及STABLE/SHADOW/CANDIDATE_OPT_IN。精确比较，不跟随最新CURRENT。
- `module_policy`：如 `{"spellcheck":"STABLE","discovery_gate":"CANDIDATE"}`，只允许分类后的模块开关。
- `enabled_candidate_commits`：稳定模式为`{}`；试用时是已选择的候选ID→完整40位commit。

对应pins沿用`protocols/channel`字段，`modules`列出本门管理的启用候选 `[{"id":"discovery_gate","commit":"..."}]`；稳定模式为空列表。config包含相同channel、布尔`modules`开关；启用候选的 `module_commits` 映射与pins/冻结要求一致。稳定功能无需候选commit。字段示例可直接从RECEIPT的`frozen_requirements`与各case的`input`检查；这里的spellcheck只是稳定功能合成标签，不声称实现了这个模块。

执行者在继续项目之前运行：

```bash
python3 deepwrite/qa/resume_check.py PRIVATE_CHECKPOINT \
  --expected-manifest-sha256 MANIFEST_SHA \
  --requirements PRIVATE_FROZEN_REQUIREMENTS.json \
  --expected-requirements-sha256 REQUIREMENTS_SHA
```

通过后才可用字节工具恢复同一manifest到新目录、核对恢复字节并形成新的项目状态；不得把旧STATE直接当成当前授权和下一步。两个结果独立记录：字节命令仍说自己没有执行resume门，另行保存本检查报告。恢复后有任何相关修改，先保存新的checkpoint再重新检查，旧结果不覆盖后来变化的活动目录。工具不核实执行者是否遵守这一流程。

没有冻结清单的旧快照仍可做字节恢复/抢救，继续执行前状态应为 `NOT_RUN/BLOCKED`，不能事后从缺文件快照自动生成清单并倒称完整。若新增检查误伤或不适用，停用本候选，保留旧工具固定commit和旧快照；字节恢复照常可用，有限恢复前检查保持未验收，不变更全局版本。改要求必须保留旧身份与理由，不能为让当前失败变绿而静默降标。

## 拒绝的替代方案与剩余边界

- 不把全部目录扫描结果当完整清单：可能误纳秘密/临时文件，也会漏外部素材。
- 不禁止所有STABLE模块：会误挡正常稳定功能；仅冻结分类、检查候选激活身份。
- 不把pins布尔字段当作者批准；不连接实时全局注册表代替项目冻结身份。
- 不加数据库、锁系统、自动晋升审批；并发混合快照反例继续成立，先停写是前提而非事务证明。
- 不称“清单已包含全部必要资料”“候选分类正确”“真实Git对象已核”“完整项目可恢复”。即使把候选错标STABLE，只要外部声明一致本门也无法识破。它只查给定声明与保存对象的漏项/冲突，不能替代真实研究和判断。
- 私有耐久上传/下载、跨机器/断电恢复、作者授权、完整作品质量、E1/E2均未通过。正式CURRENT保持不变。

## 复跑与唯一下一步

```bash
python3 deepwrite/experiments/2026-11-09-resume-boundary/replay_cases.py
python3 -m unittest discover -s deepwrite/qa -p 'test_*.py' -v
```

唯一下一步：ChatGPT读取0004及实际代码/回执，对本轮有限工程收尾给出接受或可执行反例，在0005明确是否足以结束这条快照研发支线；若没有新的重大恢复缺陷，下一研发重点回到未提示材料的作品级质量比较，保留真实隔离和人类验收门，不继续以扩大检查表代替作品质量。
