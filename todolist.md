# 待办事项

> 排名不分先后

- [] Bug fix
- [] WebUI重整，分为Dashboard与WebChat
- [x] 宣布项目公开
- [] 基于MyGO框架的GUI
- [] 对于发行版进行软件包打包（GUI）之后
- [] .desktop文件（同样在GUI之后）
- [] Live2D 支持（v1 不做，GUI 之后）
- [] 记忆系统和角色系统
- [x] 迁移config至data
- [] 全新的备份系统
- [x] WebUI设置界面（单套列表 + section 分组 + 搜索；不拆简单 / 高级两套视图，2026-11-03 定）
- [p] 项目标准化（CI 已随 v0.4.5 落地；文档重整余下部分在 v1.x）
- [] 许可证合规（NOTICE + 第三方许可清单、发行物附 COPYING、WebUI 关于页源码链接）
- [] 文档重整
- [x] git中取消跟踪docs/archive
- [x] 全面取消多配置地点，配置完全归于data/config/*.toml（.env也迁移）
- [x] 密码和 api key 加密（已定不做：0600 权限 + 只存 key 名 + 展示脱敏）
- [] v1.0.0后续版本如果有破坏性更新，需支持老版本向新版本迁移（用户同意后）
- [] memory-lite和sqlite
- [] 给予用户更多可设置项
- [] 插件系统（参考Astrbot,由于我们使用cmcb但别人不一定，而且不一定所有人都愿意用cmcb,因此需要提供兼容层）→ **v1.1**（v1.0 不做，草案在 `docs/process/v1.1-plugin-system.md`）
- [] autorun自动任务
- [] 消息平台连接（做的话先做OneBot v11）
- [] 多模态、全模态模型支持
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
- **发行包**：包名 `ariscore`，两个命令 `arisp`（后端）/ `arisp-gui`（桌面壳，依赖后端）；
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
   平台侧按 `batch_window`（默认 1.5 s）/ `batch_max`（默认 8 条）合并成一次主模型请求，
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
18. **GUI 深链**：v1 只做 `ariscore://`（`.desktop` 注册 handler）；托盘 / 通知 / 自动更新 / 全局快捷键 v1.x。
19. **`except Exception`**：继续用 ruff BLE001，降级日志固定带异常类型与上下文，不加自定义 lint。
20. **CONTRIBUTING / SECURITY**：留 S14 发布前收尾，正文程度到时再定。

## 2026-11-10 新记：笔记系统与人物卡

21. **删除测试 note skill**：`src/aris/behavior/skills/note/` 是早期测试直接进库的，**v1 前删掉**；
    它写的 `data/notes/` 是运行时数据，先确认有没有用户内容，再决定是否清理。
22. **角色笔记系统（已定稿）**：每角色（`cid`）一份，存 `data/characters/<cid>/notes.sqlite`
    （独立 SQLite，**不进记忆库**，切 full / lite / 换库都不丢，随角色目录备份与软删）；
    做成记忆系统里的**常驻工具**（不是 skill）：`memory_note_write` / `memory_note_read` /
    `memory_note_search` / `memory_note_delete`；一条笔记 = **可选标题 + 正文**；**模糊搜索用 FTS5 trigram，
    不用向量**；上限默认 **500 条 / 单条 4000 字**（进 `memory.toml [notes]`，超限拒绝不截断）；
    v1 **不自动注入**，只由模型按需调用；WebUI + CLI 都提供管理入口。
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
29. **`aris-icon.png` 是开发者设计的项目图标**：根目录未跟踪文件（2000×2000，黑体 `ARIS` + 左红右米色
    wordmark）。**v1.x 收好**：确认用途（关于页 / 应用图标 / 仓库封面）与存放位置；若要当应用图标，
    需另做带留白的方形多尺寸版本（打包在 S13 处理）。
30. **全双工模型支持（v1.x）**：v1.0 的语音链路按「STT → LLM → TTS」半双工做；v1.x 再评估
    全双工（边说边听、可打断）的模型接入与调度。
