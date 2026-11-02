# FIN·TYPE｜金融决策人格实验

FIN·TYPE 是一个移动端优先的金融决策人格实验：不是问“你喜欢什么”，而是把用户放进有资源约束、机会成本、回撤、噪音和规则失语的金融困境里，看压力出现时真正怎么选。

## 直接试玩

- 推荐入口：https://html-preview.github.io/?url=https://github.com/TaoismZp/xuyuan/blob/main/index.html
- 备用入口：https://htmlpreview.github.io/?https://github.com/TaoismZp/xuyuan/blob/main/index.html

## 当前版本

- 10 个金融决策困境
- 5 幕市场环境
- 每题 4 个均有合理性与代价的 forced-choice 选项
- 4 条金融决策轴，每轴被 5 个跨情境题目覆盖，避免平分
- 16 种 FIN·TYPE
- 模拟账户净值 / 现金 / 压力 / 最大回撤只制造路径压力，不参与人格优劣评分
- 每手选择后有独立结算页，避免“表单式连续点题”
- 结果页包含：人格代码、最稳定决策轴、最摇摆轴、Natural Edge、Kill Zone、最后一手暴露项、分享与重测
- 移动端真实入口自动回归

> FIN·TYPE 是金融决策人格实验，不是经验证的心理测量诊断，也不构成投资建议。

## 题目设计原则

当前题库不采用“你是否喜欢冒险”这类自我描述题，而采用情境决策题：

1. 每个选项都必须说得通，同时都要付代价；
2. 避免明显“更理性 / 更专业 / 更安全”的社会期许答案；
3. 同一条轴必须跨上涨、回撤、拥挤、机会成本、政策冲击等不同环境重复测量；
4. 优先测行为取舍，不测金融知识；
5. 结果反映相对决策风格，而不是投资能力评分。

## 自动回归

GitHub Actions 会在每次更新后：

- 验证 16 型代码空间；
- 在 390×844 移动端视口从真实页面跑完整 10 题 / 5 幕 / 结算 / 结果 / 重测；
- 检查横向溢出与浏览器错误；
- 同时跑 localhost 与公开 HTML Preview 入口；
- 保存首页、答题页、结果页截图作为视觉 QA 证据。

## 许愿式交付

“许愿式交付”作为独立、可版本化的系统规范存于本仓库：

- 当前规范：[`wish-delivery/README.md`](./wish-delivery/README.md)
- 版本历史：[`wish-delivery/CHANGELOG.md`](./wish-delivery/CHANGELOG.md)
- 当前不可变版本：[`wish-delivery/versions/v7.5.md`](./wish-delivery/versions/v7.5.md)
- 建房式交付模板：[`wish-delivery/templates/`](./wish-delivery/templates/)

从 v7.1 起，每一次对“许愿式交付”的实质迭代都必须写入新的不可变版本并提交 GitHub，旧版本不覆盖。

当前 v7.5 强制采用：**效果图 → 施工图 → 按图施工 → 独立监理 → 验收 → 交付**，并增加 Binding Chain Gate：效果图、唯一有效施工图、候选构建、监理证据与最终公网构建必须绑定到同一可追溯身份链。复杂项目必须真实存在 Vision Fixture、Build Blueprint、Supervision Report、Acceptance Report 四件套；Reference 只能作为裁判，禁止混入成品制造 Fake Convergence。

## 源码

当前主产品为单文件 `index.html`；历史拆分文件保留用于回溯。