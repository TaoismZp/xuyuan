# 本体迭代恢复入口

PROJECT_ID: `deepwrite-method-quality-20261109`。任务为改进公开工作台，不是撰写新书。

先读本目录 STATE.json、VISION.md、BLUEPRINT.md，再读监督和验收记录（存在时）。对照实际 Git commit 和证据清单，不根据本页推断测试已通过。按 STATE 的 `next_executable_action` 执行。

生效版本仍应从两份 CURRENT.json 读取。候选 v0.2 仅供本次开发试验；独立人类盲评和作者终审不能由模型代签。

没有私人原稿。可公开检查点只包含通用方法与合成测试；后续如加入真实书稿，必须另行核实私有持久存储，不写本目录。

## 已保存检查点

候选与20项固定证据：commit `5a34327b36c9bbf822a43942cdadc275592c924e`，GitHub回读24个文件逐字节匹配。草稿PR：https://github.com/TaoismZp/xuyuan/pull/12 。STATE的COMPLETED仅指本轮候选方法与兼容补丁已交审，不指质量终审或E1/E2通过。控制元数据更新提交会晚于候选commit；恢复时以STATE所列候选与ARTIFACTS身份为准。

唯一下一步见STATE：先读取PR和实际评审反馈；质量比较仍需预登记和真实读者，不把本轮缺陷注入演示当独立盲评。
