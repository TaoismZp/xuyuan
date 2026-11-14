# DeepWrite 正式激活与发布

正式身份来自 GitHub main 的 `deepwrite/CURRENT.json` 及其绑定的不可变 release record。工作台规范版本与工程引擎版本独立；历史候选登记、旧恢复页和聊天记忆都不定义最新版。

## 唯一正式入口

需要 Git、Python、可核的完整实现历史、有效模型权限及私有项目存储。先在新检出或隔离工作树核对实际 main；保留已有修改。普通 GPT 对话若不能执行命令，只能转交具备能力的环境，不能自称已运行引擎。

```bash
python3 -B deepwrite/release/activation.py --root . --run -- identity
python3 -B deepwrite/release/activation.py --root . --run -- \
    run /private/deepwrite-user-request.json /private/deepwrite-project
python3 -B deepwrite/release/activation.py --root . --run -- \
    status /private/deepwrite-project
python3 -B deepwrite/release/activation.py --root . --run -- \
    resume /private/deepwrite-project --expected-state-sha256 <64-hex>
```

解析器验证当前指针、规范和父协议、release record、真实 implementation commit 祖先及全部声明文件 SHA，再实际启动默认执行器。请求格式见 [DEFAULT_INVOCATION.md](../DEFAULT_INVOCATION.md)；新项目记录来源、请求、双层版本及模块身份。旧项目按锁定版本恢复，不静默升级。

当前统一入口支持 `identity/run/status/resume`。旧工程 runtime 的 `init/assemble/checkpoint/restore` 只适用于其原版本；不能作为当前启动命令。恢复要求外部保存的 `writer_project/run_state.json` SHA，样章继续还需项目/合同/正文绑定的真实作者回执。现有 E15、装订和 checkpoint 工具由工作流复用，不要求作者手动逐项调度。

## 两类发布分别验收

- **ENGINEERING_PATCH**：身份、恢复、日志、错误阻断及既有行为的执行修复。需要实际 CI、负向回归、回退证据、精确 HEAD 的所有者发布授权及不改变认知策略的理由；不能用测试绿灯掩盖已知事实/隐私失败。
- **QUALITY_BEHAVIOR_CHANGE**：研究视角、问题定义、选择/返工策略、文风或认知提示的改变。还需实际作品对照、失败回归、作者判断与独立读者证据。当前控制器对此类自动晋升保持 HOLD；作者授权研发/发布不等于这些质量证据已取得。

已正式接线的写作能力可以继续使用；工程发布只说明实际调用身份与行为回归，不保证作品质量。E1真实模型整书、E2完整作品公平对照、三层真人阅读收益和黑箱非劣须保留真实状态。

代码先提交，再以独立提交生成绑定 implementation commit 和全部文件 SHA 的 release record，并原子更新 CURRENT。旧记录不可改写。正式合并只使用 **MERGE COMMIT**，保留 implementation 祖先；SQUASH/REBASE 不适用。

## 所有者授权与必需 CI

目标保护为 main 禁删、禁强推、无 bypass、strict 最新基线、两项必需检查（Actions app15368）：

- `activation-and-runtime-regressions`：真实 main PR CI，不以路径过滤使其他 PR 悬空。
- `owner-release-authorization`：只运行可信 main 控制器，根据真实所有者身份、精确 HEAD、实际 CI 和差异范围生成；新 HEAD 不继承旧授权。

单人仓库用可追踪的 owner 发布决定，不能伪造另一位独立 reviewer。作者已授权本次工程发布时，执行者可在该范围内提交并保存精确 HEAD 的所有者回执；不能扩大为未来任意认知发布。命令第一行：

```text
/deepwrite authorize ENGINEERING_PATCH <完整40位PR-head-SHA> governance
```

仅控制平面实际变更且已授权时使用 `governance`。`/deepwrite revoke <完整head-SHA>` 撤销。控制器从 main 运行，候选仅作数据检查，不执行候选高权限代码；真实配置、授权和 CI 满足后才启用正常 merge 的 auto-merge。

现有控制器在 PR21 合并后已进入 main，早期“控制器尚未安装”的说法是历史。**配置是否生效必须重新读 API**：最近证据仍为 reviews=0、required_checks=[]、strict=false、auto_merge=false；管理 PUT/PATCH 返回403。准确观察及未关门见 [STATE.json](STATE.json)，不得把目标配置当作已部署。GitHub同一Actions App的状态名也不能证明来自某段指定代码；恶意write主体仍是信任边界，不宣称替代独立安全审批。

## 发布后的真实验收与回退

合并后重新读取 main/CURRENT、release record 与 Git SHA；从新检出的 main 实际运行 `activation.py --run -- identity`，确认默认入口和实现祖先。读取合并后 push/main CI 中的全新环境调用步骤，不能沿用 PR 中 skipped 的结果。保存命令、退出码、实际 CI/check ID、授权来源与私有恢复入口，并回读 Git Blob。

回退优先在隔离工作树演练：检出 release record 的 rollback commit，核验旧 CURRENT 与对应文件；不覆盖书稿。旧版本若无正式 runner，应安全拒绝，不伪造“旧版也能自动写书”。checkpoint 恢复以独立目标目录和逐文件 SHA 验证，损坏副本必须被拒绝。

正式 main 回退须另有授权 PR，恢复旧 CURRENT 及匹配 runtime，保留失败候选与私人作品；合并后重新运行旧正式身份。隔离代码回退、字节恢复、完整项目resume和作品质量分别记录，不互相冒充。
