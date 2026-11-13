# 工程样例恢复（不是正式 main 发布）

本目录仅含公开合成正文和临时 Git 运行证据。RECEIPT.json 的 model_called/private_manuscript_read 均为 false。

在本目录外创建新目录，从 bundle 恢复代码，再检出回执 activation_commit：

```sh
git clone fault-and-restore.bundle /private/fixture-code
git -C /private/fixture-code checkout a4ea7fd8c1e68be9a78d7a9ebe73de19f8c157f0
python3 /private/fixture-code/deepwrite/release/activation.py --root /private/fixture-code --run -- identity
```

checkpoint/manifest.json 的外部 SHA 为 d039ccff89f858cb1526df39538beb3161d5902de5fa6355843f08fe2a4b8d7f。通过该已验证的工程入口执行 restore，目标目录必须全新；再用恢复 STATE 的外部 SHA 执行 resume。13个声明文件身份见 RECEIPT.json；原始16条命令/输出见 COMMANDS.json。ARCHIVE_SHA256.json 对演练原档列SHA；本REPLAY说明在演练后追加，不属于原演练输出。

实际故障提交 bb9f7b42b8621d13b5e55c5ed090b99471317b0b 被入口拒绝，检出上述有效提交后同项目继续。此证据不等于 GitHub main 已完成发布或自动回滚。
