# 开发进度

> 只记**当前**状态与在手的事；历史条目不在仓库内。
> 开工前先读本文件，再读 `todolist.md`（待办唯一真相源）与 AGENTS.md §10 路由。

## 当前版本

`0.4.7`（tag `alpha-v0.4.7`，alpha 开发通道，2026-11-08）。上一个正式版是 `0.4.5.1`。
**v1.0「跨越」开发周期从 `alpha-v0.4.6` 起算**。

## 当前阶段

**v1.0「跨越」开发周期已启动**（`alpha-v0.4.6`），已进入施工：S1 从外部组件清单开始落代码，其余批次先收敛文档与决策。

- **v1 未定事项已收口（2026-11-08）**：S1/S2、S9 消息平台、S10 记忆与角色、S12 知识库与
  skills、S14 收尾、fallback 口径与 core 优化范围全部拍板并写回 `docs/process/v1.0.0-prep.md`
  （§3.9 / §4.x / §7）；当前只剩 CONTRIBUTING / SECURITY 正文留到 S14 发布前。
- **v1 整体复查（2026-11-09，暂停在新商议前）**：已修掉一批文档不一致——§3.5 去掉「竞速」、
  §4.4 补 `/#new-s`、§6 映射改为「视频不做、音频做」、§5.2 / §6 映射补 fallback 重写与遗漏条目、
  S1 标注配置类随批次登记；`todolist.md` 清掉已取消的「简单 / 高级两套设置」「密码和 API key 加密」
  与旧 D9 fallback。**仍开着**：① 搜索引擎注册表落点（独立 `search_engines.toml` vs 并回
  `search.toml`）；② `skills.toml [import]` 在设置页的归属（8 个 tab 里没有 skills）；
  ③ 根目录 `aris-icon.png` 的用途与存放。
- **新商议已定稿（2026-11-10）**：① 角色笔记 = 每角色一份独立 SQLite（`data/characters/<cid>/notes.sqlite`，
  不进记忆库、切库不丢），记忆系统常驻工具（`memory_note_write/read/search/delete`），可选标题 + 正文，
  FTS5 trigram 模糊搜索、不用向量，默认 500 条 / 4000 字，v1 不自动注入；② 人物卡重要度 `0~100`
  （模型可标、用户可改、`importance_source` 只显示不锁定），**卡是派生的**（纯提及只建身份，有事实或有
  直接对话才算有卡，不做 stub/active/archived 状态机），进上下文 = 当前发言人 + 固定 ≤3 + 重要度前 3，
  按 `entity_id` 去重、顺序稳定；主人保底前 3；前 15 只打标签 + 提示词名字索引 + `memory_find_person` 加权；
  新增 `memory_find_person` 与 `memory_update_fact`。契约见 `docs/process/v1.0.0-prep.md` §4.7。
- **阈值触发的两次调用已定稿（2026-11-10）**：① 事件抽取 = **一次抽取任务、只看当前上下文**
  （与 compact 同一段 history，不读 DB、不设水位线、不分块），走标准 `AgentLoop`（`tool_calls` 后必须回传
  `tool` 结果）、维护工具 `memory_find_person` + `memory_write_events`、`max_rounds` 4、单次事件上限 60；
  ② compact 摘要 = **滚动合并 + 要素化**（不写第一人称）、不设长度上限、不做模板校验、空输出算失败，
  摘要是一条带 `[记忆·对话摘要]` 的 `user` 消息。两次失败语义统一：全失败整轮失败；抽取幂等靠
  `extract_key` 覆盖重写。契约见 `docs/process/v1.0.0-prep.md` §4.21。
- **消息平台首个实现改为 Matrix（2026-11-13）**：v1 只做 Matrix，OneBot 不做（NapCat 停更 / SnowLuma
  转私有，协议端生态不稳定）。登录只封装 `matrix-nio` 已有能力——密码 + access token，不做 OAuth2 /
  refresh token；`device_id` 由 homeserver 生成并持久化、不自动轮换；密码与 token 都存
  `secrets.toml`，token 失效自动重登（沿用原 `device_id`）；别名默认不拼完整 id、用户可手填
  短别名；自动进房与 E2EE 默认关；适配器目录 `src/aris/platforms/adapters/`。离线回放默认
  60 分钟 / 每房间 50 条（可配），入站图片上限默认 20 MB（可配，0 = 不限）。契约见
  `docs/process/v1.0.0-prep.md` §4.4。
- **入站缓冲合并（2026-11-13）**：流式期间的新输入进待处理缓冲，静默 `batch_window`（默认 1.5 s）或达到
  `batch_max_messages`（默认 8 条）/ `batch_max_tokens`（默认 4000）封批，等当前轮结束按 FIFO 处理；
  `buffer_scope` 默认 `per_chat`（每来源一份，回复目标唯一），可切 `session`（跨来源合批，默认回最后来源，
  其他来源靠 `send_message` 或不回）；满了只封批，不中止输出、不丢消息。提示层来源标签按连续段打、
  不逐条重复，结构化来源仍逐条入库。契约见 §4.4。
- **来源段头与两周记开关（2026-11-13）**：段头**拼进消息内容**（`[Matrix 摸鱼群 | 小明]` 群聊 /
  `[Matrix 小明]` 私聊 / `[Matrix 群 | 小明]` 无名群；前端只标 `[TUI]` / `[WebUI]` / `[GUI]`），
  格式本身表达群聊与私聊，约定写进 system prompt 开头；时间只在相邻消息间隔超过
  `time_gap_minutes`（默认 10 分钟）时插一行 `[14:32]`。
  两周记是**总开关 + 子开关**：`fortnightly.enabled` 关掉即生成 / 注入 / 检索全关（旧记录保留），
  `inject.fortnightly` 关掉只是不注入。契约见 §4.4、§4.7。
- **入站契约与会话执行（2026-11-13）**：平台层管协议 / 去重 / 白名单 / 门控 / 媒体，`chat` 管缓冲 /
  串行队列 / 执行 / 历史，TUI / WebUI / autorun 共用 `chat.submit`（同步只入队、不调模型）。
  队列上限 `queue_max_messages` 默认 200，超出丢最旧 + 160 字预览（≤50 条）合成 `[系统·排队溢出]`
  系统块，不阻塞 `/sync`；`chat` 按职责拆文件（history 单列，S10 换实现不动链路）。契约见 §4.4。
- **上下文存储三层（2026-11-13）**：内存上下文（进程内组装，不落盘）/ PG（历史界面与首次写入的主）/
  JSONL（按会话分文件、按大小切分，旁路留档与恢复备用，`aris chat reindex` 从它重建）。
  PG 只两张表（`chat_sessions` + `chat_messages`，不做事件表 / fold）；compact 是 `kind=compact` 的
  一条消息、自带 `covers_upto_seq`；JSONL **每轮结束写、先 JSONL 后 PG**。逐条原文只在 `chat_messages`，
  记忆库存语义块 `memory_chunks`（自带正文 + `source_ref` 溯源），需要原文时走总线 `chat.history.read`。
  契约见 §4.4。
- **门控唤醒与缓冲入库（2026-11-13）**：不新增唤醒前缀——群聊触发集合 = @ / 回复 / `/#`；`/#XXX` 未命中
  指令表即视为「指定对模型说话」（等价 @），已知指令无权限则回「没有权限」并拦下。概率 / 决策判「说」时，
  决策环形缓冲（≤20 条）随命中消息一次性写入 `chat_messages`（按 `event_id` 去重），一直不命中的聊天永不落库。
  平台页「账号卡 → 设置 → 会话」块顶部放 `gate_defaults`、下面列已知聊天逐行改覆盖。契约见 §4.4、§4.12。
- **S13 启动器与首启（2026-11-13）**：**不做版本戳**，启动器每次交给 `uv sync --frozen` 判定（幂等，
  已同步约 30 ms），可选组记 `<data>/runtime/groups`；失败退出、不原子替换、不降级适配。
  首启拆成启动器（Python + 依赖）与 `aris serve`（便携 PG）两段；进度用 `<data>/state/setup.json`
  阶段提示 + GUI「正在准备运行环境」页，不假造百分比；产物命名 `aris-project_1.0.0_amd64.deb` /
  `aris-project-1.0.0-1-x86_64.pkg.tar.zst` / `SHA256SUMS`。契约见 §4.15。
- **版本检测（2026-11-13）**：v1.0 做「检测 + 提示」，只查 GitHub Releases 的 `latest`（正式版）；
  侧栏品牌区一行 + 关于页一行，点版本号即手动检查；CLI 不加入口；`update.toml` 的
  `mode = auto|manual|off` + `interval_hours`，超时 10 s 重试一次，失败静默，可按版本忽略。
  契约见 §4.25。
- **大会话与历史界面（2026-11-13）**：大会话口径落数（`user|assistant` 的 `occurred_at`，最大间隔 < 2h 停，
  `memory_conversations` 按需重算）；独立 `/history` 页＝左 1/3 列表 + 右 2/3 详情（上消息、下事件与笔记，
  小会话视图无下半），手机端竖排；`chat_messages.kind` 改 `user|assistant|system|compact` 并加 `tools`；
  不做关键词检索，深链 v1.x；笔记补 `created_at`/`updated_at`（工具默认不返回时间）。
  契约见 §4.7、§4.26。
- **笔记简化（2026-11-13）**：角色笔记砍掉标题字段（一条笔记 = 一段纯文本，**第一行即标题**）、
  砍掉 FTS5 + trigram（改 `content LIKE` 全表扫，2 MB 量级毫秒级）、砍掉冗余 `cid` 列；
  保留每角色独立 `notes.sqlite`、4 个常驻工具、500 条 / 4000 字可配上限与两个时间戳。
  契约见 §4.7。
- **默认模型与种子（2026-11-13）**：种子 `providers.toml` 的 `default_model` **留空**（运行期按
  `default_provider_order` 取第一个可用模型）；模型改名为 `deepseek-flash`、capabilities 加 `vision`。
  官方已确认旧名 `deepseek-v4-flash` 仍被接受但模型已下线（由 V4.1-Flash 承接）。
- **API 格式适配（2026-11-13）**：v1.0 三种都做——Chat Completions / Responses / Anthropic；
  `API-CALL.md` §4.2 原来「不接 Anthropic」的 2026-09-28 定案作废，改为「按端点实测能力降级」。
- **实现细则第二批（2026-11-13）**：前端三态（加载 / 空 / 错，Jinja include + 服务端错误映射）、
  长任务沿用 `webui/tasks`（内存、不持久化、备份用不确定进度）、轮次 PG 写失败「重试一次后作废本轮」、
  写库只在 chat 队列 + 记忆侧按 cid 加锁、SSE 断线插分隔不补历史。契约见 §4.27 ⑧–⑫。
- **v1 打包范围加入 Gentoo ebuild（2026-11-13）**：v1.0 出 Arch 包 + deb + Gentoo ebuild（x86_64），
  其中 ebuild 含 GUI 源码构建（`dev-lang/go` + `go-module.eclass`）。主树已有 `dev-python/uv`，
  ebuild 不内置 uv；但该包默认 `python-downloads = "manual"`，首启 wrapper 必须先显式
  `uv python install 3.14` 再 `uv sync`。**不做真机 `emerge` 验证**（只做 `pkgcheck scan` 等静态校验，
  发布说明标注未验证）；仓库只放单包 ebuild 目录 `packaging/gentoo/sci-ml/aris-project/`，不维护 overlay。
- **分发渠道（2026-11-13）**：GitHub Releases 是唯一真相源（源码 tarball + `.deb` + `.pkg.tar.zst` +
  `SHA256SUMS`），**不自建二进制仓库**——**进源只走 AUR**（`aris-project`）；Gentoo 与 deb 都不进任何源
  （ebuild 复制进本地 overlay，GURU 等第二个维护者 / 贡献者再提；deb 直接下载，要 `apt upgrade` 时
  v1.x 再上 OBS）、Flatpak 不做。
- **记忆系统对外定名 APEMS**（Aris Project Engram Memory System）：`Engram` 是名、`Memory System`
  是性质；代码仍叫 `memory`，界面导航仍叫「记忆」（2026-11-06 复核）。
- **插件系统整体推迟 v1.1**，v1.0 不做也不预留接口；草案移到 `docs/process/v1.1-plugin-system.md`。
- **决策模型去掉 `main_llm`**：只保留 `off | dedicated`，失败降级到概率 / 规则；消息密集时先攒批再判。
- **记忆**：重要性由抽取时模型标注（`importance ≥ 0.8` → 「重要」预设，weight 2048、直接常驻）；
  真实命中只续命（重置 `last_reinforced_at`、累加 `hit_count`，不改 weight）；中期在 30 天内
  ≥5 个不同自然日命中的晋升长期（止步于长期）；兜底检索 / 随机回忆不写库。
  大会话（时间聚类）保留用于作息 / 活跃度查看，但 v1 不做大会话总结（小会话总结即 compact）；
  换 embedding 模型走影子表全量重建。
- **外部 PostgreSQL**：保留支持；备份改用 `pg_dump` 逻辑导出，版本不匹配时明确标注「数据库未备份」。
- **S1 T6 已落地（2026-11-07）**：`infra/components.py` 收编 PG / pgvector / micromamba / embedding
  的版本与校验值（`Archive` / `CondaPackage` / `Model` 三种条目）；`store/bootstrap.py` 删掉版本常量、
  修掉 arch 写死；本地 embedding 改为锁 HF commit（原来读 `refs/main`，是浮动的）；
  `aris components list [--json]` 只读、`doctor` 增主版本对账。镜像写 `store.toml` 的 `[mirror]`
  （只换 URL，sha256 仍取清单）；**uv 不进清单**（运行期不用，归 S13 打包脚本）。
  版本仍钉 `17` / `0.8.1`，目标 `18.6` / `0.8.6` 在 S5 连同 `data/pgdata` 重建一起切。
- **配置档**：`serve.toml` / `webui.toml` 不随档（避免恢复别人的备份后端口变化）；GUI 不得写死端口。
- **施工顺序已定**（2026-11-03）：v1 按 S1–S14 批次推进（元数据与 i18n 基建 → WebUI 外壳 →
  备份 → 配置档 → 存储适配 → 消息模型 → LLM → 设置页 → 消息平台 → 记忆/角色 → WebChat/决策/autorun
  → 知识库二期/skills → GUI/打包/CD → i18n 收口），见 `docs/process/v1.0.0-prep.md` §5。
- **GUI 定为 MyGO（Go）**：工具链只放 `gui/`（不需要 Bun），打包配方自己写；后端地址走
  `<data>/state/webui.json`（addr / pid / 版本），关窗只关 GUI 并提供「关闭后端」按钮。
- **WebChat**：保留 `Dashboard | Chat` 分段切换；切到 Chat 后侧栏换成角色列表，不做会话切换；
  输入区 = 文本 + 图片；思考链 / 工具调用 / 记忆命中是三个用户开关（默认全关）。
- **多角色**：平台实例与角色绑定（可绑多个，实例排他），路由 = 实例 → cid → 唯一会话；
  群聊 / 共用实例留 v1.x。
- **图片**：按模型 `图形理解` 能力投影——原生发图 / 可选「图片转述」/ 占位；发送前限边长、压体积、
  动图拼九宫格（AstrBot 同思路）。
- **关于页彩蛋**：白色图标触发；默认**外链跳转**到东方红一号卫星在轨播发电子音版本的公开页面
  （普通超链接、新标签、不内嵌、不直链、不打包）。除版权外还有四层合规：软件许可（AGPL 覆盖不到
  第三方资产 / 打包规则要求许可证）、平台内容政策、链接方式、跨境分发——详见 `v1.0.0-prep.md` §4.23。
  **硬规则：包内不得出现任何《东方红》音频文件**。
- **S1 施工文档已写**：`docs/process/v1/S1-foundation.md`。工具开关只做按工具（owner 级归插件系统 v1.1），
  `tools.toml` 只记 `[disabled] tools`，关闭 = 移出工具面 + 拒绝执行；模块关闭时配置项仍列出。
- **store 总线化已排进 S5**（2026-11-06 定）：业务模块不再直接 import store，统一走 `store.*`；
  连接对象走**方案 A（池化上下文）**——`store.connect` 从 `psycopg_pool` 借还、pgvector 适配器在池的
  `configure` 注册、事务边界仍归调用方，见 `v1.0.0-prep.md` §3.7。
- **CMCB 缺失语义定案（2026-11-11）**：`call` 缺服务按三态处理——归属模块没装配 → `None`
  （预期降级）；已装却缺 / core 域（`llm` / `audit` / `http`）/ 前缀拼错 → 抛 `ServiceMissing`。
  归属用 `ModuleSpec.services` 反查、装配集由 `assemble()` 注入；**不新增 `call_required()`**。
  排 **S1**（`S1-foundation.md` T7），见 `v1.0.0-prep.md` §3.7。
- **用户自选与 v1 语音范围收窄（2026-11-11）**：v1 不做独立 TTS / STT（音频只走多模态内容块）；
  可选参数直接给扁平 TOML 键，**不做预设 / 档位**；人格与表达归 `prompt.md`；不做「只观察」模式；
  每日主动消息上限、token / 费用预算不在 v1。记忆 / 平台 / 成本三类仍写死的参数清单记进
  `todolist.md`「给予用户更多可设置项」，细节以后再说。
- **外部组件清单定案**（2026-11-06）：`src/aris/infra/components.py`（**Python 常量**，不用 TOML），
  v1 只收 PG + embedding，排 **S1**；用户层 `data/config/components.toml` 只能覆盖 `url`（镜像），
  `sha256` 永远在代码里（§3.8，§7-28 已结）。
- **v1prep 工程化（2026-11-06）**：§4.5 补全搜索引擎注册表契约（落点拆 `search_engines.toml` 仍待拍板）；
  §4.8 角色系统原按代码校正为 `character.toml` + `worldview/relations/growth.md`
  （**2026-11-08 再次推翻：改回 `prompt.md` + `character.toml` 配置**，三个 md 由泛记忆近似）、
  cid 规则与 12 位十六进制自动生成冲突、`CharacterStore.create()` 无 cid 校验
  （S10 开入口前必须补，否则是目录穿越）；§4.14 skills 导入定下「内置 / 用户两层根 + 原子落盘 + 无沙箱」。
- **记忆模型校正（2026-11-06）**：「重要」恢复为模型在抽取时打标（`weight = 1024`、直接常驻，
  不进则已、进则顶格）；检索退化为续命（只重置 `last_reinforced_at`，不改 `weight`）；
  晋升改为 5 个自然日（可配 5~7）且止步于长期；`hit×128` / `384` / `recall_bonus` 全删。
  详见 `MEMORY.md` §1 / §4。
- **`is_user` → `is_owner`（2026-11-07 定）**：原字段把「当前发言人」「归属」「是不是人」三件事挤成一个 bool，
  与「群聊 / 多平台对话对象不止一个」自相矛盾。改为 **`is_owner`（这个角色属于谁）**：至多一个、可以没有、
  只由用户手动设，数据库用部分唯一索引保证；当前发言人改由消息信封 `speaker` 经 `memory_identities` 解析。
  抽取 schema 不再输出该字段；WebUI 人物页与 CLI `aris memory owner` 对等。显示文案可配
  `owner_label`（默认「主人」，可改「管理员」等）。详见 `MEMORY.md` §5.1 / §10 / §15。
- **换 embedding 模型后的旧表保留期（2026-11-07 定）**：`retention_days` 默认 7 天、可配 0~30
  （0 = 切换成功即删）；保留期内可回滚，到期自动清理。
- **记忆库元信息 = 库自描述（2026-11-07 定，方案 A）**：每个库内部一张单行 `memory_library`
  （full 在该库 PG schema 内，lite 在该库 SQLite 文件内），**不设全局注册表**；不存 `initialized`
  （启动探测）、不存 `cid` 绑定、不存大小 / 条数；不做 `description` / `last_used_at`。
  物理位置由 `library_id` 推导（schema `mem_<id 前 12 位>`、文件 `data/memory/libraries/<id>.sqlite`），
  `character.toml` 只存 `library_id`。结构迁移逐库记在库内 `memory_migrations`——全局
  `store_schema_migrations` 的 `(owner, version)` 表达不了每库进度不同。详见 `MEMORY.md` §1.1 / §10。
- **`importance` 保留（2026-11-07 评估）**：只作抽取原始分，用于定预设、审计、改阈值后重新分层；
  运行期注入与排序只看 `w_eff`，不再参与重排。
- **会话冷却同步为 1 天（2026-11-07）**：`AGENTS.md` 与 `PORTABILITY-AND-SINGLE-SESSION.md` 一并改成
  「默认 1 天，可配、最大 5 天」，与 `MEMORY.md` §9.0 一致。
- **记忆文档一致性修订（2026-11-07）**：补 `memory_hits`（晋升要 `DISTINCT` 自然日，原 DDL 无处记录）、
  `memory_identities`（speaker → 实体）、`memory_messages` 的 `speaker` 等字段；`valid_to` 与
  `superseded_at` 拆成世界时间 / 系统时间；`stale` 落列；事件参与者只存 `memory_event_entities`；
  检索重排改为 `0.7 rel + 0.3 norm(w_eff)`（原 `importance` + `recency` 与 `w_eff` 重复计权）；
  两周记检索改用真实窗口边界；钉住上限与关键块配额对齐；工具面明确为 2 读 2 写。
- **衰减改连续曲线（2026-11-07）**：`w_eff = weight × 0.5^(Δt/H)` 取代整数位移 `>>`；
  `weight` 明确为**基准值**、永不随衰减变小；仍惰性计算、无定时任务。为保住原来的
  「重要」146 天常驻，基准从 1024 提到 **2048**（H 仍 73，彻底不可达仍是 584 天）；
  中期 `<8` 从约 70 天缩到 **约 56 天**。排序要可索引时再把算好的分物化成派生 `score`
  缓存（零迁移），v1 不做。
- **印象层（2026-11-06 定）**：`facts` 表取代 `relations`（claim 而非 truth：`confidence` / `source_kind` /
  `evidence` / 有效期 / `status`，`inferred` 默认不进常驻）；人物卡 `[记忆·人物]` 取代关系摘要卡，
  按人分卡（槽位段来自事实库、自由段由角色自写 ≤150 字）；事件加可选 `mood`（七档预设 + 允许自拟）。
  详见 `MEMORY.md` §5 / §6.1。
- **memory-lite 与 full 同构（2026-11-06 定）**：事实层三表（`memory_entities` / `memory_facts` / `memory_event_entities`）都实现，
  只砍递归 CTE；消歧靠 `aliases` 精确匹配 + 人工合并；人物卡做成通用开关 `inject.people_card`
  （默认开、两个后端共用），有效槽位 <2 自动不渲染。
- **设置页分类定案（2026-11-06）**：合并为 **8 个 tab**（聊天 / 模型与搜索 / 记忆 / 知识库 / 存储与向量 /
  服务与网络 / 日志与通知 / 界面），文件→tab 映射在 `infra/config_items.py` 一处定义、顺序显式；
  `settings.toml` 允许字段级 `category` 覆盖；section 目标 3~12 项，`collapsed` 只按冷门程度用；
  `serve.skip` / `llm_providers_file` 标 `hidden`；搜索补「跨 tab 跳转 + 高亮」，见 §3.3。
- **PG / pgvector 定版本（2026-11-06）**：改钉 **`postgresql=18.6` + `pgvector=0.8.6`**（PG 17 最高只能配
  pgvector 0.8.1，两者由 `libpq` 绑死）；版本常量进 `infra/components.py`，改它即升级、随版本发布；
  `MAMBA_URL` 的 arch 写死一并修掉（aarch64 目前装不了）；micromamba 也收进该清单以支持镜像覆盖。
  **本机需一次性重建 `data/pgdata`**（17→18），并丢弃 `data/knowledge/` 的两篇测试文档（S5 动手时做）。
  另：`architecture-findings-2026-11-06.md` 里 6 条未决项已并入 `v1.0.0-prep.md` §7-32~37。
- **打包与 CD 定案（2026-11-06）**：**M1（运行时 uv）确认**——包只装源码 + `uv.lock` + 启动器，
  解释器由 uv 在首启安装；**Arch 声明 `depends=('uv')`、deb 内置钉死的 uv**（Debian 无 uv 二进制包，
  sid 只产 `python3-uv-build`）；命名 **2026-11-13 改为包名 `aris-project`、app-id `dev.arisproject.aris`**，
  安装目录 `/usr/share/aris-project/`、`/usr/lib/aris-project/`，命令仍 `arisp` / `arisp-gui`
  （`aris` 被 GNU Aris 占用）。首启下载 ≈ CPython 73 MB + 基础依赖（装好 129 MB）+ PG 约 40 MB，
  本地 embedding 按需再补 1.5 GB。详见 §4.15。
- **Python 钉 3.14（2026-11-06）**：仓库根加 `.python-version` = `3.14`。原 `requires-python >=3.14`
  会让 uv 选到 3.15，而 `pydantic-core` / `jiter` 无 cp315 轮子 → 转源码编译。
  **暂不升 3.15**：`openvino` / `openvino-tokenizers` 任何版本都没有 cp315 wheel（C++ 扩展），
  其余依赖已就绪；等 OpenVINO 出新版再整体升。
- **旧文档集中清理不绑阶段**（2026-11-04 定），见 `v1.0.0-prep.md` §10.1。
- **S13 施工文档已写（2026-11-06）**：`docs/process/v1/S13-packaging.md`——产物与命名、安装布局、
  首启启动器（环境变量 + stamp 重同步 + 失败处理）、PKGBUILD / deb 要点（含 trixie 的
  `libgtk-3-0t64` / `libwebkit2gtk-4.1-0`）、`.desktop`、CI 矩阵、验收清单。
- **命名一致性校对（2026-11-06）**：**CMCB 服务表整表删除**（清单以 `aris services list` 为准，
  文档不再维护，必然漂移），命名规则改成「功能域 + 2~3 段」，`AGENTS.md` §6 / §7 同步；
  种子模板删掉指向已消失的 `docs/developDoc/` 的注释，`store.toml` 的 `--extra embedding`
  改为 `--group embedding`；`paths.py` / `todolist.md` 里残留的旧命令名 `paris` 改为 `arisp`；
  安装态数据目录改名 `~/.project-aris` → **`~/.aris-project`**（源码树仍用仓库 `data/`）；
  显示名统一为 **`Aris Project`**；删掉过程文档 `TUI-问题修复.md`。
  命令维持双名：`arisp` 只出现在「以包形式安装」的语境；记忆表统一 `memory_*` 前缀
   （`memory_entities` / `memory_facts` / `memory_event_entities`）。命名议题全部结案。
- v1 文档仍有未定项（STT 选型、流式提前输入、记忆检索调参等），见同文 §7。

| 项 | 状态 |
|---|---|
| pytest 假失败（模块级 `skipif` 早于 autouse fixture） | 已发布 |
| integration 选中系统 PG、缺 pgvector | 已发布，远端 integration 已绿 |
| `db init` 后紧跟 `db start` 误判端口 | 已发布（`4b9bd80`） |
| `docs/dev-flow.md` 错误陈述、`gh` 改网页优先 | 已发布 |
| `PROGRESS.md` 刷新、`V1.0-PLAN.md` 归档、`todolist.md` 结算 | 已完成 |
| `CHANGELOG` 归档 `[0.4.5]` 并封 `[0.4.5.1]` | 已完成 |

发版过程记录：tag `v0.4.5.1` 打在 `main` 的合并提交 `ea73a74` 上；发布期间上游尚未开启
**Allow auto-merge**，0.4.5.1 的两步 PR 均为检查全绿后手动合并。

## 模块状态

| 模块 | 状态 |
|---|---|
| `core/` | 完成：CMCB 总线（服务 + 事件 + 审计）、LLM 多提供方 / fallback / 流式 / 工具调用 |
| `store/` | 完成：便携 PG + pgvector、本地 embedding（Bekko 384 维）、迁移机制、向量 helper |
| `knowledge/` | 首期完成：摄入 / 分块 / 纯向量检索 / CLI / agent 工具 / WebUI 页 |
| `behavior/` | 完成：agent loop、工具注册表（世代同步）、内置工具、skills；工具声明式收编（`.ai_tools`） |
| `mcp/` | 完成：通用 MCP 客户端（stdio / streamable-http，owner 线程 + 同步总线服务） |
| `chat/` | 完成：会话逻辑 + TUI（调试用） |
| `character/` | 完成：角色载体 `data/characters/<cid>/` |
| `serve/` | 完成：`aris serve` 一条命令起全套；唯一组装根 |
| `webui/` | 完成：鉴权 / 仪表盘 / 审计 / 提供商 / 技能 / 配置 / 日志 / 知识库；配置页体验待重做 |
| `memory/` | v1 P4 开工（对外名 **APEMS**）；契约已按 2026-11-03 决策更新（见 `docs/forAiDoc/MEMORY.md`） |
| `voice/` | 占位：STT / TTS 选型未定 |
| `autorun/` | 方向已定，暂不实现（只留设计） |

## v0.4.5 已落地

- **变更记录**：根 `CHANGELOG.md` 只留 `[Unreleased]` 与最新版本，旧版本归档到 `changelogs/`。
- **CI 分档**：`check`（所有 PR / `develop` / `main` 推送）、`integration`（发版 PR 到 main，
  真 PG + embedding + 全量测试 + 冷启动）、`smoke`（alpha tag）。
- **发版脚本**：`scripts/release.sh` 只做本地准备（校验、切分支、bump、检查），不推送、不打 tag。
- **文档与合规**：`docs/dev-flow.md` 发版节重写、README 变更记录与许可证段、`NOTICE`。

## 0.4.5.1 已落地

- `tests/test_store_portability.py`：PG 二进制探针的跳过条件改为运行时判断。模块级 `skipif`
  在收集阶段求值，早于 autouse fixture 把 `shutil.which` 打成 `None`；装了系统 PostgreSQL 的
  CI runner 会先被判成「已安装」，用例内再探测却得到「未安装」，变成假失败。
- `ARIS_PG_SOURCE=auto|project|system`：收窄便携 PG 探针链。系统 PostgreSQL 未必装
  pgvector，`integration` 设 `project` 强制走 `data/pg`（`ARIS_PG_BIN` 仍最高优先）。
- `choose_port` 复用「本实例已在跑」的端口，`start` / `stop` 不再误清运行中实例的
  pid/socket：修 `db init` 后紧跟 `db start` 的幂等性回归。
- `docs/dev-flow.md`：修正「fork PR 首次带 workflow 也能跑」的错误陈述，补 bootstrap 坑；
  `gh` 命令改为网页操作步骤。

## 阻塞 / 待决

- **上游仓库设置**：`.github/rulesets/` 的必需检查已生效（0.4.5.1 两次 PR 都跑了
  `check` + `integration`）；**Allow auto-merge 已开启**（2026-11-03），后续发版 PR 可直接
  开 auto-merge。
- **`gh` CLI**：本机尚未安装；网页操作可用，配置后可简化 PR 与合并操作（auto-merge 的
  仓库开关仍需先在上游设置里打开）。
- **安装态数据目录**：**包安装用 `~/.aris-project`，源码树用项目根 `data/`**（2026-11-06 定）；不做 XDG、不上 Flatpak。
- **v1 设计已收口**：`docs/process/v1.0.0-prep.md` §7 只剩 CONTRIBUTING / SECURITY 正文待定
  （S14 前），其余条目均可直接施工。
- STT 选型：候选 Groq Whisper / 通义听悟。
- mypy 检查范围：当前只查 `core` + `store`，扩到其余模块的时间待定。
- `CONTRIBUTING.md` / `SECURITY.md`：0 字节占位，S14 重写（面向人类、不引用 AI 文档）。

## 下一步

1. **S1 契约与地基**：配置项元数据 schema + `config.items`、i18n 基建 `t()`、工具开关、
   品牌 URL / egg-info 尾巴、旧文档清理（§10.1）；顺手带走 `cli.py` 拆包与 tests 分组。
2. **S1 已谈定，可开工**（2026-11-07）：元数据字段 / 英文 slug / 新增 `config` 命名空间 /
   `condition` 先落字段 / `config.items` 在 S1 提供 / 不做 `aris config items` /
   可关模块改显式 `register()`；细节见 `docs/process/v1/S1-foundation.md`。
3. **v1 文档剩余待定项**：GUI 框架、WebChat 界面、彩蛋等（§5.4 / §7）。
