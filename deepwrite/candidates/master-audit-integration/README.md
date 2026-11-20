# DeepWrite 总审整书候选

候选入口从一个已提交的检出验证代码和版本指针。请在私有输出目录使用它。

```sh
python3 -B deepwrite/release/activation.py --master-audit-candidate --run -- identity
python3 -B deepwrite/release/activation.py --master-audit-candidate --run -- run /private/request.json /private/book-project
python3 -B deepwrite/release/activation.py --master-audit-candidate --run -- status /private/book-project
python3 -B deepwrite/release/activation.py --master-audit-candidate --run -- resume /private/book-project --expected-state-sha256 <sha256>
```

运行请求沿用正式工作台格式。恢复使用同一候选提交和外部保存的 `writer_project/run_state.json` SHA。样章先审模式继续要求外部作者回执。

G6/G7 写作阶段复核和装订之后，统一入口验证拓扑决定和完整装订清单。KEEP 审原稿，REPLAN 审实际派生版本并重新生成分片清单。模型逐节报告机制、反方和定位问题，再用章报告检查全书。总审还对装订字节做逐片模型调用与引用核对。重要问题触发至多一轮关联章节全文返工、定位复核及修订稿整书审读。显著缩减、未关闭问题、缺少凭证或预算超限会停在候选阻断状态。

审计凭证保存在项目的 `discovery_evidence/master_audit` 下。逐次记录模型实际请求和响应并以原子文件提交，最终就绪由 `status` 和 `resume` 重放同一证据链算出。已保存的响应可以继续复用。若中断发生在已发请求和响应入账之间，调用成本未知，需要先核对该请求。手改外层 `RESULT.json` 不会关闭问题。具有整个项目存储写权限的人可以篡改所有本地材料，发布验收仍须对照独立保存的检查点和作者验收凭证。

独立的 PR #26 CLI 只核凭证和字节。总审运行时额外验证章映射、走过的模型审查和实际修订。模型仍可能漏判、误判或无法做外部事实核验。代码记录的模型审读不提供真人判断。超过单章上下文上限将说明阻断原因。

如作者已有逐章写作参照，可在私有请求中提供 `sequential_baseline`，其中 `path` 指向正文，`sha256` 是外部保存的版本校验值。进入总审前及完成返工后，如果候选稿字符数低于参照稿的 75%，需要检查独有内容是否丢失。该信号仅用来触发审查。是否比逐章路线更好仍需要同来源、同预算的作品配对和读者评价。

CI 用合成稿和脚本模型跑同一写书链及真实 PR #26 门禁。真人作者和读者验收、自然场景下的质量改进及黑箱和逐章写作非劣性继续待证。已发布引擎由 main 的 CURRENT 指向，候选提交需经过单独授权才能进入正式发布。
