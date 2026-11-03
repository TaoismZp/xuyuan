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
