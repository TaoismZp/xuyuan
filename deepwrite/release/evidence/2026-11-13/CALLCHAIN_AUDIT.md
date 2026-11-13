# 实际入口与候选调用链

正式main仍是v0.1规范，无active_engine；不是已运行的自动写作器。逐节点正式/候选Git blob、SHA及工作树文件身份见CALLCHAIN_AUDIT.json。其中candidate_snapshot=fcdacc1保留工程修复前后对照；worktree与quality_execution_chain是本轮最终候选源码。

```mermaid
flowchart TD
  A[main CURRENT v0.1] --> X[无正式runner: STOP]
  B[候选 E23 prepare: canonical writer SHA] --> C[现有 E18 writer]
  C --> D[冻结项目 mode / 作者范围 / 读者合同]
  D --> E[DISCOVERY → SOURCE_LEARNING → EVIDENCE]
  E --> F[DRAFT → ADVERSARIAL_REVIEW]
  F --> G[有重大问题: 真正改正文 / 源学习返工]
  G --> H[RECHECK / E15 actual file guard]
  H --> I[跨章审查与返工]
  I --> J[前言和尾声]
  J --> K[FULL_BOOK_RECHECK: 全部部分]
  K --> L[历史问题重验 → 装订 → 检查点]
  D --> W[未批样章: AWAIT_AUTHOR_REVIEW]
  E --> Q[未解决: BLOCKED_QUALITY_UNRESOLVED]
  H --> Q
  K --> Q
```

KEEP允许正确正文无需改写。工程断言和定位模型意见不同；模型审稿也不等于作者或真人读者。当前固定正式入口拒绝运行候选，STABLE正向profile未执行；代码已准备真实identity/profile校验，尚待正式质量验收和作者发布决定。
