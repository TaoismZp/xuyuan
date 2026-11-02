# FIN·TYPE｜金融决策人格实验

FIN·TYPE 现在已经从“金融版 MBTI 问卷”升级为一局可玩的金融决策模拟器。

## 直接试玩

- 推荐入口：https://html-preview.github.io/?url=https://github.com/TaoismZp/xuyuan/blob/main/index.html
- 备用入口：https://htmlpreview.github.io/?https://github.com/TaoismZp/xuyuan/blob/main/index.html
- 直出候选：https://raw.githack.com/TaoismZp/xuyuan/main/index.html

## 当前版本

- 初始资金：100 万虚拟资金
- 6 幕市场环境
- 18 次关键决策
- 每次选择都会影响模拟净值 / 现金 / 压力 / 回撤
- 4 条金融决策轴
- 16 种金融人格
- 终局压力题 / tie-break 机制
- 结果页包含：人格代码、优势、结构性盲点、Kill Zone、账户路径复盘、反向训练
- 支持重新开局与断点状态

> 注意：模拟收益只用于制造路径压力，不代表“赚得多的人格更好”。人格判定来自决策结构，而不是最终收益。

## 自动回归

仓库已加入 GitHub Actions 浏览器回归：每次更新会自动启动静态站，并用真实浏览器走完“开始 → 18 次决策 → 6 幕切换 → 结果页 → 重新开局”。

当前最新回归：PASS。

## 源码

`index.html` + `styles.css` + `data.js` + `app.js`

GitHub Pages 仍需仓库首次手工启用，所以当前先使用无需额外配置的公开预览入口。
