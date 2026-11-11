# Perspective Inversion 候选模块｜本地工程验证记录

记录日期：2026-11-11；**实验性**；`deepwrite/CURRENT.json` 未修改，正式 DeepWrite `v0.1`。

## 被检验的实际代码身份
- `perspective_gate.py` Git blob `b021765b3231295fc818dcef6f05d631cb85c76a`
- `test_perspective_gate.py` Git blob `bbafd0273ba386805c43d195c88951c5159ef790`
- 由已上传仓库文件的**逐字相同本地副本**计算标准 Git blob SHA1，分别等于上述远端 blob SHA，不是只运行另一个相似脚本。

## 执行
`python -m unittest -v test_perspective_gate.py`：

- `test_duplicate_candidate_fails` — PASS
- `test_holds_even_when_structurally_complete` — PASS
- `test_missing_prior_baseline_fails` — PASS
- `test_not_enough_competitors_fails` — PASS
- `test_not_found_is_not_proof_of_novelty` — PASS
- `test_prior_covered_must_not_be_called_new` — PASS
- `test_tampered_hash_fails` — PASS
- `test_wrong_prior_quote_fails` — PASS
- `test_wrong_source_quote_fails` — PASS

结果：`Ran 9 tests in 0.011s; OK`，仅证明静态字段、文本身份和输出边界行为。**不能证明视角质量、新颖性或学术原创。**

## 私有真实负控制度
以一个已有完整历史版本的私有长文项目的两段实际精修正文为旧稿基线，完成 local CLI `perspective_gate.py` 实际运行。结构检查 PASS；旧稿已经拥有的两条“再次发现”被标 `REJECT_AS_NEW_DISCOVERY`；第三条需要人工跨章检查，仍 HOLD。输出明确 `quality_or_novelty_auto_pass=false`、`HOLD_PERSPECTIVE_ADJUDICATION_NO_BOOK_REWRITE`。

私有具体原文、局部反证、SHA、运行输入及输出位于受限项目档案，**不进入公共仓库**；此文件不能用来推测私人文件路径或展示私人稿件。

## 尚未完成
- 未接入生产 `CHAPTER_LOOP` 或真实自动审核/重写调用链；
- 未以陌生书题、隔离执行器和真人独立评阅证明质量改善；
- 不修改 `deepwrite/CURRENT.json` 或任何父协议；
- 结构门检测已标注的先前思想血缘，但无法自动发现所有被漏报的同义重复；
- 候选功能只有明确 `SHADOW / CANDIDATE_OPT_IN` 才能运行，不等于当前正式 DeepWrite 自动使用。

下一步工程任务：让生成阶段在写书前真正调用此门，并在旧稿/外部来源对照缺失时停止而非继续产出；用陌生新书进行受保护比较，再由作者决定是否批准升级。
