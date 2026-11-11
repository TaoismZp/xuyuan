# DeepWrite 候选方法｜跨章整书质量闭环与源头治理（2026-11-11）

状态：**CANDIDATE_SHADOW_ONLY / NOT_ACTIVATED / NOT_QUALITY_PROVEN**。本文件是对实际十三章写作和整书自审的脱敏工程复盘，供ChatGPT×Codex评估与试用，不自动修改 \`deepwrite/CURRENT.json\` 的 v0.1，也不替代当前已生效的八道质量门。不可把未发表正文、作者私密原话、内部项目文件/Hash、评审分数放在本公开仓库。本模块不给“因果改善已被证实”的承诺。

## 已存在的规则与新增执行差额

有效v0.1已规定源领域原生知识地图、章节独占、第二次发现、每3—5章跨章碰撞与整书验收；真实失败并非“没有写规则”，而是**规则未阻断生产**：章节局部看起来不错，仍可能违反源材料最重要的反常识；大量章逐篇产出、README或审核单标为“检查过”，不代表整书结构质量提高。

本候选新增的不是再做一份打分表，而是3个可拒绝继续生产的 **artifact transformations**：

1. **Source-to-Thesis Rebind**：原始材料读取之后，写出 \`source_surprising_claim\`、\`forbidden_surface_transfer\`、\`target_domain_causal_chain\`、\`counterexample\`、\`what_author_may_lose_if_ignored\`。用原文独有的决策结构去支配章节开头、转折、推导和下结论；“在原稿某段加古典引文”不算修复。反问：如果拿掉原典名称，本章是否仍可由目标域的现金流、期限、对手方、信息与权利义务独立推导？然后反问：如果换一个原典篇目，本章的因果链是否仍然成立？如果都成立，可能是通用金融文章而非源头治理。
2. **Bookwide Collision → Mandatory Derivative**：任何全书审稿不许只写“问题已发现”就继续包装。实际标记最严重的\`source_not_governing\` / \`duplicate_lesson\` / \`two_endings\` / \`appendix_old_binding\`，提出对照原稿的具体“删、换、合、保留”区间；产出 **原文只读 + 派生章/序尾/附录 + 重新合订本 + 不可变差异记录**；如果本轮无法修稿，则状态 \`PENDING_REPAIR\`，不允许 \`FULL_BOOK_READY\`。
3. **Proof-bound Book Snapshot**：每章原始blob、派生blob、章顺序、序尾和附录绑定到同一个 \`BOOK_CANDIDATE\`，合订本反向核查来源、版本和完整性。工具只可签发\`BYTE_ASSEMBLY_PASS\`，不能把自评、跨章比对、作者方向认可自动升级为\`LITERARY_PASS\`。

## 真实过程观察 → 通用故障 → 最小修复

| 实际观察（脱敏） | 可复现故障 | 新增动作及不应声称的能力 |
|---|---|---|
| 十余章逐篇“完整”，累加以后仍发现母命题没控制某一核心章 | SOURCE_INGESTED_BUT_NOT_GOVERNING；模型可准确复述源思想却沿自己熟悉的市场案例跑偏 | 对最严重一章执行源文段落逐项绑定 + 完整派生重写 + 原文比较；不是全局修复已证实 |
| 不同章都讲期限、流动性、被迫交易，字面没有相同句子 | SEMANTIC_COLLISION；字符串去重对主题重叠零检出 | 逐章列 \`unique_decision_object\` 与 \`must_not_repeat\`，并从相邻章节剔除重复机制；作者审读仍必要 |
| 终章和尾声两次全书回顾 | DOUBLE_ENDING | 序言只立母命题、终章交付最终能力、尾声提供不能被终章替代的新问题 |
| 附录来自旧版，正文更新后附录没换 | APPENDIX_BINDING_STALE | 每次章节替换后按章节专属决策重新生成附录映射并核对source_sha |
| 12/13章外显“第二次发现”，高度同一种假设型开头 | NARRATIVE_TEMPLATE_OVERFITTING | “第二发现”仍作内部门槛，外在叙述节奏由读者需要而异，不能通过删术语伪装深度 |
| 全书存成Markdown，却不能保证前台长文完整显示 | DISPLAY_INCOMPLETE_IS_NOT_STORAGE_LOSS | 保留私有完整 Markdown 可读入口、精确blob，报告显示问题与存储状态分离，默认聊天展示与下载/阅读入口两个验证表面 |
| 几轮实际修改混用旧附件与新版正文 | VERSION_MIX | 每次生成full-book artifact必须有每章blob清单和生成时间，发现来源冲突立刻禁止“终稿” |

## 操作合同（从整书审稿到真实修复）

A. **复原**：读取双CURRENT的实际生效版本、私有RECOVERY/STATE、冻结原稿、十三章来源blob及原始知识源；不可依赖聊天摘要把此前“方向可以”升级为质量PASS。

B. **建立书的因果地图**：各章各回答一个真正不同的目标域决策问题（非换个原典名），明确章节依赖、反例、不可替代的结果。核对原典最反常识的机制有没有真正改变该章结构，而非引文贴片。

C. **定义改动单**：每个发现固定 \`issue_id, severity, original_blob, source_locator, unique_decision_object, current_failure_evidence, correction_operation, check_before, check_after, still_open\`。内容改动先重写全章的 governing argument，再微调措辞；若没有新增发现，删减即可，不制造新例子充页数。

D. **逐项返工**：最先修 **A类源头错用**；继而修与相邻章节的语义边界；再修双结尾和附录错版；再做事实/数字与风格；每个结点保留旧稿和独立新稿，记录真实修改和证据，独立回读；不只给计划。

E. **整书再连读**：对完整序言—章节—尾声—附录做第二次碰撞，确保新主张没有制造别的章节漂移。把“原章例子能换到另一章且毫无影响”视为编辑疑点，不自动认定FAIL；真正裁判是因果任务差异。注意故事案例属于虚构时明示、事实机制与规则需要真正核实。

F. **成品+验收**：私有完整阅读稿及精确 manifest 真实可取；读者实际可完整阅读（不仅首屏）；经作者/真正独立读者评价后才有质量等级，AI自审不得顶替。缺真实人工证据则状态 \`PENDING_AUTHOR_OR_READER\`。

## 代表测试而不是纸上新增门槛

最小测试：拿一章已有的源头偏航、一个与邻章语义冲突的段落，以及一份旧附录，冻结同一原稿；记录 **之前的完整原文→采用本模块的派生正文→旧流程同等成本的修订正文**。对比思想由来源统治、原生金融推理、重复改善、真实性、风格；在读者未比较以前只能\`IMPLEMENTED_CANDIDATE\`，不能说“更好”。

避免“外部自评模型”伪装独立盲审；AI同时做修稿和打分仅供自检。正式生效须走既有GUARDED_EVOLUTION证据门与作者批准，不能直接改变CURRENT。

## 给Codex的实施任务（待接力，不抢占现有桥接编号）

1. 在真实写书runner/审稿环节找到能够执行\`CROSS_CHAPTER_AUDIT\`后真正**阻断包装并触发返工**的调用点；没有runner则明确\`BLOCKED_NO_RUNNER\`而不是只加若干JSON字段。
2. 用脱敏的多章小样与冻结原稿复演“原典中做虚换做实却被写成泛化等待”“终章和尾声双重回顾”“附录旧版本”等故障；给出可核验文件diff。
3. 只有确实使修稿质量或使用者行为改善，才考虑合并进稳定工作台；不增加无效新Gates，原有G1/G3/G4/G6/G7完全保留。

## 版本与权限
- DeepWrite CURRENT：仍v0.1；许愿式交付 CURRENT：仍v7.6（以实际实时读取为准）。
- 本文公开仅用于通用方法，私人原稿、特定作者写作素材和私有Git历史均不复制。
- 本文若只获得GitHub文本读回：\`PUBLIC_METHOD_STORED_PASS\`、\`RUNNER_EXECUTION_UNVERIFIED\`、\`READER_GAIN_UNVERIFIED\`。
