# 许愿式交付 v7.5 — 跨对话接班模板（操作附件）

本模板是对现有 v7.5 Execution Continuity 和 Binding Chain Gate 的**实施样板**，不是新的不可变版本或独立的验收捷径。

## 目的

任意一次 ChatGPT 长对话无法回复，新的执行者从**项目外部可信档案**恢复，而不是依赖模型记忆、旧聊天摘要、截图或主人重述。

## 每个长期项目的最小 Checkpoint

建立合适权限的项目空间（私密资料不能放公开仓库），至少保存：

1. `RECOVERY.md`：用户一眼能看懂、可发给新执行者的唯一入口；给出真实项目地址、唯一下一动作和不可替代的原始目标。
2. `recovery/state.json` 或同等结构：项目 ID、主 Artifact、用户实际 Delivery Surface、Vision 版本与 hash、唯一有效 Blueprint 版本与 hash、最近发布 commit、监理和验收的证据身份、未关闭的 A 类问题与 Pending Owner Gate。
3. `PROJECT_STATE.md`：人工可读的版本、变更原因、已验收 / 未验收边界、后续执行入口；原稿和旧版不覆盖。
4. **可复现检查**：本地无聊天依赖的程序及独立 CI；至少核对引用文件真实存在、身份链一致、关键交付入口可达。公网自动冒烟并不替代用户真实使用验收。

## 施工过程中的纪律

- 每个**真正验收通过**的里程碑立刻写入 checkpoint，再推进下一阶段；未经验证的工作仅标 CANDIDATE。
- 发生错误时先从最近已验收 checkpoint 检索，再验证 Git 提交、验收构建与公网版本一致；不根据“我记得做完了”直接继续。
- 文档更新是归档动作，不得用文档的最新 Git HEAD 冒充网站当前已部署的 commit。
- 新对话优先读取 RECOVERY.md 和机器状态，然后自行核对 Git/CI；仅当账号认证或不可逆动作需要用户执行时才介入。
- 公开库只能写公开事实；完整 ChatGPT 导出、密码、Token、私人原稿、邮箱和未经允许的历史聊天内容都不得写入公开仓库。
- 如果用户要找回**逐条聊天文本**，本方案不能代替账号数据导出；该动作需要账号所有者通过 ChatGPT 数据控制申请。

## 防回归验收

- A：在新对话不给任何历史，只提供 RECOVERY.md URL，能读到原始 Vision、最后已验收版本、下一项未完任务。
- B：故意把 fixture hash 或已验收身份改错，CI 必须 FAIL；任何新提交不得冒领原 PASS。
- C：确认用户真实打开的公网入口及核心闭环，不拿 localhost / repo / 截图冒充。
- D：每个阶段的 auth、write、publish Gate 明确标成 PASS / PENDING / FAIL，不允许由浏览器登录入口测试推断作者登录成功。

## 本仓库的已实现样例

- 接班入口：`personal-site-v1/RECOVERY.md`
- 机器状态：`personal-site-v1/recovery/state.json`
- 校验程序：`personal-site-v1/recovery/check.mjs`
- 独立 GitHub Actions：`.github/workflows/personal-site-v1-recovery.yml`

未来新项目应使用自己的独立空间和权限边界，不应把所有项目数据都塞进 `TaoismZp/xuyuan` 公开库。
