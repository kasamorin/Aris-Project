# 待办事项

> 排名不分先后

- [] Bug fix
- [] WebUI重整，分为Dashboard与WebChat
- [x] 宣布项目公开
- [] 基于MyGO框架的GUI
- [] 对于发行版进行软件包打包（GUI 之后；v1：进源只走 AUR 的 `aris-project`，deb 与 Gentoo ebuild 只挂 Release / 本地 overlay）
- [] .desktop文件（同样在GUI之后）
- [] Live2D 支持（v1 不做，GUI 之后）
- [] 记忆系统和角色系统
- [x] 迁移config至data
- [] 全新的备份系统
- [x] WebUI设置界面（单套列表 + section 分组 + 搜索；不拆简单 / 高级两套视图，2026-11-03 定）
- [p] 项目标准化（CI 已随 v0.4.5 落地；文档重整余下部分在 v1.x）
- [] 许可证合规（NOTICE + 第三方许可清单、发行物附 COPYING、WebUI 关于页源码链接）
- [] 文档重整（含两类当前缺失的文档：面向插件的**行为文档**、面向贡献者的**核心开发文档**——如何开发新模块 / 如何在现有模块上扩展。内容不止这些，具体范围到时再定；**动笔前先调研优秀文档架构**（如 Diátaxis、Write the Docs、成熟项目的 `docs/` 组织）并给出建议，再决定怎么写。v1 不做，随文档重构一起）
- [x] git中取消跟踪docs/archive
- [x] 全面取消多配置地点，配置完全归于data/config/*.toml（.env也迁移）
- [x] 密码和 api key 加密（已定不做：0600 权限 + 只存 key 名 + 展示脱敏）
- [] v1.0.0后续版本如果有破坏性更新，需支持老版本向新版本迁移（用户同意后）
- [] memory-lite和sqlite
- [] 给予用户更多可设置项（2026-11-11 定方向：直接给扁平配置键，不做预设 / 档位；人格与表达归角色提示词 `prompt.md`）
- [] 用户可设置项·记忆：配额 / 阈值 / 晋升窗口 / 人物卡上限 / 注入条数等仍写死的参数，逐个评估改成 `memory.toml` 的键
- [] 用户可设置项·平台行为：合并窗口、是否 @ / 引用、分段、回复前缀等目前只有一种做法的地方，评估哪些该给键
- [] 用户可设置项·模型与成本：输出预算、上下文长度、fallback 链、会话复用冷却等成本侧参数
- [] 插件系统（参考Astrbot,由于我们使用cmcb但别人不一定，而且不一定所有人都愿意用cmcb,因此需要提供兼容层）→ **v1.1**（v1.0 不做，草案在 `docs/process/v1.1-plugin-system.md`）
- [] autorun自动任务
- [] 消息平台连接（v1 做 Matrix；OneBot 暂不做）
- [] 多模态、全模态模型支持（v1.x 的「多模态全双工」见本文件第 30 条）
- [] 决策模型支持（自主回复 / 自主操作门控；不做主模型兜底，密集消息攒批）
- [] v1.x：借鉴 SurfCore（Mieksido/surfcore，v1.0 之后到 v2 之前，不进 v1.0 核心决策）
- [] v1.x：主管理员账户（人格化管理员提示注入）
- [] v1.x 评估：生活化主动联系（状态/日程/关系 → 行为候选；v1.0 的主动联系只走 autorun + 决策模型）
- [] v1.x：群聊全量历史持久化 + 工具查询
- [] v1.x 参考：重看「我会永远陪着你」插件（v7.1.3，已 clone 到 `data/temp/plugin-private-companion`）——上轮只取了 6 条，记忆侧不采纳；消息投递 / autorun / 提醒还没细看
- [] v1.x 候选：回复拆多条（模型分段）、情绪/状态记忆
- [] v1.x：插件 LLM/结果钩子扩到 AstrBot 全量（on_waiting、工具前后、agent 开始/结束、消息发送后等）
- [] v1.x：知识库 rerank（成本敏感，v1 只留接口默认关）
- [] v1.1：文档站（VitePress）+ 域名（v1.0 不做，§4.16）
- [] v1.1：aarch64 / 交叉编译、deb / AppImage / Windows 打包
- [p] 制作图标与更改项目定义
- [x] 开发流程文档（从创建分支到更新版本）
- [] 制作宣传视频
- [] 统一连接路径&接入点
- [] LLM连接与提供商完全重构
- [x] LLM fallback 重定（默认模型必配 → 出错发占位 → 同模型同提供方重试一次 → 全局一条链；不竞速、不粘滞，2026-11-08）
- [] 知识库分组
- [] 日志优化（可读性与检索）
- [] 加强路径守卫测试（只白名单 `paths.py`；覆盖 f-string / 字符串拼接；扫描 templates 与脚本）
- [] 知识库二期
- [] 知识库-lite（不依赖 embedding 的纯关键词版；方案未定，v1 不做）
- [] 从zip导入skills
- [x] 切换项目许可证为AGPL
- [x] 增加只在develop发布的alpha-渠道
- [] 彩蛋
- [p] 模块开关&工具开关
- [] 取消models.dev获取元信息，直接从提供商获取（以及参考astrbot）
- [x] 将项目名正式修改为Aris Project(与Project AIRI作出区别),并将项目移入Github组织
- [x] 定v1大版本开发代号为"跨越"("Cross")


---

## 备注（2026-10-28 定）

> 上方条目保持原样，这里只记阶段划分与已定决策。

### 两阶段
- **阶段一 beta-v0.4.3 → 正式 v0.4.4（地基版）**：路径与配置收口、CLI 事实入口、模块开关、退休机制退役、工程小件。不承诺旧数据 / 旧配置兼容。
- **阶段二 alpha-v0.4.6 → 正式 v1.0.0**：项目标准化、备份系统、WebUI 重整与设置页、统一连接路径、LLM 提供商重构、memory / 角色、打包与 GUI、公开。

> 阶段一（v0.4.4）已完成；阶段二进行中，施工入口见 `docs/process/v1.0.0-prep.md` 与 `docs/process/v1/`。

### v0.4.4 范围（W1–W6）
1. **W1 统一数据目录**：新增 `paths.py`；解析顺序 `ARIS_DATA_DIR` > 开发树 `./data` > 安装 `~/.project-aris`（2026-11-06 起安装态改为 `~/.aris-project`，见下文「安装态数据目录」）；清除硬编码；加守卫测试；`aris info` 打印解析结果。
2. **W2 配置收口**：`data/config/` 为运行时权威，模板随包（`src/aris/seed/config/`）首次幂等播种；**`.env` 不搬家，改为 TOML 并入 `data/config/`**（不再保留 `.env`；拆 `settings.toml` + `secrets.toml`，后者 0600；加载器改为「先读 TOML，再把 key 字段 setdefault 进 `os.environ`」以保住 provider 的 `api_key_env` 链路）；删除 `.env.example`，变量清单由 `aris config env` 只读展示；**不做自动迁移**（v1.0 前不承诺兼容）；同批改 `README.md` 快速开始——去掉 `cp`，目标形态是 `uv sync && uv run aris serve` 一条命令。
3. **W3 CLI 事实入口**：`aris info` / `aris config path|list|show|validate`（只读，不写配置）/ `aris modules list|status|enable|disable`；模块开关 7 个（store / knowledge / mcp / behavior / webui / character / voice），`modules.toml` 统一，`knowledge.toml.enabled` 并入；关闭时日志报错、不退出程序。
4. **W4 架构原则落地**：`serve` 只做组装与启动，**任何模块不得 import serve**；`get_runtime` 等运行时对象移到 `behavior/runtime.py`；加守卫测试。
5. **W5 LLM 退休机制退役**：`fetch` 只把同步后消失的模型写入 `data/state/llm-list-missing.json`，`aris llm missing list` 与 WebUI 只读查看。
6. **W6 工程小件**：AGPL-3.0-or-later、alpha 渠道（占号）、`git rm -r --cached docs/archive`、`docs/dev-flow.md`（人类文档）、`CLAUDE.md -> AGENTS.md` 软链。

### 已消歧
- 模块开关按模块粒度；工具开关 v1.0 再做（`ToolSpec.enabled` / `owner` 地基已存在）。
- 用户主动关闭的模块被依赖时：**记 error 日志、跳过依赖方，不退出程序**；`required` 只保留 `store.db`。
- CLI 不负责配置写入（查看 / 校验即可，编辑交给编辑器）。
- alpha tag 形如 `alpha-vX.Y.Z`，只在 develop，**占用数字线**。
- 旧配置 / 旧 `.env` 的迁移与兼容性：v1.0+ 再做。
- `.env` 的去向是**转成 TOML 并入 `data/config/`**，不是原样搬进 `data/`；拆分方案已定：`settings.toml`（启动参数）+ `secrets.toml`（密钥，0600）。
- 图标、CI、项目标准化、彩蛋、备份、公开：v1.0 或之后。

### 仓库形态（2026-10-29 定）
- **单仓多构建单元**：`src/aris/` 后端；`gui/` 桌面 / 前端（独立 `package.json` 与 lock）；`docs/` 文档站（VitePress，独立 lock）；`packaging/` 发行配方。GUI、文档站都不拆仓库。
- **构建隔离**：普通 `uv sync` 不装 Node、不构建 GUI；仅发版时设 `ARIS_BUILD_GUI=1`，通过构建钩子把 `gui/dist` 打进发行物（参照 AstrBot 的 dashboard）。
- **发行包**：包名 `aris-project`，两个命令 `arisp`（后端）/ `arisp-gui`（桌面壳，依赖后端）；
  `arisp` 入口显式注入 `ARIS_DATA_DIR`。同仓、同 CI、共用 `__version__`。
  安装布局与首启流程见 `v1.0.0-prep.md` §4.15 与 `docs/process/v1/S13-packaging.md`。
- **何时升级 workspace**：GUI 拆成多个 JS 包、或后端确需拆 `core` / `store` 时，改用 uv workspace / pnpm workspace，仍是单仓，不拆多仓。
- **仓库体积**：大资产（图标源文件、宣传视频、截图）走 release 附件，不进 git；`docs/archive` 按计划取消跟踪。

### 安装态数据目录（2026-11-06 定）
- **包安装**用 `~/.aris-project`；**源码树**用项目根下的 `data/`。
- 解析顺序 `ARIS_DATA_DIR` > 开发树 `./data` > `~/.aris-project`；不做 XDG、不上 Flatpak
  （参考：AstrBot 桌面包用 `~/.astrbot`）。
- **本项目不上 Flatpak**（开发者 2026-10-30 明确），所以 XDG 的沙箱优势不成立，主要看备份与习惯。
- 决定后只需改 `paths.py` 一处 + `tests/test_paths.py` + 施工文档。

### v0.4.4 施工进度（已发布）
- W1–W6 已完成，`v0.4.4` 于 2026-10-30 发布（施工文档已归档）。
- 技术债（建议项，本阶段未做）：`cli.py` 拆包；模块开关测试的总线快照隔离（3.5）。

## v0.4.5 标准化（v1.0 开发正式启动前必须完成）

> 目标：让项目看起来与维护方式符合「标准开源项目」。CI/CD 与 i18n 不在本阶段（v1 期间做）。

### A. 提交记录（head / body / footer）
- [x] 规则写清：AGENTS.md §8、docs/dev-flow.md §4（footer：Refs / Closes / BREAKING CHANGE / Co-authored-by）
- [x] commit-msg hook 增加 footer token 白名单校验（仅在有 footer 时校验，避免误伤）
- [x] 新提交按规则带 footer（有可关联 issue/PR 时；没有可关联内容不硬凑）

### B. 文档
- [x] changelogs（README + 0.4.4 + unreleased）
- [ ] CONTRIBUTING.md / SECURITY.md **保留 0 字节占位**，v1 P7 按「面向人类、不引用 AI 文档」重写正文
- [ ] 用户文档体系：docs/zh（与 docs/en）→ **v1.1 随文档站一起做**
- [x] README 升级：简介、快速开始、许可证与徽章（v0.4.5）；截图与文档索引 → v1.1
- [x] forAiDoc 清理：skills-backup、discuss-2026-09-28.md、Project-Aris.drawy、PLUGIN、DOCS-SITE、
      SECURITY-AND-REFACTOR-PLAN、referenceDocumentation、v0.4.4 施工文档 → `docs/archive/`（本机保留、不再跟踪）
- [x] 0.4.5.1：归档 `V1.0-PLAN.md`，同步 AGENTS §10 / §12；`WEB-SEARCH` / `EMBEDDING` /
      `TUI-问题修复` 的重写 / 归档要求写进 `docs/process/v1.0.0-prep.md` §10.1

### C. 项目结构
- [x] datadir.py 并入 paths.py（数据目录只有一处来源）
- [x] 顶层基础设施收进 `src/aris/infra/`：paths / settings（原 config）/ toml（原 cfgtoml）/ modules / logging / branding
- [ ] tests/ 按模块分组或加 README；测试支持代码收口到 tests/support → **v1 P7**
- [x] docs/ 目录边界：`forAiDoc`（AI 契约）/ `process`（阶段过程）/ `archive`（本机存档，不随仓库）；
      用户/开发文档语言结构随 v1 文档站一起规范（docs/zh、docs/en）
- [x] oldWish 迁出主仓库：独立仓库在 `data/temp/oldWish`（带历史），主仓库与 fork 已删除该分支

### D. CI/CD（v1 期间）
- [x] CI：PR 与 develop / main 推送跑 ruff / mypy / pytest；发版 PR 加真库 + embedding；alpha tag 跑 smoke（v0.4.5）
- [x] 0.4.5.1：修 `check` 的 PG 探针假失败；`integration` 用 `ARIS_PG_SOURCE=project` 强制便携 PG
- [ ] 打包（wheel + 可选 GUI）后加构建 / release 产物步骤
- [ ] CD：tag 触发构建与发布（等发行包形态稳定）

### E. i18n（v1 期间）
- [ ] 用户可见文案集中到常量 / 资源（先做后端，不引框架）→ **v1 P7**
- [ ] 至少支持中 / 英；后续再评估其它语言 → **v1 P7**

### v0.4.5 施工进度（已发布）

- 2026-11-01 发布 `v0.4.5`（tag `v0.4.5`）：W1 变更记录、W2 CI 分档、W3 发版脚本、W4 文档与合规。
- 发版时 `main` 上还没有 workflow，首次 release PR 走了 bypass 合并（bootstrap）；此后按正常 auto-merge。
- 遗留：`check` 的 PG 探针假失败、`integration` 选中系统 PG 缺 pgvector——均在 0.4.5.1 修复。
- 本版不做：`session_cooldown_days`（代码里尚无消费方，留到 v1 会话落地）、GitHub Release、打包、文档站、i18n。

### v0.4.5.1 收尾（2026-11-03）

- [x] 修 `check`：`test_probe_runnable_real_binary` 的跳过条件移到用例内（模块级 `skipif` 早于 fixture）
- [x] 修 `integration`：新增 `ARIS_PG_SOURCE=auto|project|system`，CI 设 `project` 强制走 `data/pg`
- [x] `docs/dev-flow.md`：修正 fork PR workflow bootstrap 的错误陈述；`gh` 命令改为网页优先
- [x] `PROGRESS.md`：刷新到 0.4.5 / 0.4.5.1
- [x] `todolist.md`：结算 v0.4.5（文档体系与 i18n 移交 v1.x）
- [x] `V1.0-PLAN.md` 归档，AGENTS §10 / §12 同步
- [ ] 发版：`bash scripts/release.sh 0.4.5.1` → 归档 `[0.4.5]`、封 `[0.4.5.1]` → PR → tag

- v1.0 决策收敛（2026-11-03）：记忆系统对外名 APEMS、插件推迟 v1.1、决策模型去掉 `main_llm`、
  记忆晋升与共享额度、配置档 `serve`/`webui` 不随档等，详见 `docs/process/v1.0.0-prep.md`。

---

## 2026-11-08 新记待办与问题

> 开发者口述后记下，未排序、未定归属版本；待商议时再落成正式决策。

1. **LLM 错误兜底文案的平台适配**：现有 `settings.llm_error_message`（默认
   `Someone tell Morin there's some problem with my AI.`）已覆盖 LLM 输出错误 / 超时，
   并作为 `StreamDelta` 返回；S9 消息平台需要把这条文案也发出去。文案可自定义；只针对
   **LLM 输出相关错误**，不是任意异常。基本已完善，只剩平台侧接线与配置元数据确认。
2. **记忆原文存储**：已确认**原文全量保留 + 向量化**，`raw` 检索走向量 + 关键词混合
   （禁止裸 LIKE）；`MEMORY.md` 的设计正确，代码尚未实现（`src/aris/memory/` 仍是 stub）。
   检索参数（RRF k / λ / MMR）做成配置项，但设置页默认隐藏，需打开「高级检索参数」并确认风险提示。
3. **多角色同时运行**：**v1 做**。每个角色独立会话 + 串行队列，文本可同时处理；
   音频独立 TTS 队列 + 全局混音，**默认允许重叠、不 ducking**；角色间对话互相注入发言；
   每角色可绑自己的 LLM 提供商 / 模型。详见 `docs/process/v1.0.0-prep.md` §4.8。
5. **Live2D**：远景，已有条目（v1 不做，GUI 之后）。
6. **core 模块大优化**：**v1 做**，范围已定：LLM 引擎拆分、工具循环可控性（可中断 / 统一超时 /
   错误归一）、工具循环并行调用；fallback 最终口径另记（第 15 条）。见 `v1.0.0-prep.md` §3.9。
7. **`cli.py` 拆分**：**v1 做**，已有技术债记录（§5.2 填缝车道）。
8. **arisdk**：**v1.x**。思路参考 neuro-sdk：WebSocket + 类型化 action 协议（Context / Registered actions /
   Forced actions），让外部程序 / 游戏声明动作、Aris 返回动作名 + JSON。
9. **选择性回答 + 非逐条请求**：选择性回答已有设计（§4.4 门控档位
   `only_trigger` / `probability` / `decision_batch` / `always`）；「非逐条请求」**已定**：
   入站待处理缓冲按 `chat.toml` 的 `batch_window`（默认 1.5 s）/ `batch_max_messages`（默认 8 条）/
   `batch_max_tokens`（默认 4000）合批，`buffer_scope` 默认 `per_chat`、可切 `session`，
   不依赖决策模型开启。
10. **日常 ftf 对话**：**v1.x**。参考 AstrBot 插件或 AIRI 的做法；与语音链路耦合。
11. **游戏接入**：**v1.x 以后**。可参考 neuro-sdk 的类型化 action 协议。
12. **知识库（S12）**：按库配置 v1 **不做**，全局一套（`meta` 空着）；上传任务保持内存态，
    补 `content_hash` 全局去重（不同文件名同内容直接 skipped）。
13. **skills 导入（S12）**：同名拒绝、要更新先删；体积上限做成 `skills.toml [import]` 配置项
    （默认 10 MB / 500 条 / 2 MB，按解压后算）；导入 / 删除后标 `prompt_dirty`、下一轮重建
    system prompt；**不做**技能级开关。
14. **会话生命周期**：`/#new` = 上下文到阈值时的行为（事件总结 + compact 两次调用），
    不是清空；新增 `/#new-s` 强制开新会话。工具开关 / 技能变更 / 模型绑定统一标 `prompt_dirty`，
    下一轮重建 `history[0]`（一次性 cache miss）。
15. **fallback 最终口径**：**已定（2026-11-08）**——默认模型必配；出错先发 `llm_error_message`
    占位 → 同模型同提供方重试一次 → 全局一条 `fallback_models` 链逐个尝试 → 全失败 / 无链就停在
    占位等下一次请求；不粘滞、不竞速、已输出内容后不切换。删除「同模型换提供方」与每模型自带链。
16. **mypy 范围**：v1 维持 `core` + `store`；扩不扩按长期收益评估，v1.x 再定。
17. **tests 分组**：按模块分 `tests/<module>/`，`tests/support/` 留共享 mock，跨模块用例放
    `tests/integration/`；S14 前完成。
18. **GUI 深链**：v1 **不做**（`.desktop` 不注册 handler）；将来若做，scheme 用 `aris-project://`。
    托盘 / 通知 / 自动更新 / 全局快捷键 v1.x。
19. **`except Exception`**：继续用 ruff BLE001，降级日志固定带异常类型与上下文，不加自定义 lint。
20. **CONTRIBUTING / SECURITY**：留 S14 发布前收尾，正文程度到时再定。

## 2026-11-10 新记：笔记系统与人物卡

21. **删除测试 note skill**：`src/aris/behavior/skills/note/` 是早期测试直接进库的，**v1 前删掉**；
    它写的 `data/notes/` 是运行时数据，先确认有没有用户内容，再决定是否清理。
22. **角色笔记系统（已定稿；2026-11-13 补时间戳）**：每角色（`cid`）一份，存 `data/characters/<cid>/notes.sqlite`
    （独立 SQLite，**不进记忆库**，切 full / lite / 换库都不丢，随角色目录备份与软删）；
    做成记忆系统里的**常驻工具**（不是 skill）：`memory_note_write` / `memory_note_read` /
    `memory_note_search` / `memory_note_delete`；一条笔记 = **一段纯文本，第一行即标题**（不单设标题字段）；
    检索用 `content LIKE`（**不用 FTS5 trigram**，也不做向量——500 条 / 2 MB 上全文索引无收益）；
    上限默认 **500 条 / 单条 4000 字**（进 `memory.toml [notes]`，可配，超限拒绝不截断）；
    v1 **不自动注入**，只由模型按需调用；WebUI + CLI 都提供管理入口。
    **时间字段（2026-11-13 定）**：加 `created_at` / `updated_at`（ISO8601 TEXT），供大会话视图按段归位；
    但**工具默认不返回时间**，模型明确要看时间时才给（WebUI / CLI 列表照常显示）。
23. **笔记重要度（v1.x 再议）**：是否给笔记加重要度排序 / 置顶 / 自动注入，先留待办，不进 v1。
24. **人物卡重要度与固定（已定稿）**：`memory_entities.importance`（0~100，**每张卡都有**，模型可标、
    用户可改）；初始分按来源：主人 80 / 有直接对话 50 / 只有事实 30；`importance_source` 只显示「谁设的」，
    **不做写入保护**。进上下文 = 当前发言人完整卡 + 固定卡 **≤3** + 重要度前 **3** 的精简卡，总卡数 ≤6，
    按 `entity_id` 去重、顺序稳定（保 KV cache）；**主人保底前 3**（选卡时先占一个名额，不把分数钉成 100）。
    前 15 名只打「重要角色」标签（**不改变列表排序**），另在提示里给名字索引，并在 `memory_find_person`
    时加权（**不改普通 `memory_search` 排序**）；抽取时能匹配前 15 别名的优先归并，减少裂卡。
25. **人物卡用户可改（已定稿）**：v1 明确「人物卡全部可编辑」——印象 / 重要度 / 固定位 / 槽位事实，
    用户 WebUI + CLI 都能改；模型可改印象与重要度。
28. **人物卡读写工具补齐**：新增 `memory_find_person(name, limit=5)`（补上「写完看不到、所以改不了」的闭环，
    返回 `entity_id` / 重要度 / 槽位 / 印象 / 最近互动，前 15 加权）与 `memory_update_fact(fact_id, ...)`
    （只改既有事实，新事实仍只由抽取产生；更正 = 新行 + 旧行标 `superseded`，返回新 `fact_id`；
    记 `updated_by`）。防编造：工具描述写「不确定就不要写」，注入人物块注明「过往记录，可能过时，
    以对方当前所说为准」。
26. **清理 SnowLuma 引用**：SnowLuma 已停，文档中相关描述（`v1.0.0-prep` §4.4 / §4.22）后续统一删；
    现在先别删，留待办。
27. **人物卡防污染（已定稿）**：不做 stub / active / archived 状态机；**卡是派生的**——纯提及只建身份
    （`memory_entities`），**有事实 或 有直接对话**才算有卡，由查询现算、不存字段。列表按重要度降序，
    低于阈值（默认 20，可配）折叠进「其他」组，可展开；这是视图，不是数据库状态。
29. **`aris-icon.png` 是开发者设计的项目图标**（2000×2000，黑体 `ARIS` + 左红右米色竖分，上下大留白）。
    **2026-11-10 定**：它是 **wordmark / 封面型**，不是应用图标——16~48px 下四个字母糊成一团，
    方形应用图标与 favicon 需要另做紧凑标记（单字母 `A` / 红米分色方块，由开发者设计）。
    - 母版**暂时留在仓库根目录**，不改名、不挪位置；
    - **不做 README 头图**：头图要长方形、更简约，另做一张；
    - **favicon + 应用图标集**（`icon-{16..512}.png` / `favicon.ico` / `.desktop` 的 `Icon=`）随 S13
      品牌资源同批做；派生图平铺进 `src/aris/webui/static/`，避免改 `pyproject.toml` 的 package-data。
30. **多模态全双工模型支持（v1.x）**：v1.0 的语音链路留到语音批次，按「STT → LLM → TTS」半双工作为
    默认形态；v1.x 再评估全双工（边说边听、可打断）的多模态模型接入与调度——模型直接收发音频
    内容块，边说边听，不再经过独立 STT / TTS 两段。
    两条路线**长期并存**，不是替代关系：①**独立 STT / TTS 管线必须做**——不是所有模型都支持多模态，
       纯文本模型只能走这条；②不是所有模型都支持原生全双工，届时需要**手动模拟全双工**
       （分段送音频 + 句子边界插话 + 可打断的 TTS 队列），`voice` 模块按此预留调度能力。
31. **v1.x：修复阈值总结导致的对话不连贯**：上下文到阈值时 compact 把旧历史换成摘要，语感会断；
    v1.0 接受这个代价，v1.x 再找更好的方案（例如滚动摘要、分层摘要、只压工具输出等）。
32. **行为文档（v1.x，人类向）**：每个模块「做什么、暴露什么服务 / 事件、何时触发、有什么副作用」，
    与 AI 向的 `docs/forAiDoc/` 契约文档分开；写作规范参考阮一峰《中文技术文档写作规范》
    （短句、先结论、少用被动、术语一致）。现有相关内容只在 `docs/process/v1.1-plugin-system.md`
    的「文档分三层」里提过一句，属于插件场景。
33. **v1.x：维护调用失败的复杂回落**：v1.0 的两次调用都走正常 LLM 重试 / fallback，全失败就整轮失败
    （不 compact、不回复）；v1.x 再考虑「只 compact 不抽取」「标记待补、稍后从原文补抽」
    「摘要失败退回机械摘要 / 直接截断尾部」等更平滑的降级。
34. **特殊人物卡替代角色提示词（v1.x 实验性功能）**：给每个角色加一张**专用人物卡**，比普通人物卡更详细
    （性格 / 说话方式 / 喜好 / 经历 / 关系态度等字段化），并**开放部分字段允许角色自己改**，
    以此替代静态的 `prompt.md` 人设正文。为省成本：**不因改动重写 system prompt**（保 KV / prompt cache），
    改过的字段在上下文**末尾再注入一遍**（增量提示），让模型注意到变化。
    - **已定（2026-11-10）**：开启该功能后，这张卡的内容**直接取代 `prompt.md`**，不是叠加；
      关闭则回落到 `prompt.md`。v1 的「`prompt.md` 放完整人设正文」契约不变，只是 v1.x 多一条替代通路；
    - **待议**：允许改哪些字段、有没有改动上限 / 频率限制 / 回滚与版本历史（人设漂移是真实风险）；
    - ~~**待议**：卡片存 PG 还是角色目录~~ **已定（2026-11-13）：存 PG**——「记住别人」本来就是记忆的一部分，
      人物卡就在 `memory_entities` / `memory_facts`（以 `docs/forAiDoc/MEMORY.md` 为准）；
      换机靠全量备份 `data/`（含 `pgdata/`），**不做「换库不丢」**；角色笔记仍另走
      `data/characters/<cid>/notes.sqlite`，两者不混。
    - **2026-11-13 复看（未定，v1.x 开工前先定形态）**：本条与现有记忆体系大面积重叠——喜好 / 关系态度
      已有 `memory_facts`、经历已有事件、自我印象已有 `impression`；再新造卡片会成为第三套人设真相。
      且「卡片整体取代 `prompt.md`」与「字段可自改」冲突：身份 / 边界会跟着变成可改的。
      开工前先回答「是否复用记忆 + 只开自我写入」，别直接照本条开工。

## 2026-11-13 新记：待商议

35. **[x] 大会话 & 历史界面（2026-11-13 已定）**：独立 `/history` 页，去掉侧栏后左 1/3 列表 + 右 2/3 详情，
    右上消息、右下事件与笔记（只有大会话视图有下半），手机端竖排；左栏顶部角色下拉 +「小会话 | 大会话」切换；
    keyset 分页（列表 30 / 消息 50 / DOM 300），只读；大会话按最大间隔 < 2h 递归切分、按需重算；
    assistant 行带 `tools` 标签，不做关键词检索，深链留 v1.x。契约见 `docs/process/v1.0.0-prep.md` §4.26。
36. **开发细节补全（进行中：全局总则已定 2026-11-13）**：开发时一定会遇到、但现在文档里没写的细节——
    重试边界、并发与串行队列、幂等与去重、状态持久化位置、失败降级、日志字段、迁移回滚、
    前端交互与空态 / 错误态等。逐模块过一遍，补进对应契约文档或施工文档，不留在口头。
    **第一批（全局七条）已定**：重试 / 超时 / 幂等 / 日志 / 状态文件 / CLI 退出码 / 迁移口径，
    见 `docs/process/v1.0.0-prep.md` §4.27。**剩下**：前端空态 / 错误态 / 加载态、长任务进度、
    SSE 断线重连、chat 轮次失败恢复、并发与背压，以及各模块特有细节。
37. **消除歧义 & 消除自相矛盾**：全仓文档交叉检查（AGENTS / `docs/forAiDoc/` / `docs/process/` /
    `PROGRESS.md` / `todolist.md`）：同一事实只留一处，过期结论删掉或改成指针；
    冲突按 AGENTS 的权威顺序裁决。**发现冲突先记录，不擅自删不认识的改动。**
38. **LLM 连接架构重整商讨**：provider / model / 统一连接页 / fallback 链 / 决策模型之间的关系再梳理一遍，
    先出架构方案与迁移步骤，拍板后再动 S7 相关代码。
39. **[p] 消息平台首个实现改为 Matrix**：v1 只做 Matrix，平台抽象层保留；**OneBot v1 不做**（NapCat 停更、
    SnowLuma 转私有，协议端生态不稳定），将来若做目标是 OneBot v11（v12 仍在开发）。
    已定：密码 + token 登录（不做 OAuth2 / refresh token）、密码与 token 都存 `secrets.toml`（token 失效自动重登、
    沿用 device_id）、device_id 由 homeserver 生成且不轮换、别名默认不拼完整 id（用户可手填短别名）、
    自动进房 / E2EE 默认关、离线回放 60 分钟 / 每房间 50 条、入站图片上限 20 MB（均可配）、
    适配器目录 `platforms/adapters/`。
    余下：落文档收尾 + S9 施工。
40. **[x] 自动检测新版本（2026-11-13 已定，进 v1.0）**：只查 GitHub Releases 的 `latest`（即正式版，
    天然不含 beta / alpha）；提示 = 侧栏品牌区一行 + 关于页一行，**点版本号那一行就是手动检查**；
    CLI 不加入口（源码用户 `git pull`、包用户走包管理器）；`update.toml` 的 `mode = auto|manual|off`
    + `interval_hours`；失败静默、可按版本忽略。契约见 `docs/process/v1.0.0-prep.md` §4.25。
41. **[x] 笔记简化（2026-11-13 已定）**：砍三样——① **标题字段**：一条笔记 = 一段纯文本，**第一行即标题**，
    工具描述里写一句即可；② **FTS5 + trigram**：改 `content LIKE` 全表扫（2 MB 量级毫秒级），不建虚表与触发器；
    ③ 冗余 `cid` 列（库文件路径已编码）。保留：每角色独立 `notes.sqlite`、**4 个常驻工具**、
    上下限 **500 / 4000 字可配**、`created_at` / `updated_at`（工具默认不返回时间）。
    契约见 `docs/process/v1.0.0-prep.md` §4.7。

## 2026-11-13 新记：DeepSeek API 适配器（**全部留 v1.x**，2026-11-13 定）

> v1.0 只保持现有 DeepSeek chat 兼容接入，**Search 引擎、全家桶、平台 API 一律不动**。
> 下面三条是已按官方文档核实过的事实，留作 v1.x 开工依据，不要在 v1.0 期间开工。

42. **[v1.x] DeepSeek 联网搜索 API 适配器**：DeepSeek 有**独立的** Search / Fetch JSON API，可直接进搜索引擎池
    （`behavior/search/`，现有 Bing 直连 / Tavily / Exa）。**已按官方文档核实（2026-11-13）**：
    - 端点 `POST https://api.deepseek.com/v1/tools/search`（`query` 1~128 字、`count` 1~50 默认 10、
      `need_content` 默认 false、可选 `ori_question` / `localization`）；`POST /v1/tools/fetch`
      （`url` ≤ 8192，返回 `title` + Markdown 正文）。Bearer 鉴权，与 chat 共用同一 API Key。
    - 返回 `results[]`：`rerank_score`（0~3，≥ 1.5 为优质）/ `title` / `url` / `snippet` / `summary` /
      `content` / `site_name` / `site_icon` / `date` / `authority`（0~4，-1 未知）。
    - 计费**只算成功请求**（Search 结果非空、Fetch 拿到正文）：每千次 5 元；QPS 按账号算，
      Search 100 / Fetch 25，与用哪个 Key 无关。
    - **别和「联网工具」混**：`deepseek_web_search` / `deepseek_read_url` 是 chat 请求里的服务端工具，
      结果以内容块回传、要原样带回下一轮；引擎池接的是上面两个独立端点。独立 Search 暂不支持图片搜索。
    - 落地：新增一个引擎（Key 复用 `DEEPSEEK_API_KEY`），默认是否进池 / 优先级 / Fetch 是否兼作「读链接」
      随实现定；整页正文要截断，别把整页塞进上下文。
43. **[v1.x] DeepSeek 对话应用 API（官方「全家桶」）适配**：指官方「构建 Chatbot」那套能力
    （`/zh-cn/guides/build_a_chatbot`），**不是**把所有 REST 端点接一遍。清单（2026-11-13 核实）：
    联网搜索、深度思考搜索、文件输入（PDF / Word / PPT / 图片的文本提取或图文混排解析）、阅读链接、
    模型内容安全、用户元信息标记、会话标题、朗读回答（TTS）、语音输入（ASR）。
    - 三种协议都提供：Chat Completions `POST /chat/completions`、Responses `POST /responses`、
      Anthropic Messages `POST /anthropic/v1/messages`；官方要求用 `deepseek-flash`。
    - 联网工具是**服务端 tool**：请求里声明 `deepseek_web_search` / `deepseek_read_url`，结果以
      `server_tool_use` + `web_search_tool_result` / `web_fetch_tool_result` 内容块返回，下一轮原样回传。
      与 #42 的独立 Search / Fetch 是两条路，别混。
    - 开了联网工具 / `safety_check=high` / `title` 后，temperature、top_p、stop、seed 等由服务端接管；
      三种协议被忽略的参数清单不同，以官方表为准。
    - 对 Aris 的映射：联网工具会绑死 DeepSeek 且要回传结果块，破坏自有引擎池抽象 → 仍走 #42；
      文件输入涉及隐私与计费，知识库继续本地摄入；`safety_check` / `title` / 用户元信息个人项目用不上；
      TTS / ASR 留语音批次评估（TTS 可作 Edge TTS 后备，ASR 进 STT 候选）。
    - 结论：**v1.0 不接这套**；Chat Completions 本来就支持，另两种协议不必为它去适配。
44. **[v1.x] DeepSeek 平台 API（不属于「全家桶」）**：`GET /models`、`GET /user/balance`、
    FIM `POST /beta/completions`（Beta，仅非思考模式）、Files（上传 / 列出 / 查询 / 删除）、
    OCR `POST /v1/tools/ocr`。v1.x 先做 `GET /models`（补提供商管理的 fetch）与余额展示；
    FIM / Files / OCR 不进当前链路。
    **已核实（2026-11-13，官方 Models & Pricing）**：现行模型只有 `deepseek-flash`（V4.1-Flash-1017）
    与 `deepseek-v4-pro`（V4-Pro-0813），均 1M 上下文 / 384K 输出；`deepseek-flash` 支持 Vision。
    旧名 `deepseek-v4-flash` / `deepseek-v4-flash-vision-exp` **仍被接受但模型已下线**，请求由
    V4.1-Flash 承接、按 Flash 价计费。**种子已改为** `deepseek-flash` 且 `default_model` **留空**
    （运行期按提供方顺序取第一个可用模型）。
