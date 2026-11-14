# 2026-11-12｜正式激活任务实读盘点

这是本轮开始时的事实快照。后续结果以 ../../STATE.json、实际 main 和不可变发布记录为准；工程测试通过不等于正式发布或作品质量提升。

## 固定身份与复用

|对象|实读提交|结论|
|---|---|---|
|main|6b81a45d8576aa0636d29950f9a2d86f2a5cf8b1|DeepWrite CURRENT v0.1；父规范 v7.6；无正式自主写书 runner|
|PR12|e5a1c9f0b057f5483022bd196a53790e905b0896|开放草稿；安全装订器、研究/编辑候选与历史档案|
|PR13|d7dadf80aaef3963d0784787219e2b5e6e12b59f|开放草稿；旧关闭守门器不应覆盖修复版|
|PR14|d2ef373c5e0dcb7736c56a00e0aefb32d63b0b1a|开放且已非Draft，标题仍带Draft；E18/E23/E24未合并、未激活|

实际运行git merge-base与merge-tree：main+PR14可干净合并；PR14+PR12冲突deepwrite/RECOVERY.md；PR14+PR13冲突guard、测试、README三文件。不能把三个PR按编号整包合入。

PR14 packager与PR12同blob cc5654d3a2ee112b3bd640dc1f64a8021ddb95ea；RESEARCH_LOOP、EDITORIAL_LOOP、v0.2候选说明也逐blob相同。PR14修复guard blob 1ef044813e856d8990986ae2d757abb8d95411dd替代PR13旧a086c03a24730df79343763523cca8d3f7a4c8b9。

## 已有测试原样取用

PR14原先遗漏PR12的15项装订器回归，本轮恢复既有测试，不重复开发：

- 路径：deepwrite/tests/test_packager.py
- 来源commit：e5a1c9f0b057f5483022bd196a53790e905b0896
- 来源Git blob：4f04fe618c0d08b33460c2c578b3db1f2e2e4f6a
- SHA256：5e56fb7d850f64cb51eaf1d77be9cf819c7f451a25f516f6df5f94651a380013；10810 bytes。
- 用git show COMMIT:PATH取原始字节并回比完全相同；实际python3 -B deepwrite/tests/test_packager.py，15项成功。

在/workspace/deepwrite-release对PR14源码实际跑release15、guard42、E23 17、runner27项unittest，全部成功。均为工程样例，不是计量真实模型、真人盲评或成书质量证据。

GitHub API回读同一PR14提交：activation-and-runtime-regressions，App ID15368，PR事件run43042185352/job130596608896和push事件run43042177261/job130596578065均completed/success。

历史activation工作流带deepwrite/**路径过滤；若作为全main必需检查，其他PR可能永久等待。该job当时未直接运行guard42或packager15；另两个对应工作流只响应实验分支push。本轮需修执行覆盖，不新增同义质量门。

## 实际配置阻断

2026-11-12环境已连接，gh API读取repo permissions.admin=true；这不代表当前令牌具备Administration写权限。root执行GET branches/main/protection、PATCH repos/TaoismZp/xuyuan（allow_auto_merge=true）均403 Resource not accessible by integration。

已实读本轮RULESET_WRITE_RESULT.json：2026-11-12T00:18:02.730649+00:00，对repos/TaoismZp/xuyuan/rulesets/27040989执行PUT，exit1、HTTP403、Resource not accessible by integration。请求拟保留review1并添加activation-and-runtime-regressions/App15368，未宣称生效。任务开始时规则回读为active/default main/no bypass，required checks为空。最终配置必须再次API回读。

## 发布边界与最小增量

身份、恢复、日志、安全装订与发布解析属于可复用工程能力。E24仍需绑定真实commit、依赖与发布记录，并以认证GitHub身份核授权，JSON字段不能冒充审批。

E23明确只允许SHADOW，会修改下游wish和材料，尚未质量通过。E18当前还读取候选RESEARCH_LOOP/EDITORIAL_LOOP为模型提示；正式默认启用它们属于认知行为变化，不能只靠工程CI晋升。正式工程引擎应固定正式规则，将未验收认知候选隔离。

本轮未读取/公开私人书稿，未修改CURRENT或原协作桥STATE。唯一下一步由root完成授权、正式入口及失败/恢复链真实验证，并保留实际权限阻断。
