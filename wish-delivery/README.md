# 许愿式交付｜Wish Delivery

当前版本：**v7.3**

当前规范：[`versions/v7.3.md`](./versions/v7.3.md)

历史变更：[`CHANGELOG.md`](./CHANGELOG.md)

## 版本管理规则

从 v7.1 起，每一次对“许愿式交付”本身的实质迭代，都必须：

1. 在 `versions/` 新建一个不可变版本文件；
2. 不覆盖旧版本；
3. 更新本文件的当前版本指针；
4. 更新 `CHANGELOG.md`；
5. 真实失败样本必须写入对应版本，成为永久回归测试；
6. 只有 GitHub 提交完成，才算系统迭代真正落地。

## 当前定义

**Intent → Reference Fixture → Capability Proof → Silent Execution → Finished Reality**

用户负责提出成熟目标与必要边界；系统负责把模糊质量要求编译成可感知的目标 Artifact，主动搜索并实证 Skill/方法能力，选择足以承载目标表面的技术路线，然后完成构建、失败恢复、返工、同表面验证、质量回归与最终交付。

v7.3 新增：高主观质量任务优先形成并锁定 **Reference Fixture**；技术架构必须证明足以逼近该参考；Skill 不再允许“写进记录即算使用”，必须留下搜索、读取、筛选、实测和实际影响实现的证据；Final 前必须做同视角实机对比，明显像“两个时代的产品”则 Comparative Quality 自动 FAIL。