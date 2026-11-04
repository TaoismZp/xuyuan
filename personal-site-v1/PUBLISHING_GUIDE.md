# 个人长文网站：发文与内容隐私边界

## 日常写作

打开 https://taoismzp.github.io/xuyuan/personal-site-v1/admin/ ，用 TaoismZp 账号的 **fine-grained GitHub personal access token** 登录。Token 仅需授权 `TaoismZp/xuyuan` 的 **Contents: Read and write**；请设置有效期与最小权限。只在 CMS 登录界面输入，不要发给聊天助手，也不要提交到 GitHub 文件。

进入「长文」，填写标题、摘要、日期、标签和正文，将状态改为「已发布」后保存。CMS 会向 GitHub 写入 Markdown，GitHub Actions 重新构建网站。文章链接形如 `/personal-site-v1/essays/<文件名>/`。修改已发布文章后再次保存，将触发同一发布链路。

## 重要：草稿不等于私密

`TaoismZp/xuyuan` 是**公开仓库**。`status: draft` 只表示不进入网站首页、文章列表和正式正文页；**提交到 GitHub 的草稿依然可以通过 GitHub 公开源文件读取**。请不要把未公开的私人手稿或敏感资料保存到这个仓库。真正的私人草稿应保存在受控的私人空间，等准备公开时再复制进 CMS。

已经加固的 Pages 部署仅打包允许展示的前台页面、静态资源和 CMS 入口；不再把站点的 `content/posts/`、构建脚本、node_modules 或内部报告复制到 GitHub Pages。**这项加固不能改变公开仓库源码的可见性**。

## 修改、归档、恢复

- 编辑原文并保存：重新发布对应文章。
- 改为「已归档」：文章从下一次构建的公网展示中移除，但原文仍在公开 GitHub 仓库。
- 改回「已发布」：下一次构建恢复文章地址。
- 删除源文件会删除该篇文章的网页（下次构建）；Git 历史通常仍保留旧内容。不要把删除当成彻底销毁已公开的文字。

## 当前验收边界

已经在隔离的 CI 环境验证 Markdown → 首页 / 归档 / 正文，以及草稿不进入展示页。已在真实公网验证 CMS 登录入口。**尚未使用站长自己的 Token 完成生产环境首次授权保存**，因此这一项仍需真实作者发文时验收；不会假装完成。

## 分享与订阅

正式发布后，生成器会自动更新文章的 canonical URL、Open Graph/Twitter 分享信息、RSS 订阅和 Sitemap，无需手动填表：

- 文章分享：页面「分享这篇」使用没有追踪参数的规范链接。
- RSS： https://taoismzp.github.io/xuyuan/personal-site-v1/feed.xml
- Sitemap： https://taoismzp.github.io/xuyuan/personal-site-v1/sitemap.xml

只有 `status: published` 的文章进入这些索引；公开 GitHub 源文件的可见性仍由仓库决定。分享预览的实际效果依赖接收平台抓取与缓存策略，不保证每个平台立即显示一致。

## 无需额外 Token 的轻量发文入口

打开 **https://taoismzp.github.io/xuyuan/personal-site-v1/write/**

- 把已准备公开的文章粘贴进去，填标题、摘要、日期和标签；或者导入本地 `.md/.txt`，在手机上预览正式 Markdown 排版。
- 点击「下载 .md 备份」保留一份本地文件；点击「复制完整发布稿」将含 Frontmatter 的文章复制到剪贴板。
- 点击「去 GitHub 新建文件」。这一步只将**文件名**放入 GitHub URL，**没有将文章正文放到查询参数**。使用已登录的 GitHub 账号粘贴全文，确认直接提交到 `main`，才会发生真正公开发布。
- GitHub Pages 构建完成后到长文列表或文章完整地址验证。网页表单**没有接入 GitHub 的写入 API，不会悄悄发文**。
- 在提交前，这个页面既不自动上传也不自动存储草稿；**刷新/关闭可能丢失表单内容**，请先下载备份。不要在公共电脑上编辑敏感资料，也不要把私密草稿提交到公开仓库。

**限制**：这条路径比 Sveltia 多一次复制粘贴，主要服务于首次发文或不想单独创建 Token 的场景；GitHub 网页编辑体验由 GitHub 提供，且真实 GitHub 登录、Commit 和公网更新仍需站长亲自执行才能验收。
