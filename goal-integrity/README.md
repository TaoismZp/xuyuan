# 防目标漂移｜候选结构性检查器（尚未生效）

本目录在 Draft PR #28。正式《许愿式交付》版本由 `wish-delivery/CURRENT.json` 决定；候选机制不自动修改正式版本。

## 当前迭代的边界

- 通过：目标锁、项目身份、当前用户指令ID、最权威checkpoint及blob、当前NEXT、主交付物的结构性核对；防止旧恢复索引覆盖用户新指令；支持性工作不得自称完成主任务。
- 失败即停：不确定的恢复来源、错误稿件SHA、目标版本不符、缺乏正文差异却宣称书稿质量提升、未验收却宣称人类认可。
- 只靠`goal_conflict:false`不再构成充分证据；`semantic_reviewed:true`仍是执行者声明，**不能证明语义无漂移**。必须由宿主从可信用户对话和实际Git对象独立采集上下文并人工/语义审查。
- 本仓库的十轮运行是**10次模拟输入**，不是十轮真实ChatGPT接班。单元测试PASS !=引擎已接线。不可将此机制描述为全局自动生效。

## 使用

`node --test goal-integrity/tests/gate.test.mjs`

真实接入所需：从GitHub/文件库读取可信来源生成`context.authoritative_checkpoint`，与最新可见用户指令绑定；在内容工作执行前及声称成果时调用`checkGoalIntegrity(lock,action,context)`；保留独立回读与用户验收。未接入前标`ENGINE_UNVERIFIED`。

## R23事件的真实修复条件

当旧Library指向R6、私有GitHub项目根恢复状态指向R23时，宿主必须使用可核验最新正文Blob作为权威checkpoint。不能在旧索引上运行审核，也不能把工具/审稿QA替代正文产物。此规则没有私有材料写入公开仓库。

## 仍待完成

CI检查的实时状态、真实DeepWrite调用链接入、完整10回合实测、独立监理、用户验收。公开仓库仅有脱敏模拟夹具。
