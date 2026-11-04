# 轻量发文入口 — Artifact / Delivery Contract

## 目标
让已经在 GitHub 登录的作者即使不额外申请 Access Token，也能从 iPhone 的一篇现有长文直接获得适合本网站的 Markdown，并进入 GitHub 的原生提交页面。

## 原型与成品边界
- 最终真实成品是公网 `/personal-site-v1/write/`，不是 PDF、说明书或截图。
- 本站页面可以 **整理/预览/复制/导出**；真正的 GitHub 登录和最终 Commit 仍需站长操作。
- 原有 Sveltia CMS 路径完整保留；这是一条更少权限前置步骤的备选路径，不偷偷替换后台。
- 用户不得误认为 `draft` 在公开 GitHub 仓库具有私密性；本工具仅生成 `status: published`，不在公开仓库自动存储稿件。

## 实现
- 一个不联网提交内容、也不使用 localStorage/sessionStorage 的静态页面；可从用户设备导入 .md/.txt。
- 标题、摘要、日期、标签、首页重点、可选 slug 和完整 Markdown 正文。
- 生成同构 Frontmatter：title/summary/date/tags/status/featured，保留正文原字符（除头尾空白）。
- 与正式文章共用 pinned Markdown-it 14.1.0 的浏览器打包版本，`html:false`，避免执行原稿里的 HTML。
- 本地预览、复制、下载 .md；GitHub 原生新建文件 URL 仅包含 `filename`，**不**包含正文。
- 显式展示用户需要在 GitHub Commit 后才会公开，且本地未保存的内容刷新会丢失。

## 验收
- 320/390/1024/1440px：完整字段、前台 Markdown 预览、无横向溢出、导航不孤字。
- 复制内容与下载文件逐字相同，标题/标签 JSON-YAML 转义不破坏 Frontmatter，正文含 `<script>` 不能在预览执行。
- 文件导入不发送网络请求；无外部请求、无草稿持久化；GitHub URL 无 `value=` 或正文参数。
- Pages allowlist 含 /write/ 与 pinned Markdown bundle，同时依然排除 canonical Markdown/构建脚本/内部档案。
- iPhone/iPad/Desktop 实际公网 WebKit，检查预览和新建文件链接；**不**假装已在 GitHub 完成作者登录、粘贴或提交。

## 不在本轮
真实用户 GitHub 会话/最终 Commit、Sveltia PAT 编辑保存，以及独立作者域名。它们不可以被自动化测试中的发文样稿代替。
