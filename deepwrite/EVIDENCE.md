# DeepWrite v0.1 验证与能力缺口（2026-11-08）

## 真实已验证

- 通用SHA256只读书稿打包器已存在：[tools/book_packager_v0.1.py](tools/book_packager_v0.1.py)。
- 在本轮的本地执行环境使用两章**合成数据**进行正常装订：\`PASS\`。
- 修改其中一章而不更新manifest SHA256：拒绝装订，返回 \`SHA256 mismatch\`，\`PASS\`。
- 提交非法章节顺序：拒绝装订，\`PASS\`。
- 公共 GitHub 文本文件经 create 后重新 fetch 内容与版本：需要运行和记录；脚本详见 [tests/test_packager.py](tests/test_packager.py)。
- 这些结果**只验证字节身份、次序与错误拒绝**；不验证AI写作质量、GitHub自动建仓、真实独立编辑或完整新书自主生成。

## 尚未验证

- \`E1_AUTONOMOUS_FULL_BOOK\`: \`NOT_IMPLEMENTED\`（无一次调用独立产出完整陌生书的真实闭环）。
- \`E2_UNSEEN_TOPIC_BLIND_AB\`: \`PENDING\`（需公平比较旧式批量与内循环两路）。
- \`PRIVATE_REPO_CREATE\`: 当前GitHub连接未暴露新建repo动作；新项目必须私有立项，能力不足则诚实 \`GITHUB_PRIVATE_REPO_PENDING\`。
- \`COLD_CHAT_BOOTSTRAP\`: 新对话需实测能否直接读取本项目、创建私有检查点；未做之前不能宣称跨对话触发已自动安装。
- \`PRIVATE_MANUSCRIPT_GITHUB_MIRROR\`: 不在公共仓库存私有文稿；仍受私有repo创建权限和用户授权约束。

## 注意

本文件是公开可审的**能力状态表**，不是对所有此前私人对话的完整备份报告。全套私人书稿与详细审稿还需要独立私有保管与异地备份。
