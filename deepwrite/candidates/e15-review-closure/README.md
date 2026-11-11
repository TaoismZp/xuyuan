# DeepWrite E15：跨版本审查结论必须约束返工（候选）

**状态：CANDIDATE / NOT_ACTIVE / NOT_QUALITY_PROVEN**  
**研究起点：** 2026-11-11 的一次私有真实整书 E12→E13→E14→E15 回顾。公开文件只包含脱敏机制和合成测试，不包含未发表书稿、私人审稿原文、具体哈希或私人谈话。

## 为什么做

已观察到的故障不是“AI根本没看到问题”，而是 **REVIEW_FINDINGS_RECORDED_BUT_NOT_GOVERNING_REVISION**：审稿曾报告严重跨章重复，但完整书稿、PDF和内部QA的工程完成感没有触发同一轮的实际修改。后来用户要求跨A/B/旧版原文对照和自我评分，才出现定位返工；数值评分不是已验证的必要原因，不能因此引进“每本书都让AI打72分”之类的新机制。

此候选只落实 DeepWrite v0.1 已有 **G3（独占能力）/G4（第二次发现）/G6（整书连续性）/G7（交付身份）**，不加新默认Gate、不改`deepwrite/CURRENT.json`、不改`wish-delivery/CURRENT.json`。

## 必须改变的行为

1. **写前：** 每章定义自己的 `unique_capability`、与序言相比新增加的读者判断、预期对照章节、原素材证据以及目标领域的独立机制。
2. **写中：** 每3—5章，以**实际冻结正文**对比初版和关键代表样章，不只把标题、简介或自评当对照。检查语义重复、复制粘贴、论证顺序和案例可互换性；允许合理复用旧文字，不能把高复用率直接判为差稿。
3. **写后：** 每个实际审稿负面条目留 `id / severity / location / issue / status`；严重条目改后必须有 `revised_sha256` 与 `recheck_evidence`，需要覆盖到当前候选全文；没修的高严重级别问题阻止“书稿已全面通过”的状态。对可暂缓的重大问题，只有作者真实确认风险后才可申报豁免（记录中的 `authority` 字段**不是**身份认证）。
4. **两本账：** `PASS_STRUCTURAL_ONLY` 表示已登记重大问题结构性闭环，不是文学验收、独立读者验收或事实审核PASS。AI自评可保留为编辑笔记，但不得代替实际修改、第二读者或作者验收。

## 可执行原型

`review_closure_guard.py` 是仅用 Python 标准库运行的 **G6关闭前置检查器**。输入 UTF-8 JSON：

```json
{
  "schema": "deepwrite/review-closeout/v0",
  "baseline_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "candidate_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "comparison": {
    "baseline_read": true,
    "candidate_read": true,
    "reviewed_units": ["chapter-1", "chapter-2"],
    "comparison_rationale": "Compared actual paragraphs and unique decisions"
  },
  "findings": [
    {
      "id": "F-01",
      "severity": "MAJOR",
      "status": "CLOSED",
      "location": "chapter-2 paragraph-4",
      "issue": "chapter-1 decision duplicated",
      "revised_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "recheck_evidence": "Verified changed text plus reverse reading of chapter-1"
    }
  ]
}
```

Run:

```bash
python3 review_closure_guard.py closeout.json
python3 -m unittest discover -p 'test_*.py' -v
```

`HOLD` exits with code `2`; `PASS_STRUCTURAL_ONLY` exits `0`. The preflight is useful only if the actual DeepWrite runner **honors nonzero exits** and blocks advancement to final quality status. Merely writing the guard or JSON is not engine integration.

## 已验证与未验证

- `PASS_ENGINEERING_LOCAL`: 11个合成场景的本地 `unittest`，包括已知重大缺陷OPEN却宣布成稿、没有修后证据的伪关闭、过期SHA、缺少实际版本对照、重复ID、Critical豁免等。
- `NOT_TESTED_IN_RUNNER`: 没有证明当前DeepWrite自动执行此检查、阻断流水线、返工后恢复；正式版v0.1没有因此升级。
- `UNVERIFIED_QUALITY`: AI可能不报告自己漏检的缺陷，伪造已读/证据字段；填写合格不等于读者觉得好。模型打分、同模型多角色不等于独立盲评。
- `PENDING_REAL_WORLD_AB`: 下一本未见过的跨领域书用同素材和计算预算比较有无候选，观察实际修补、理解增量、读者价值和额外成本，不能只看检查表是否变长。

## 晋升条件

必须在新任务内部实现真实自动调用/状态阻断/返工闭环，并验证不增加无意义审稿。至少保留同输入基线/候选、原始审稿、文稿身份、真实修改差异、复核结果；再按`deepwrite/GUARDED_EVOLUTION.md`做跨题材、真实读者、作者签收和回滚验证。即使测试通过，也要作者决定是否更新正式`CURRENT.json`。

**所有私人书稿与来源材料保持在受限私有档案，严禁上传到本公开GitHub候选。**
