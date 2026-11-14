# DeepWrite v0.2-canary.1｜跨对话恢复入口（脱敏工程项目）

**任务**：审视DeepWrite全演化并将有效成果连接真实写作器；不要用“作者认可某章80分”冒充工作台正式v0.4，也不能把旧私人稿件写公开仓库。

## 真实版本身份

2026-11-14主线 `main` commit `6b81a45d8576aa0636d29950f9a2d86f2a5cf8b1`，官方 `deepwrite/CURRENT.json` active **v0.1**，无active engine。父规范 v7.6。正式升级**尚未发布**。

本次工程试用命名 **v0.2-canary.1**，仅指 PR #18 分支内的候选 E18+E23+源领域优先+知识复利连线，不是官方`CURRENT`。依赖的PR#14仍未合并；PR#15禁止合并；PR#17独立洞见实验保持隔离未验证，不得宣称已整合。

- [PR #18](https://github.com/TaoismZp/xuyuan/pull/18)，branch `deepwrite/integration-source-first-kc-20261114`
- [全部演化审计及真实调用链](../../research/EVOLUTION_CALLCHAIN_AUDIT_20261114.md)
- [可试用操作说明及最小 config 片段](README.md)
- [Canary Registry](CANARY_REGISTRY.json)
- [机器状态](STATE.json)
- 固定可核代码/CI提交：`7960364511bb003337a0257fed975bda42df0611`。
- 当前试运行全部工程门清单： release 73、E15 guard 42、packager 15、E23 reader 55、source-first 11、E18 writer 51，**共247项**。真实GitHub Actions [run #43558917115](https://github.com/TaoismZp/xuyuan/actions/runs/43558917115) 与[run #43559004405](https://github.com/TaoismZp/xuyuan/actions/runs/43559004405) SUCCESS；注意这里的writer使用 scripted mock，不是接入真实OpenAI/Codex写书。
- 两次真正红CI回归保留为失败历史，已修复，不能只报最后绿而抹去故障。

## 主要工程变化

- `source_first_gate.py`：模型在真正写正文之前必须先看到 SHA绑定的源研究、原文引文、反常识/反方解释、至少两个竞争性研究方向与选择依据，以及源概念→章节问题的**独立映射**；不是自动把每篇课程做一章。
- `writing_loop_experimental.py` 实际加载并运行这个可选门禁，保存实际来源/模块receipt；未明确选择时旧模块行为保持。STABLE未发布时拒绝把新module偷塞正式调用。
- `reader_source_gate.py` 新增 `knowledge_compounding_probe`，要求对真实正文定位，指出另一新情景如何使用已教概念与失效边界；缺少/UNVERIFIED阻断下游写稿候选，不把机器评价当作新手、熟手、专家真正学会。
- GitHub Actions确实运行全部新增unit和已有E15/E23/E18/Release/Packager回归。

## 当前Open Gate

1. **CHAPTER_TOPOLOGY_AUTONOMY：NOT_IMPLEMENTED**。E18最初仍需config已有chapters；本次只使其必须有独立研究证据，动态自动生成目录和调整章数尚未打通。不可因资料源课有23讲就预定23章。
2. **REAL_PROVIDER/BLACKBOX_E1：NOT_RUN**。无本次可核真实已授权模型调用，PR14之前实际探针401；无需虚报ChatGPT有后台daemon。
3. **CONTENT_QUALITY/THREE_READER/KNOWLEDGE_COMPOUNDING：UNVERIFIED**。结构化模型probe不等于真实人类阅读收益；原生成作品的数学正确也不等于思想质量。
4. **PROMOTION：BLOCKED**。GitHub ruleset `27040989` main需1个审查，required checks仍空，auto-merge=false，管理API之前403。PR14/PR18均未合并，不能改官方CURRENT并谎称正式激活。
5. **PRIVATE_SOURCE/BOOK**：保留私有仓库，不因升级自动修改或曝光已写的《NO FOLD》/《孙子兵法》/《概率论》。
6. **INDEPENDENT_ORIGIN_PR17**：独立方向候选不等于已产生任何真正独立的新视角，尚未整合，本次也不声称它正式生效。

## PASS/PENDING/UNVERIFIED

- PASS：公开实际GitHub main、PR、history、规则集、候选源码与工程Actions日志已检索；新源码、审稿门和CLI说明已写入PR18，247项工程fixture曾在最新代码执行成功。
- PENDING：当前RECOVERY和STATE最终远端重新读取、PR审稿/合并、实际用新题材进行provider写作。
- UNVERIFIED：高质量自动整书、真实读者知识复利、跨学科稳定超越旧版本/逐章。

## 唯一下一步

在有适当权限/费用和安全保密条件的独立执行环境中，以**全新未设计过的私有题材**、冻结素材和作者授权运行PR18可选真实provider，比较同预算旧版、作者/独立读者检查迁移题；失败保留原版。之后由有管理与审批权限的Owner/Codex按PR14→PR18顺序处理有证据的正式工程发布/质量门/仓库规则；完成正式发布后读取main CURRENT +真实runner确认才可说DeepWrite不再是正式v0.1。不得直接推主线、伪造review或把候选标ACTIVE。

**重要提醒**：不需作者重述聊天历史。下次先读本RECOVERY/STATE、PR18 head、main CURRENT 和真实CI；版本回退与已写稿件均保持可恢复。
