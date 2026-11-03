# 许愿式交付｜Wish Delivery

当前版本：**v7.6**

当前规范：[`versions/v7.6.md`](./versions/v7.6.md)

历史变更：[`CHANGELOG.md`](./CHANGELOG.md)

项目模板：[`templates/`](./templates/)

## 版本管理规则

从 v7.1 起，每一次对“许愿式交付”本身的实质迭代，都必须：

1. 在 `versions/` 新建一个不可变版本文件；
2. 不覆盖旧版本；
3. 更新本文件的当前版本指针；
4. 更新 `CHANGELOG.md`；
5. 真实失败样本必须写入对应版本，成为永久回归测试；
6. 只有 GitHub 提交完成，才算系统迭代真正落地。

## 当前定义

**成熟愿望 → 效果图 → 施工图 → 按图施工 → 独立监理 → 验收 → 交付**

用户负责提出成熟目标与必要边界；系统负责把模糊质量要求编译成可感知的目标 Artifact，主动搜索并实证 Skill/方法能力，选择足以承载目标表面的技术路线，然后完成构建、失败恢复、返工、同表面验证、质量回归与最终交付。

v7.6 在 v7.5 的 Binding Chain Gate 上增加 **Execution Continuity & Liveness Watchdog**：聊天结束、请求超时、单个工具/CI 失败只能把任务标记为 INTERRUPTED/BLOCKED，不能隐式终止；长任务必须保存 Durable Task State（最后可靠 checkpoint、当前 Gate、真实 blocker、下一可执行动作），用户下一次回到同一项目时必须先恢复再继续。同时新增 **Monitor Must Be Simpler Than Product**：监理不能自己演化成比产品更复杂的工程瓶颈。