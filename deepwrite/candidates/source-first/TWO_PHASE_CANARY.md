# DeepWrite 两阶段源学科→章节发现候选（v0.2-canary.2）

> **状态**：PR #19，堆叠依赖 PR #18→PR #14。**只允许 CANDIDATE_OPT_IN、真实授权项目和私有工作目录。** GitHub `main/deepwrite/CURRENT.json` 仍 v0.1；本候选没有宣布正式引擎发布，也没有通过真人质量验证。

## 解决的上一版真实缺陷

PR #18 虽然为 E18 引入了 `source_first_architecture` 和知识复利模型审查，但 E18 在 `__init__/_validate_config` 阶段就必须得到 `chapters`，然后才调用研究模型。作者指出，连框架和章数都可能错误，不能再将23篇课文直接当23章，也不能让某个领域的已有目录诱导另一门学科。

本候选 `architecture_discovery.py` 是写作器**前置的独立真实阶段**，在源研究前**明确拒绝预设章节和读者概念依赖图**，避免原本顺序错误：

1. **SOURCE_DOMAIN_STUDY**：首次实际模型调用阅读项目私有 `sources/*.md` 已冻结 SHA 的原文，输出独立原学科机制、原文逐字定位、反方和≥2个研究方向；不允许提早给定目录。
2. **BOOK_ARCHITECTURE_DISCOVERY**：第二次模型调用只在读取上一步研究后，自主提出临时章节数量/顺序、每章独占的读者变化、概念依赖、三层读者 + 知识复利迁移目标。章节数在作者允许的上下限内由模型提出，**不等于作者批准或者已验证最优**。
3. **FREEZE → E18**：生成 `sources/discovery_native_study.md`（私有工作目录）、`discovery_receipts/writer_config.json`、`architecture.json`、两次模型 request/response 证据与 `STATE.json`，校验来源SHA、作者合同、两阶段顺序、条件/概念/目录数据。之后将 `writer_config.json` 送现有真实 `writing_loop_experimental.py`，按原阶段迭代写章、反方审稿、返工、合订、恢复；模型内部PASS不等于实际作者/读者认可。
4. 整个过程仅保留**独立私有项目目录**，公开库不写私有原稿、授权文件或模型输入/响应。断档可按私有 recovery 对照两阶段事件/响应SHA恢复，**本阶段尚没有通用自动失败重试**，一旦返回 BLOCKED 应保存证据并由操作人决定新运行ID与新目录。

## 准备（必须由实际项目所有者授权）

项目目录例如：
- `/private/deepwrite-project/sources/material.md`——真实私有知识源的完整原文；
- `/private/deepwrite-project/sources/author-contract.txt`——项目所有者授权，符合 `deepwrite/author-project-authorization/v1`，`mode=AUTONOMOUS_FULL_DRAFT` 且 `chapter_scope=ALL_CANDIDATE_CHAPTERS`；
- `/private/deepwrite-base-config.json`——从 PR #18 `deepwrite/candidates/source-first/README.md` 与 E18 的正式配置 schema 出发，补充必要的 model、真实授权源文件 SHA、pins、版本身份与预算，**必须删去** `chapters`、`reader_prior_knowledge_contract`、`source_first_architecture`。没有真实全书授权，不得把当前用户“继续/下一步”猜成跨项目全书授权。

新增必填：
```json
{
  "channel": "CANDIDATE_OPT_IN",
  "adapter": "codex",
  "discovery_token_budget": 20000,
  "discovery_output_cap": 5000,
  "min_chapters": 1,
  "max_chapters": 12,
  "modules": {
    "e18_loop": true,
    "source_first_architecture": true
  }
}
```

示例只是补充字段：**不是完整配置**，不能直接运行；模型实际名字、作者授权、源内容SHA、固定版本模块pins、项目ID必须在你的私有环境真实配置，不能粘贴示例中的假哈希。若使用 `adapter=responses`，必须有经授权的真实 provider API 凭据；若使用 `adapter=codex`，必须有可用的已登录 Codex CLI。fixture 模式只在工程测试时经注入脚本启用。

## 真实执行命令

```bash
# 前置：所选候选分支精确HEAD，代码有Git身份，Python3.10+
python3 -B deepwrite/candidates/source-first/architecture_discovery.py \
  /private/deepwrite-base-config.json \
  /private/deepwrite-project \
  /private/deepwrite-discovery-receipts

# 仅上一步生成成功且审查过临时章目后，执行实际E18
python3 -B deepwrite/tools/writing_loop_experimental.py \
  /private/deepwrite-discovery-receipts/writer_config.json \
  /private/deepwrite-project
```

本步骤一次性完成的只是**临时研究/章节发现**；后续E18是否真正写完本书、模型是否授权、作者是否接受、是否比逐章高质量等都单独验收。**动态章数目前只在入稿之前生成一次，整书跨章返工以后重新规划结构仍未实现。**

## 质量门和工程证据

- `PASS_ENGINEERING_ONLY`：真实阶段调用顺序、精确来源引文、SHA、至少两研究方向、临时章数和概念依赖、真实E18脚本的模拟接入；一切由GitHub Actions本分支最新CI回执为准。
- `BLOCKED`：缺原始资料、SHA不匹配、预设目录、无效项目授权、预算超额、模型无实际输出、选中不存在的研究方向、读者依赖成环、研究/章节信息不匹配、private目录不符合要求。
- `NOT_IMPLEMENTED`：动态 `ASSISTED_AUTHOR_GATED` 章作用域的安全语义（未知章ID时作者不能预签具体章节）；模型可自由整书重编与真实人类读者反馈闭环。
- `UNVERIFIED`：模型真的发现独立洞见、源研究的正确性、王路六维知识复利的真人迁移、黑箱写作不劣于逐章、真provider 401解除。
- `FORMAL_RELEASE_NOT_RUN`：PR #19、#18、#14均不得单独视为正式新版本，main CURRENT未经作者审批和治理门不改。

## 必须执行的独立验收

在一份有合法私有源材料的未见过题材上先跑**真实provider研究→临时章图→E18完整写作**，固定基线与同预算对照；隐去版本标签交给与作者及模型审稿分离的真实读者，检查新手理解、熟手增量、高手源学科正确性、知识复利独立迁移。未得到真实结果不得将 `v0.2-canary.2` 宣传为全书质量成功。

**唯一下一步**：当前候选工程测试通过后做有真实模型授权的私有canary；保存相关SHA、原稿、全部QA和读者反方；按权限审查PR后才可能正式激活。
