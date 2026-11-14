# DeepWrite E23｜源领域视角竞争 → E18 写书候选连接（SHADOW）

状态：**EXPERIMENTAL / NOT_ACTIVE / ENGINEERING_ONLY**。此目录不包含任何私有书稿、用户聊天、未发表内容或密钥。

## 这轮到底“接入”了什么

此前 E18 写书试验的 `WritingLoop.run()` 依次执行 research → direction → draft → review/rewrite → cross-close → assembly；研究方向仍来自模型叙述文本，它没有自动强制冻结旧稿、查出处与做竞争视角核验。E15守卫能检查**已经报告的**错误被真实修正，不能自动发现未被报告的“思想旧知”。

本候选添加显式入口 `prewrite_entry.py`，**在 E18 任何模型调用之前**：
1. 按 SHA256 读取旧稿全文、至少一种源领域资料和三套以上互相竞争的解释（manifest）；
2. 对已存在的思想作证据绑定的 RECOVERED / REFRAME / HYPOTHESIS_NEW 判别，旧稿明确涵盖的观点不得标为新发现；
3. 由外部选择文件指定一个**尚待反方评审的**实验视角，拒绝用“RECOVERED/已获作者认可”等自封标签跳门；
4. 实际写入三个新材料文件到私有项目的 sources/，逐个 SHA256 冻结；
5. 生成新的独立 E18 config，追加三个 source 引用，并修改 **wish** 要求后续 research 和 direction 将其作为受检验假设，而不是当成已被证明的命题；
6. 默认只**准备输入，不调用模型，不运行写书器**。只有显式 `--execute --runner <existing E18 writing_loop_experimental.py> --runner-sha256 <实际预期SHA>` 才继续调用本仓库同一份 E18，拒绝任意脚本替代。需要可用的模型API/登录、预算和所有既有E18安全条件。

### 正面与负面工程结果

与此分支上传版本逐字相同的本地测试：`test_perspective_gate.py` 9/9 PASS，`test_prewrite_entry.py` 8/8 PASS；实际私有旧书两项老思想负控被拒，最新旧书**全文**四解释测试中三条旧观点被拒，一条 REFRAME 仅待审。四解释的文本及私人证据位于用户私有恢复档案，本公开分支无私稿。

本候选能证实的是**证据、老稿查重、模型调用前停止、以及材料和方向配置真的传给 E18**。不能证明哪个解释最有洞见、后面生成文本的质量，也没有证明真实live E18写书、独立盲评和跨项目稳定收益。

## 可复核工程命令

```bash
python3 -B -m unittest discover -s deepwrite/candidates/e23-frame-wiring -p 'test_*.py' -v
python3 -B -m unittest discover -s deepwrite/tools/tests -p 'test_writing_loop_experimental.py' -v
```

示意（路径都由作者私有项目提供，切勿提交真实书稿到这个仓库）：
```bash
python3 deepwrite/candidates/e23-frame-wiring/prewrite_entry.py \
 --config /private/E23_runner_config_unprepared.json \
 --manifest /private/E23_frame_manifest.json \
 --selection /private/E23_frame_selection.json \
 --project-root /private/E23_shadowsource \
 --prepared-config /private/E23_runner_config_prepared.json
```

候选输出 `PASS_PREWRITE_IDENTITY_AND_PROMPT_WIRING_ONLY` 不是 `PASS_QUALITY`。有三个已知限制：**E18原CLI仍可被直接绕过**；SOURCE_FRAME的语义优劣仍由模型/作者审稿（非自动识别）；自动执行完整书的真实生产与发布仍没有通过验收。要让它成为“默认必经门”，必须单独把验证调用并入正式 E18 的最早入口，并通过真实失败复现、回归、权限和作者受保护发布。不能把一个可选wrapper冒充完成集成。

DeepWrite `CURRENT.json` 仍正式 `v0.1`，许愿式交付 `CURRENT.json` 仍正式 `v7.6`。本候选以E18实有runner `experiment/deepwrite-e18-closure-runner-20261111` 为基座，不覆盖其分支或PR12/13。正式升版需独立授权与作者验收。

## 2026-11-13 读者先修与源领域评审接线

`reader_source_gate.py`是供同一 E18 调用的执行检查。它冻结读者已知/未知、概念首次解释/使用和先修图；模型的源领域评审必须绑定实际正文、源材料位置与合同SHA。源错误或负知识复利报告返回 `STOP_RESEARCH_MORE`；读者先修/价值缺陷报告返回 `CONTENT_REWORK`；缺真实评审、错版SHA或只在QA里写证据返回 `HOLD_REVIEW_EVIDENCE`。E15继续负责冻结问题、正文真返工和重新关闭，没有另外建立写作器。

这段代码只核验已提供的模型观察与字节身份。词典代替因果、错误规则、初学介绍无研究增量、机械三层重复、后章复用旧错等负控的语义报告由fixture预先给出，不能据此宣称模型已自动识别真实缺陷。正向控制不要求指定词语、三层标题或六评分；完整严谨的叙事允许零实质问题通过，真人/作者验收始终未由代码建立。

配置提供 `reader_prior_knowledge_contract` 时，prewrite会把同一合同写成实际冻结source并传给后续runner。`e23_preprocess_receipt`记录代码与输出SHA；不在当前Git提交中的源码commit为null。下游只能称“预处理回执字节匹配”，不能把可写JSON当成独立调用证明、当前run里加载了E23或正式激活。正式状态仍从main CURRENT与真实调用证据判断。
