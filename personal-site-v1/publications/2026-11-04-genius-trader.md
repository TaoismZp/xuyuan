# 首篇真实文章发布登记 — 2026-11-04

- article_id: `A-20261022-GENIUS-001`
- title: 《天才交易员为何注定陨落》
- canonical source: `/作者第二大脑/01_成稿原文/天才交易员为何注定陨落_用户原稿_2026-10-22.md`
- canonical source SHA-256: `312cf1ebad852621edd72078d7cce2f653da6e5072f12e0199787e823e5e23b4`
- published source file: `personal-site-v1/content/posts/genius-trader.md`
- intended permalink: `/xuyuan/personal-site-v1/essays/genius-trader/`
- original line count: 265
- source scope: complete canonical text, no additions or substantive rewriting
- nonsemantic layout normalization: individual manuscript lines separated into Markdown paragraphs; four existing unmarked section titles represented as Markdown level-two headings: 乱反馈 / 天才的死法 / 遍历性 / 市场不在乎你
- text integrity validation: reverse normalization restores all 265 original manuscript lines exactly
- edition: original manuscript, publicly formatted derivative
- published date metadata: 2026-11-04
- publication channel: GitHub canonical Markdown → deterministic static builder → GitHub Pages
- verification: deployment and same-surface public acceptance must be checked against the resulting publication commit, not assumed here

本登记不改变原始文稿；发布版是派生文件，Git 提交历史保留变动。

## 第一轮公网证据

- 首次发文提交：`3ef03ed3455c22b7bafcf51d3a5a7ca440198e39`
- 首次真实内容部署：GitHub Actions `41678947550`，结论 PASS。
- 首次公网验收：GitHub Actions `41679087653`，结论 PASS；站点 HTTP 实测发现 1 篇已发布长文；WebKit 在三种尺寸验证了首页、文章列表和网站其他主页面。
- 补强验收：为文章详情页加入 iPhone / iPad / Desktop WebKit 直接打开、排版、正文完整性、首尾截图检查，并修正过时的“空站”验收报告语句。此轮验收必须重新绑定到新的 Delivery SHA，以独立运行记录为准。

## 首篇文章真实阅读页追加验收

- 文章特定 WebKit 首次完整验证：GitHub Actions `41680031506`，公网站点与 iPhone/iPad/desktop 首屏检查 PASS。
- 审阅验收附件时发现“末尾截图”与首屏像素完全相同，原因是滚动请求后立即截图，未等待 CSS 平滑滚动完成。此问题不影响文章正文或页面访问，但**末尾截图证据当时无效**。
- 后续监理改进：关闭测试页的平滑滚动、等待两帧布局、断言浏览器真实滚至文章底部才截图；最终合格证据以新增运行和 SHA 为准。
