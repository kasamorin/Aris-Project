# 标准 GitHub 项目开发流程（按角色拆分）

先看整体：一个托管在 GitHub 的项目，主线基本是 **Issue → 分支开发 → Pull Request（PR）→ CI 检查 → 代码评审 → 合并 → 发布**。主流协作模型有三种，先对号入座：

- **GitHub Flow**：main 分支永远可发布；任何改动都从 main 拉一个短生命周期分支，改完开 PR 评审合并。官方定义的核心步骤是：建分支 → 改代码 → 开 PR → 处理评审意见 → 合并 → 删分支。[cite:9700fb]
- **Fork & Pull（复刻和拉取模型）**：没有写权限的人先 fork 仓库，改完向上游仓库发 PR。开源项目的标准做法，降低了新人参与门槛。[cite:5fff7a]
- **Git Flow**：main + develop 双主干，配 feature / release / hotfix 分支，适合有明确版本发布节奏、需要维护多个版本的项目。[cite:6240f2]

下面按身份逐一展开。

## 一、项目所有者 / 维护者（Owner / Maintainer）

**定位**：仓库的决策者，决定"什么能进主干、什么时候发版"。权限通常是 Admin / Maintain。

**项目启动阶段（一次性配置）**：
1. 建仓库，补齐基础文件：README、LICENSE、CONTRIBUTING.md、CODE_OF_CONDUCT、SECURITY.md、Issue / PR 模板。
2. 配置**分支保护规则**（需要 admin 权限）：要求合并前必须开 PR、必须通过评审、必须通过状态检查（CI），还有"要求线性历史""需要合并队列"等选项。[cite:33bc50][cite:f54e7e]
3. 配置 **CODEOWNERS**：指定模块负责人，改动对应文件时自动请求其评审，可配合分支保护里的"要求代码所有者审阅"。[cite:d970ee]
4. 建立标签体系（bug / enhancement / good first issue…）、里程碑、Projects 看板。

**日常流程**：
1. **Issue 分诊（triage）**：读新 issue → 打标签、判断优先级、要求补充复现步骤；把适合新人的标成 "good first issue" 来吸引贡献者。[cite:4bf1db]
2. **处理 PR**：检查 CI 与评审状态 → 决定合并方式（merge / squash / rebase）→ 合并或关闭。
3. **治理**：维护路线图、处理争议、给协作者分配权限（读取 / 会审 / 写入 / 维护 / 管理员五级）。[cite:56c2ed]
4. **发布**：小项目里维护者兼任发布管理员，见第七节。

## 二、核心开发者（Committer / 核心团队）

**定位**：有 Write 权限的常驻成员，能直接在仓库里建分支。

**流程**：
1. 从 issue / 路线图领取任务。
2. 建功能分支：`git switch -c feat/xxx`（不要直接在 main 上改）。
3. 开发 + 本地测试 + 按规范提交。
4. push 分支 → 开 PR。因为有写权限，不需要 fork，直接在仓库内分支上开 PR 即可。[cite:9f4515]
5. 等 CI 通过 + 评审批准 → 合并 → 删分支。
6. 额外职责：评审别人的 PR、参与设计讨论、带新人。

## 三、外部贡献者（Contributor）——Fork & Pull 流程

**定位**：没有仓库写权限的人，开源项目里绝大多数贡献属于此类。在 PR 机制中，贡献者负责提出并实现改动。[cite:6240f2]

**标准流程**：
1. **先沟通再动手**：读 CONTRIBUTING 指南，找合适的 issue；新功能最好先在 issue 里讨论方案，避免白做。[cite:19bbaa]
2. **Fork**：在 GitHub 页面把仓库复刻到自己账号。[cite:b250ba]
3. **Clone + 配上游**：`git clone` 自己的 fork；`git remote add upstream <原仓库地址>`，之后常 `git fetch upstream` 保持同步。[cite:b250ba]
4. **建分支**：`git switch -c fix/xxx`；每个不相关的改动单独开分支，方便评审和回滚。[cite:9700fb]
5. **开发提交**：小步提交、信息清晰（很多项目要求祈使句、关联 issue 编号）。[cite:9ed595]
6. **推送并开 PR**：push 到自己 fork → 在 GitHub 创建 PR 指向原仓库 main 分支；描述写清"做了什么、为什么、怎么验证"，用 `Closes #15` 关联 issue；可勾选允许维护者修改你的分支。[cite:19bbaa][cite:f1914c] 想先要早期反馈可以开草稿 PR（草稿不能合并）。[cite:5fff7a]
7. **响应评审**：CI 挂了就修；评审意见**直接在原 PR 追加提交**，不要另开新 PR、不要 force push，方便评审者看到增量；与上游有冲突时 rebase 解决。[cite:19bbaa][cite:9ed595]
8. **合并后**：删分支、同步自己 fork 的 main。

## 四、评审者（Reviewer）

**定位**：对 PR 做质量把关，通常是维护者或资深贡献者。[cite:6240f2]

**流程**：
1. 收到评审请求（或主动认领）。
2. 读 PR 描述和 diff，必要时本地 checkout 跑一遍。
3. 逐行评论、提 suggestion、提问（可以评整份 PR，也可针对具体行）。[cite:9700fb]
4. 给结论：Comment（评论）/ Approve（批准）/ Request changes（要求修改）。
5. 作者修改后复审增量，满意则批准。
6. 关注点：正确性、测试覆盖、风格一致、向后兼容、安全、文档。

## 五、测试 / QA

- 维护测试用例和 CI 流水线（GitHub Actions：lint、单测、构建）。
- 对每个 PR：看 CI 结果，必要时拉分支做手动 / 回归测试，结论写回 PR。
- 发现 bug：按模板提 issue（复现步骤、环境、期望 vs 实际）。
- 发布前：对候选版本做验收测试。

## 六、文档 / 本地化贡献者

- 文档改动同样走"分支 → PR → 评审"，不搞特殊通道。
- 更新 README、API 文档、CHANGELOG。
- 翻译一般放独立目录，由对应语言的维护者评审。

## 七、发布管理员（Release Manager）

**流程**：
1. 确认 main 上该进的改动都已合并、没有进行中的 PR。[cite:28f346]
2. 按 **SemVer** 定版本号：不兼容改动升 MAJOR、新功能升 MINOR、修复升 PATCH。[cite:e5ef73]
3. 打 tag（如 `v1.2.0`）→ 创建 GitHub Release → 生成 / 整理 release notes 与 changelog。[cite:28f346]
4. 发布制品（npm / PyPI / Docker / 二进制等）。
5. 紧急修复：从对应 tag 拉 hotfix 分支 → 修复 → 发 PATCH 版本 → 合并回 main。
6. 很多项目用 semantic-release 一类工具自动化：根据 commit 信息算版本号、生成 changelog、发布；changelog 建议按 Keep a Changelog 规范写给人看。[cite:527dc3][cite:47e462]

## 八、安全响应人员

- 维护 SECURITY.md 私密披露流程。
- 通过 GitHub Security Advisories 私下修复、协调披露、申请 CVE（创建安全公告需要 Admin 权限）。[cite:3d1ecc]
- 用 Dependabot 跟进依赖漏洞。
- 注意 fork PR 的 CI 安全：来自 fork 的 workflow 以受限权限运行，维护者侧可用 `pull_request_target` 等机制安全处理。[cite:289e09]

## 九、普通用户 / 社区成员

- 提 issue（用模板、先搜重复）、参与 Discussions、反馈使用体验。
- 好的 feature request 要说清场景和动机，而不只是"求加功能"。[cite:219e5a]
- 可以点赞、参与投票，但不直接改代码。

## 十、自动化（CI/CD 与机器人）

- GitHub Actions：跑测试、lint、构建、部署、发布。
- 机器人：自动打标签、stale bot 关闭长期无响应的 issue、Dependabot 提依赖升级 PR。
- 它们相当于"没有情感的团队成员"，把大量评审前置工作（检查、格式、覆盖率）自动化掉。

## 把所有角色串起来：一条改动的完整生命周期

issue 提出 → 维护者分诊确认 → 贡献者认领 → fork / 建分支 → 开发提交 → 开 PR → CI 自动检查 → 评审者评审 → 贡献者按意见修改 → 维护者合并 → 进入 main → 发布管理员打包发版 → issue 自动关闭。

## 速查表

| 角色 | 典型权限 | 核心操作 | 主要产出 |
|---|---|---|---|
| 所有者 / 维护者 | Admin / Maintain | 治理、分诊、评审合并、发版 | 合并的代码、Release |
| 核心开发者 | Write | 建分支、开 PR、评审 | 代码、review |
| 外部贡献者 | Read（+ 自己的 fork） | fork、PR、按评审修改 | PR |
| 评审者 | Read / Write | review、approve / request changes | 评审意见 |
| 测试 / QA | Read / Write | 跑 CI、验收、提 bug | 测试报告、issue |
| 发布管理员 | Maintain / Admin | 定版本、打 tag、发 Release | 版本发布 |
| 安全响应 | Admin（+ 安全功能权限） | 处理漏洞、发安全公告 | 安全公告、补丁 |
| 用户 / 社区 | Read | issue、讨论、反馈 | 反馈 |

## 跨角色通用规范

不管什么身份，有几套"公共语言"是全项目共用的：

**1. 分支命名**
- `feat/xxx`、`fix/xxx`、`docs/xxx`、`chore/xxx`、`hotfix/xxx`
- 短而描述性，让协作者一眼看懂这条分支在做什么。[cite:9700fb]

**2. 提交信息（Commit Message）**
- Conventional Commits：`feat:` 新功能、`fix:` 修复、`docs:` 文档、`refactor:` 重构
- 好处：能自动生成 changelog、自动计算版本号（semantic-release 这类工具的前提）。[cite:527dc3]
- 正文写清"做了什么、为什么、怎么做的"，并关联 issue 编号。[cite:9ed595]

**3. 合并策略（维护者要做的选择）**

| 策略 | 效果 | 适用 |
|---|---|---|
| Merge commit | 保留完整分支历史和每个 commit | 需要审计追踪的大改动 |
| Squash merge | 把整个 PR 压成主干上一个 commit | 大多数功能分支，历史干净 |
| Rebase merge | 把 commit 逐个重放到主干，形成线性历史 | 想保留多个干净 commit 的功能分支 |

要求"线性历史"的仓库只能用 squash 或 rebase 合并；繁忙仓库还可以启用合并队列（merge queue），避免主干被并发的合并搞坏。[cite:a59f0f] 另外，rebase 适合功能分支，不建议用在两个长期共存的分支之间。[cite:29b3c5]

**4. 分支保护与门禁**
- 必需评审（如至少 1 人批准）+ 必需状态检查（CI 必须绿）+ 禁止直接 push / force push。[cite:f54e7e]
- 可选加强：要求 CODEOWNERS 审批、要求线性历史、需要合并队列。[cite:f54e7e][cite:a59f0f]

**5. 版本与发布规范**
- 版本号用 SemVer：`MAJOR.MINOR.PATCH`。[cite:e5ef73]
- 每个版本一个 tag + Release notes；changelog 按 Keep a Changelog 的风格写给"人"看。[cite:47e462]

## 不同规模项目的差异（角色会合并或拆分）

- **个人 / 小项目（1–3 人）**：所有角色由同一两人兼任；通常只保留"GitHub Flow + 可选的分支保护"，不需要 CODEOWNERS 和正式的发布管理员。
- **团队项目（10 人左右）**：拆分出维护者、评审者、QA；启用必需评审 + CI 门禁 + CODEOWNERS；发布走 tag + Release 流程。
- **大型开源项目**：角色最全——维护者团队、triage 团队、发布团队、安全团队、社区经理；配套 RFC 流程、CLA / DCO 签署、多版本维护分支、安全公告流程。

## 给不同身份的一句话建议

- **维护者**：把规则前置（分支保护 + CI + 模板），比事后救火省力得多。
- **贡献者**：先讨论后写码；PR 小而聚焦；保持原 PR 打开、增量提交。
- **评审者**：对事不对人，给可执行的修改建议（用 suggestion 直接改）。
- **发布管理员**：发布前跑一遍清单——合并确认 → 定版本号 → 打 tag → 写 notes → 发制品。

---

至此，从"仓库怎么建"到"每个角色每天做什么"再到"发布怎么收尾"就串完整了。如果你告诉我你的具体身份（比如"第一次给开源项目提 PR"或"要给自己团队搭一套流程"），我可以把对应部分展开成一份可勾选的实操清单或模板。