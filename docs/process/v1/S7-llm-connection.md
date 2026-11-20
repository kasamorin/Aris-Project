# S7 LLM 连接、提供商与 fallback

> 状态：细节已定、可开工（2026-11-20）
> 代码入口：`src/aris/core/llm/`、`src/aris/cli.py`、`src/aris/chat/`
> 事实查看：`aris llm list` / `aris llm check` / `aris llm fetch`；服务清单 `aris services list`
> 上游契约：`docs/process/v1.0.0-prep.md` §3.5、§3.9、§4.2、§4.12、§4.28

## 1. 一句话

把 LLM 配置收成**一层 provider（连接）**：协议在 provider 层、引用统一 `provider/model`、
id 创建后不可改、fallback 只有顶层一条链；本地 / 决策 / 全双工都投影到同一套 provider 抽象，
但各自走独立入口，不互相污染。

## 2. 出口条件（DoD）

| # | 验收 | 判据 |
|---|---|---|
| 1 | 新 schema 可加载 | 新格式 `providers.toml` 能启动；旧键（`default_provider_order` / `transport` / `formats`）直接报配置错误并给新格式示例 |
| 2 | 引用解析稳定 | `provider/model` 按第一个 `/` 切分；model id 自身含 `/` 仍能命中；不按模型 id 全局搜索 |
| 3 | 默认模型必配 | 缺失 / 无效 / 指向非对话模型 = 配置错误；`aris llm check` 非零退出，不再取第一个可用模型 |
| 4 | fallback 时序可控 | 占位 → 可重试错误同模型同提供方再试一次 → 全局 `fallback_models` 逐条尝试 → 停在占位；已吐真实内容 / 已执行工具后不再切换 |
| 5 | 不粘滞、不竞速 | 下一次请求仍从会话模型或 `default_model` 开始；`llm.race` 服务与竞速代码删除 |
| 6 | 删除受引用保护 | provider / 模型被 `default_model`、`fallback_models`、会话、角色、`decision.model`、全双工选择引用时拒绝删除并列出位置 |
| 7 | 本地投影可用 | 本地模型投影为固定 id `local` 的 provider，引用写 `local/<model>`；加载 + 推理计入本次总预算；加载失败 / busy / 预算不足跳下一条 |
| 8 | 决策隔离 | `decision.model = "provider/model"`，只接受决策协议族与本地决策模型；无 fallback 链；失败降级到概率 / 规则 |
| 9 | 全双工隔离 | 能力标记 `full_duplex`，适配器在 `core/llm/full_duplex/`；不接 `stream_chat`，不参与 `default_model` / `/#model` / 对话 fallback；代码无硬编码模型名 |
| 10 | 回归干净 | `bash scripts/check.sh` 全绿；`aris serve --dry-run` 启动检查通过 |

## 3. Schema

### 3.1 顶层

```toml
default_model = "deepseek/deepseek-flash"          # 必配；必须是对话模型
provider_order = ["deepseek", "openrouter"]        # 只影响展示顺序与 fetch 默认对象
fallback_models = ["openrouter/deepseek/deepseek-v4-pro"]
```

- `default_model`：必填、只能指向对话模型（`openai_chat` / `openai_responses` /
  `anthropic_messages` / `local` 下的 chat 模型）。
- `provider_order`：去重后决定提供商列表顺序；未列出的 provider 按文件出现顺序追加。
  **不参与 fallback**；`llm fetch` 无参数时取列表第一个。
- `fallback_models`：有序、可空；每项必须是允许模型列表里的对话模型；重复项报配置错误。

### 3.2 provider

```toml
[[providers.provider]]
id = "deepseek"                 # 创建后不可改；不能含 "/"
name = "DeepSeek"               # 可改
api_format = "openai_chat"      # 协议族，见下表
base_url = "https://api.deepseek.com"
api_key_env = "DEEPSEEK_API_KEY"
timeout = 30                    # 单次尝试超时（秒）

  [[providers.provider.models]]
  id = "deepseek-flash"         # provider 内唯一；创建后不可改；可含 "/"
  name = "DeepSeek Flash"       # 可改
  request_name = "deepseek-flash"
  context_length = 1000000
  capabilities = ["tools", "reasoning"]
  thinking_default = false
```

`api_format` 取值：

| 值 | 模型类型 | 说明 |
|---|---|---|
| `openai_chat` | 对话 | OpenAI Chat Completions 及兼容实现 |
| `openai_responses` | 对话 | OpenAI Responses |
| `anthropic_messages` | 对话 | Anthropic Messages |
| `systemone` | 决策 | `/v1/systemone`（TypeSafe / Transformers / llama.cpp decision） |
| `openai_decisions` | 决策 | OpenAI Decisions |
| `openai_live` | 全双工 | GPT-Live 事件流 |
| `local` | 由模型决定 | `inference` 投影，**不写进配置文件** |

- 一个 provider 只有一种协议；同一 `base_url` / 密钥要多种协议就建多条 provider，
  id 各自独立（例如 `openai` 与 `openai-decisions`）。
- `base_url` 是 API 前缀（含版本段，如 `https://api.openai.com/v1`）；适配器只拼协议后缀
  （`/chat/completions` / `/models` / `/systemone` / `/decisions` / `/live/sessions`），
  不硬编码版本段。
- `capabilities` 只描述模型侧能力：`tools` / `reasoning` / `vision` / `audio_in` / `audio_out`。
  主类型由 `api_format` 决定；本地模型由 manifest 的 `kind` 决定后随投影写入内存记录。
- `thinking_default` 三态：`true` / `false` / 缺省（跟随提供方）；思考档位字段见 §4.3.1，
  本批只保证新 schema 不被旧的布尔口径挡住。

### 3.3 删除字段（破坏性）

- 删除 `default_provider_order` → `provider_order`。
- 删除每 provider 的 `transport`（SDK / httpx 不再由用户选）。
- 删除每模型的 `formats` → provider 层 `api_format`。
- 删除每模型的 `fallback_models`；降级只认顶层 `fallback_models`。
- 删除 `candidates_for()` 的「同模型跨提供方自动横向」语义。
- 删除 `race_fallback` / `retry_count` 用户配置；重试固定为「可重试错误一次」。
- **不提供自动迁移**：旧配置启动即报错；`aris llm check` 打印新旧对照示例；
  `CHANGELOG` 标破坏性变更。

## 4. 引用解析与校验

```text
resolve("openrouter/deepseek/deepseek-v4-pro")
  -> provider_id = "openrouter"
  -> model_id    = "deepseek/deepseek-v4-pro"
```

- 只按**第一个** `/` 切分；provider id 不允许含 `/`，model id 允许。
- 解析失败分三类，错误信息都要带**完整引用**与可用候选：
  1. 没有 `/`；
  2. provider id 不存在；
  3. provider 存在但 model id 不在允许列表。
- 不按模型 id 全局搜索，也不猜「唯一匹配」；同名模型在不同 provider 下是不同条目。
- 加载期校验（`load_providers`）：
  - provider id 唯一、非空、不含 `/`；
  - 同 provider 内 model id 唯一、非空；
  - `api_format` 是已知枚举；
  - `default_model` 存在且是对话模型；
  - `fallback_models` 每项存在、是对话模型、无重复；
  - `provider_order` 每项存在、无重复；
  - 发现旧键直接抛 `ProviderConfigError`，不尝试兼容。
- 运行期解析失败按配置错误处理：功能不可用 + error 日志，不静默换模型。

## 5. fallback 时序

总预算沿用 `settings.toml` 的 `llm_fallback_timeout`（一次请求的总时长，含切换与本地加载）。
单次尝试超时 = `min(provider.timeout, 剩余总预算)`；本地条目的加载 + 推理都吃这份预算。

```text
起点 = 会话显式切换的模型，否则 default_model
  ↓
发请求（首字占位计时从这一刻开始，fallback 不重置）
  ↓ 可重试错误（429 / 5xx / 网络 / 超时）
同模型、同 provider 再试一次
  ↓ 仍失败 / 不可重试错误（鉴权 / 配额 / 请求非法）
按 fallback_models 顺序逐条尝试（每条同样最多两次尝试）
  ↓
链走完仍失败 / 没有链 -> 停在占位，等下一次请求
```

硬规则：

- **已吐真实内容或已执行工具后不切换**：直接进错误处理，避免重复文本与重复工具副作用。
- **空输出重试**：只回 reasoning、无 content 或空响应时，同模型重试 1 次，**不计入 fallback**。
- **不粘滞**：fallback 成功不改变下一次请求的起点，会话里不记「降级中」。
- **不竞速**：删除 `stream_deltas_race` / `llm.race` / `RACE_GRACE` / 降级后竞速恢复。
- **占位保留**：fallback 成功的回答接在占位后面；WebChat 与消息平台都不替换、不撤回。
- **关闭 SDK 内建重试**（`max_retries=0`），重试只由 engine 负责。

## 6. 删除与引用检查

删除 provider 或模型前扫描全部引用源：

| 引用源 | 位置 |
|---|---|
| 默认模型 | `providers.toml` 的 `default_model` |
| fallback 链 | `providers.toml` 的 `fallback_models` |
| 会话当前模型 | 会话存储（数据库） |
| 角色模型绑定 | `data/characters/<cid>/character.toml` |
| 决策模型 | `decision.toml` 的 `model` |
| 全双工模型 | `full_duplex.toml` 的模型选择 |
| 本地模型 | 同表各项；由 `inference` 删除入口执行同一套检查 |

- 任一命中 → **拒绝删除**，返回引用位置清单（文件 / 会话 / 角色）。
- 引用源读不到（例如数据库未启动）→ **fail closed**，提示先启动数据库或先解除引用；
  不做「先删了再说」。
- provider id / 模型 id 不出现在编辑接口的可写字段里；WebUI 新建后置灰，CLI 没有 `--id` 改名参数。
- `name` / `request_name` / 元信息可改；改 `request_name` 只影响请求体，不影响引用。

## 7. 投影

### 7.1 本地 provider

- `inference` 在装配时把本地模型目录投影成一个 provider：
  `id = "local"`、`name = "本地模型"`、`api_format = "local"`、无 `base_url` / `api_key_env`。
- 不写 `providers.toml`，不进 `/models` 联网列表；在提供商页**只读展示**，管理入口跳本地模型页。
- 模型引用 `local/<model>`。对话模型可进 `default_model` / `fallback_models` / 会话 / 角色；
  决策模型只进 `decision.model`；全双工模型（v1.x）只进全双工选择。
- 本地模型 manifest 的 `kind` 必须是 `chat` / `decision` / `full_duplex` 之一；
  embedding 不进 provider。

### 7.2 决策

- `decision.model = "provider/model"`，只接受 `systemone` / `openai_decisions` 与 `local` 下
  带 `decision` 能力的模型；废弃 `decision.provider_id`。
- 决策不读 `default_model` / `fallback_models`，没有自己的 fallback 链；
  失败 / 超时 / 置信度不足 → 概率 / 规则降级（§4.12）。
- v1 只做 `systemone` + `openai_decisions`；SGLang `/v1/decisions` 不进。

### 7.3 全双工

- 能力标记 `full_duplex`；provider 的 `api_format = "openai_live"`；v1 只有这一个 adapter。
- 适配器接口 `FullDuplexAdapter`：`open_session` / `send_audio` / `send_text` / `events` /
  `interrupt` / `close`；核心只依赖这组方法与 `capabilities`
  （`audio_in` / `audio_out` / `text_in` / `text_out` / `delegation` / `playback_ack` /
  `turn_detection`）。
- 配置 `full_duplex.toml`（原 `duplex.toml` 改名）；不接 `stream_chat`，不参与
  `default_model` / `/#model` / 对话 fallback。
- 不硬编码模型名：语音入口从可用 `full_duplex` 模型里选，只有一个自动选，没有就禁用入口。
- 新增 Gemini Live / vLLM-Omni 等只加 adapter，不改核心。

## 8. 施工任务

### T1 schema 与加载器

- `src/aris/core/llm/message.py`：扩展 `ApiFormat`（七个取值，含 `local` 仅内部使用）。
- `src/aris/core/llm/config.py`：
  - `LLMProvider`：`id / name / api_format / base_url / api_key_env / timeout / models`
    + 运行期字段 `origin`（`config` / `local`，不序列化）；
  - `LLMModel`：`id / name / request_name / context_length / capabilities / thinking_default`；
  - `ProviderConfig`：`default_model / provider_order / fallback_models / providers`；
  - `resolve(ref)`、`chat_models()`、`decision_models()`、`full_duplex_models()`；
  - 新校验 + 旧键拒绝。
- `src/aris/seed/config/providers.toml`：在**本批**改成新格式（seed 只影响首次启动，
  旧加载器仍可读旧文件的阶段不要提前改）；注释示例覆盖 `openai_live`，但不预填可计费模型。

### T2 engine 重写

- 删除 `candidates_for` / `_degraded_targets` / `_race_deltas` / `stream_deltas_race` /
  `llm.race` 服务 / 竞速常量。
- 单链执行：起点 → 重试一次 → `fallback_models` → 占位；已产出内容后不再切换。
- 首字占位、空输出重试、错误提示保留；fallback 不重置占位计时。
- 本地条目按总预算调用；`busy` / 加载失败 / 预算不足直接跳下一条。
- `thinking_default` 解析保留；思考档位按 §4.3.1 接。

### T3 管理与 CLI

- `llm list`：显示 provider id / name / `api_format` / key 状态 / 模型引用；标 `[默认]`、
  `[降级 N]`；本地 provider 标「本地」。
- `llm check`：新 schema 校验、旧键提示、引用解析、决策 / 全双工引用、key 缺失、
  空模型列表警告；错误非零退出。
- `llm fetch`：无参数 provider 取 `provider_order` 第一个；只对支持 `/models` 的协议拉取；
  沿用允许列表 + 缺失记录 + 写回备份；**彻底移除 models.dev**。
- `llm test` / `chat --model` / `/#model` 改用 `provider/model`；`/model` 无参展示标 `[默认]`。
- 删除入口加 §6 引用扫描；`doctor` 附 `llm check` 摘要（不改 doctor 退出码）。

### T4 决策适配器（可插空）

- `systemone` + `openai_decisions` 两个适配器，响应归一成 `{value, probabilities, confidence, score}`。
- 只由 `decision.model` 选模型；无 fallback 链；失败 / 超时降级。
- 门控、攒批与 `decision.toml` 参数仍归 S11；本批可只落适配器与选择逻辑。

### T5 全双工适配器

- `core/llm/full_duplex/`：抽象基类 + `openai_live` 实现 + mock adapter。
- `full_duplex.toml` 与模型选择；入口不可用时禁用。
- mock / 契约测试：开会话、收事件、打断、关闭；不发真实语音请求。
- 不把 GPT-Live 特调写进主调度：核心只认 `FullDuplexAdapter` 与 capability flags。

### T6 提供商页

- 新建连接：`id` 必填且创建后锁定；`name` 可改；`api_format` 改动会影响模型解释方式，
  页面要给确认提示，不自动转换已有模型。
- 模型表：`id` 锁定；`name` / `request_name` / 上下文 / 能力可编辑；「+」从联网列表加入允许列表。
- 能力测试、缺失记录、删除引用清单；本地 provider 只读。
- 旧页面字段 `transport` / 每模型 `formats` 删除，不留隐藏兼容字段。

### T7 测试

- 加载：新格式通过；旧键 / 重复 id / 缺默认 / 无效引用 / 重复 fallback 各有用例。
- 解析：model id 含 `/`、provider id 不存在、无 `/`、跨 provider 同名模型。
- fallback：重试一次后切链、不可重试直接切、已吐内容不切、空输出重试不计链、不粘滞。
- 删除：每种引用源各一条拒绝用例；引用源不可读时 fail closed。
- 投影：`local/<model>` 可解析；本地 busy / 加载失败跳下一条；决策与全双工不进对话链。
- 全双工：mock 会话开 / 打断 / 关闭；代码中无 `gpt-live` 字面量（测试可断言）。

## 9. 不在本批

- 多配置档（S4）里的 `providers.toml` 迁移：本批只认全局文件；S4 落地后按档路径读取。
- 决策门控与攒批（S11）。
- 本地双工（v1.x）。
- 官方提供商预设 / 支持列表 / models.dev。
- 旧配置自动迁移（明确不做）。
