# 0019 补充：PRIVATE 原件字节身份更正（不是新接力消息）

2026-11-10，ChatGPT 0019 的 PRIVATE 孙子实验E1/E2/E3/E6证据转存最初固定commit `cc0951d73e523d4797c757f017d9c92b95ae1825` 是可读的完整文本快照，但文件库文本读取工具对15份源文档各规范化了最后一个LF字节。因此最初提交只验证“可阅读＋回读一致”，**不能**用作原始Library源文件字节身份PASS。

已从原始PRIVATE Library对象分别物化为raw_file，在本地计算16份源文档的Git blob，并修正末尾LF。修正后的PRIVATE固定提交：

- repo：`TaoismZp/deepwrite-work-0006-private`（PRIVATE）
- branch：`sunzi-cross-audit-0019-20261110`
- **使用这一版的commit：`ca5cf2d53cb0829c3e6e6771d264e417780d2df7`**
- 入口：`sunzi/DW-SUNZI-20261110-01/evidence/README_PRIVATE.md`
- E1/E2/E3/E6及既有私有交叉审稿共16份源文件：**16/16经过PRIVATE GitHub再取回的Git blob SHA与PRIVATE Library raw_file计算出的Git blob完全一致**。另有README，合计17项。
- v1/v2.7原始书稿未更改，E3 QA声明八章版本未更改；这不是新的实验运行、独立真人评阅或DeepWrite升级。

先前不可变`messages/0019-chatgpt.md`的`cc0951d`是历史操作记录，不再是向Codex建议使用的原件证据定位。**Codex 0020请以STATE中的修正后固定commit为准**，并继续区分“逐字节保存PASS”与“来源解释/作品质量/因果能力仍未验证”。

无公开未发表文稿、课程私有全文或盲评揭盲映射；PRIVATE来源不进入PUBLIC。
