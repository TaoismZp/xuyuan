# 网站与《许愿式交付》交叉审计 — 2026-11-04

**性质**：只读诊断结果归档，不是获批的 v7.8 修订，不修改网站代码、正文或既有协议。
**审计目标**：把“个人长文网站是否真正满足站长与读者需要”与“许愿式交付是否真的能验收这一目标”分开。
**现场版本**：GitHub `main` 为 `0d6ba0b8f1d7c8812a166169b3f9f8d639090d8a`；公网验收 GitHub Actions [41818903329](https://github.com/TaoismZp/xuyuan/actions/runs/41818903329)。

## 方法与诚实边界

- **苏格拉底式复核**：先定义“成品”“完成”“独立监理”和“好用”，再查隐含前提、反例、内部矛盾、受影响者与实际后果。用户原有的 `socratic-review/SKILL.md` 保存在其 Mac 本地，不在此运行环境可直接读取；本轮采用以往归档的六类审议框架，并核读了公开的 [Socrates Skill](https://github.com/justinhuangai/socrates-skill/blob/main/SKILL.md)。不可声称已直接执行用户电脑上原文件。
- **精英思维复核**：依据用户图书馆的 `精英思维skill.md`（万维钢·现代思维工具100讲）选择 **7.5 古德哈特定律**为主工具，辅以 **3.10 状态杠杆**、**3.5 信息价值 VOI**、**7.6 指挥官意图**。不泛加载所有100项，不把模型名字当作证据。
- **事实来源**：实际公开网站的 GitHub Actions WebKit 截图和 [验收报告](https://github.com/TaoismZp/xuyuan/actions/runs/41818903329)，[CMS 配置](https://github.com/TaoismZp/xuyuan/blob/main/personal-site-v1/admin/config.yml)，[构建器](https://github.com/TaoismZp/xuyuan/blob/main/personal-site-v1/scripts/build.mjs)，[监督工作流](https://github.com/TaoismZp/xuyuan/blob/main/.github/workflows/personal-site-v1-supervision.yml)，[v7.6 规范](https://github.com/TaoismZp/xuyuan/blob/main/wish-delivery/versions/v7.6.md)。

## 一、结论

网站是**可公开阅读、可由 GitHub 源码自动构建的个人文章站**；不是已全面验证的**站长可以在 iPhone 上独立、舒适地完成编辑→保存→发布的个人出版系统**。原有“全链路完成”表述必须降级。

“许愿式交付”解决了“规划冒充成果、截图冒充运行、公网不是本地”的真实事故，但当前也产生了一个新的结构性问题：**将代理验收指标（PASS、SHA、截图、文档、工作流数）优化成了目标本身**。应当把真实用户闭环置于流程证据之上，而不是继续增加流程层数。

## 二、网站审计：问题与证据

| 等级 | 发现 | 实际证据 | 正确状态 |
| --- | --- | --- | --- |
| A | 站长本人未使用 Sveltia 完成真实 Token 登录、编辑、保存与公网生效；仅 GitHub 连接器直接提交了第一篇文章 | [Acceptance Report run 41818903329](https://github.com/TaoismZp/xuyuan/actions/runs/41818903329) 直接写明 `private-token authenticated write not performed` | **未验收，PENDING_USER**，不能称完整写作闭环 PASS |
| A | 关于页与项目页 iPhone 大字号中文标题被异常断为孤字、破坏预设句子断点 | 同一 WebKit 运行的 `iphone-about.png`、`iphone-projects.png`；[CSS](https://github.com/TaoismZp/xuyuan/blob/main/personal-site-v1/assets/site.css) 手机端 `.page-head h1` 的 `max-width:7ch` | **感知体验 FAIL**；无横向溢出不等于视觉合格 |
| A | 视觉身份链绑定错文件 | [监督/验收脚本](https://github.com/TaoismZp/xuyuan/blob/main/.github/workflows/verify-personal-site-v1-public.yml) 哈希 `VISION_FIXTURE.md`（原始冷纸/钴蓝方向），而已通过用户选择的是 `VISION_FIXTURE_V2.md`（暖白/墨黑/橄榄色） | **参考身份证据不成立**，即使效果可能实际接近 |
| B | 编辑工具需要本人创建且输入具有整个 `xuyuan` 仓库 Contents RW 权限的 PAT；仓库还包含其他项目 | [CMS 配置](https://github.com/TaoismZp/xuyuan/blob/main/personal-site-v1/admin/config.yml) 和仓库结构 | 鉴权入口实测、日常舒适度/最小权限仍需权衡 |
| B | `status: draft` 不让文章出现在 Pages，但原文仍保存在公开仓库 | [后台配置的明确提示](https://github.com/TaoismZp/xuyuan/blob/main/personal-site-v1/admin/config.yml) | 隐私是**已知设计边界**，不是已发生的泄露；私人草稿不能存在这里 |
| B | 关于页描述多为抽象交易原则，缺少可以指认的个人经历、作品与判断演化证据；除第一篇外文章库仍很薄 | 首页/关于页真实公网截图、文章清单 | “作者辨识度、回访理由”尚无读者证据；不得擅自改写成虚构自传 |
| C | 站点正式 URL 为 `/xuyuan/personal-site-v1/`，显得工程路径化；RSS 已生成但前台没有显著订阅入口 | 当前公网与构建器 | 保留为未来低风险迭代，不能压过 A 类缺口 |

**做对的部分**：已有真实公网 URL，第一篇真实长文可读，公开文章的 Git Markdown 可移植；手机阅读排版整体克制、文章章节导航和主站视觉一致，已验证多设备功能，CMS 没绑架前台设计。不能因为 A 类缺口而否认这些事实。

## 三、“许愿式交付”审计：自身矛盾

### 1. 核心闭环被代理指标替代（主问题）
原愿望是“我有个人网站，可以自己发长文”。验收主要证明“GitHub Markdown 可被脚本渲染为网页”和“登录按钮能显示”，没有站长生产授权的编辑写入。它与 v7.6 “核心用户闭环真实跑通才能 Final”冲突。

**苏格拉底反例**：若一个网站公开可读，但主人无法编辑发布，它是否已经完成“我自己发长文的网站”？答案应是“阅读子系统已完成，出版系统未完成”，不是一个统一 PASS。

### 2. “独立监理”更像形式独立，不是证据独立
另一 GitHub Action 用 grep 检查指定 class、固定文案、生成文件，并没以不知实现的用户视角判断中文断行、文案真实性或真实鉴权。监理与建造者共享同一套自写假设，缺陷可在两者间共同存在。

### 3. 身份链中存在直接错绑
公网站点已采用暖白+橄榄色 V2，但 Acceptance Report 的 `Vision Fixture Identity` 来自旧 `VISION_FIXTURE.md`。哪怕截图好看，“绑定正确效果图”这一声明也没有被证实。独立监理同样使用旧文件。

### 4. 部署总控自指悖论
[部署工作流](https://github.com/TaoismZp/xuyuan/blob/main/.github/workflows/deploy-pages.yml) 把 `personal-site-v1/**` 作为推送触发范围，涵盖 `PROJECT_STATE.md`。
每次把“最新已接受的 SHA”写进同一仓库的状态文件，都会生成一个新的 SHA 并重新部署；这又使状态文件里的最新 SHA 落后。**用改写当前对象的方法追求对当前对象的精确自我引用，在此机制下无法收敛**。
改法不是增加第六条 Gate，而是将版本验收证据留在 Actions artifact/Release，或把纯文档排除部署触发。

### 5. 协议当前版本不唯一
根目录 `WISH_DELIVERY_V7.md` 自称 v7.5，`wish-delivery/README.md` 指向 v7.6，`wish-delivery/versions/v7.7.md` 又已存在。v7.7 可以是未晋级候选，但目前没有清楚的状态字段说明。唯一可执行版本应当被机器可读地指出，其余标记为“已废止/草案/归档”。

### 6. 过程复杂度不断附着
每次小改都要增量写监督断言、重跑浏览器、上传截图、写状态和触发整站部署。v7.6 已规定“Monitor Must Be Simpler Than Product”，但当前同一页面的小修可能被冗长的自检/状态机制拖住，用户连续说“继续”也显示推进时钟没有彻底从用户身上移开。

### 7. 许愿式的自主性有物理边界
没有用户授权不能代替用户登录、付款或批准不可逆动作；普通聊天回合结束后也不能假设仍在后台执行。因此自治交付须区分 `READY_FOR_OWNER_ACTION` / `BLOCKED_USER` 与 `VERIFIED_FINAL`；不能把用户必须做的最后一步重新定义成已经完成。

## 四、精英思维模型执行：目标—代理—瓶颈—信息价值

**主工具 7.5 古德哈特**
- 真目标：作者能在真实手机上长期发布并维护自己的文章，读者能稳定访问、理解与返回。
- 代理指标：CI PASS、网页 HTTP 200、截图数量、文档四件套、相同 commit SHA。
- 失真机制：为了让所有代理指标亮绿，优先实现和测量容易被自动证明的任务；难以自动验证的用户真实编辑体验和阅读价值反而一直被推迟。
- 修复：每个 Gate 都只能为它实际证实的事实背书；`NOT TESTED` 必须保持中立，不能被上游 PASS 覆盖。

**补充 3.10 状态杠杆**
- 当前关键约束不是再做新的首页特效，也不是多一个监理脚本。
- 当前先修**中文断行与错误 Vision 绑定**，并完成**站长手机发文路径**的真实操作验收；其他优化先暂停。

**补充 3.5 信息价值**
- 一次真实手机“从打开后台到真实文章发布”的演练，得到的信息可能立即改变 CMS 选型与交互方案，比继续做十张同风格截图更能改变决策。
- 对读者可用性，找几位没有看过项目施工过程的真实读者阅读一篇文章并复述作者主题、操作反馈；没有真实读者证据时不要假装已获市场验证。

**补充 7.6 指挥官意图**
- 目的：让作者独立发布、读者舒适阅读。
- 最终状态：站长真实操作 + 公网可读 + 可继续维护。
- 禁区：假文章、私密草稿误公开、未授权改原文、截图/CI 替代用户真实闭环。
- 执行者应被授权自主换手段，但不能把“跑齐 6 段流程”当成目的本身。

## 五、建议整改顺序（不是已获批改动）

**A / 先修，停止新功能**
1. 修 iPhone 关于页和项目页的中文断行；在 320/375/390/430 像素截同一文案的真实浏览器截图，并人工看首屏。
2. 正式将 `VISION_FIXTURE_V2.md` 作为验收参考；旧 V1 明确归档、不得再给候选盖章。
3. 把核心闭环明定为“作者本人手机编辑并保存 → GitHub 提交 → 正式 Pages 更新 → 新访客能读”；目前应标记 `OWNER_AUTH_PENDING`，直到站长亲自完成真实操作。Token 只在后台输入，不传聊天。

**B / 紧随其后**
4. 决定私人草稿留在本地/私有仓库，正式公开时进入公开内容仓库；避免将 Public Git 的 draft 误当秘密空间。
5. 把“文档改动”排除网站部署触发；验收的 commit 只在 Actions/Release 或外部报告作凭据，避免自指失配。
6. 将“独立监理”改成 **规则 CI + 真实体验/反证测试** 两层；前者不许宣称取代后者。
7. 唯一规范指针：标明 v7.6 active，v7.7 draft 或按实际授权正式晋级；根部旧版明示历史归档。

**C / 有真实内容和使用证据后再做**
8. 作者辨识度、订阅入口、独立域名、更多栏目，必须以真实内容、真实用户反馈与成本为依据。暂不为了首页好看而造文章。

## 六、更新条件与停止规则

- 在真实 owner 操作前：**网站阅读子系统可视为接受，个人出版闭环不得 Final**。
- 真实编辑发布通过后：重新判断是否还有核心阻塞；不得用一次成功推断长期稳定，需要至少一次修订/回滚演练。
- 修好移动端断行并完成正确参考绑定后：才可再次宣称移动端感知视觉 PASS。
- 若两轮新流程改动不能缩短真实交付闭环或降低用户参与成本：暂停增加条款，检查是否已再次古德哈特化。
- 本报告未修改生产网站，也未把提案纳入 v7.6 或 v7.7。只有获得用户对实质规则修订的授权且完成相应实验，才生成新的不可变规范版本。
