# LLM 提供商与模型管理

> 状态：契约
> 代码入口：`src/aris/core/llm/`
> 事实查看：`aris llm list` / `aris llm check` / `aris llm fetch` / `aris llm missing list`
> 施工细节：`docs/process/v1/S7-llm-connection.md`

## 1. 模型

**provider = connection，只留一层。** 一个 provider 是一条连接（`base_url` + 密钥环境变量 + 一组模型），
协议由 provider 层的 `api_format` 决定。同一 `base_url` / 密钥要多种协议就建多条 provider，
不设「连接 + 模型实例」双层。

- **id 稳定**：provider id 与模型 id 创建后不可改；`name` / `request_name` / 元信息可改。
  provider id 不能含 `/`；模型 id 在 provider 内唯一，可以含 `/`。
- **协议族**：`openai_chat` / `openai_responses` / `anthropic_messages`（对话）、`systemone` /
  `openai_decisions`（决策）、`openai_live`（全双工）、`local`（本地托管，内部投影）。
- **不提供官方预设与支持列表**：用户手动建连接、填地址 / 密钥名 / 模型；`api_format` 只描述协议，
  不描述厂商。
- **无 models.dev**：元信息优先取提供商 `/models`；取不到就显示「未知」并允许手填。

## 2. 引用

模型统一写成 `provider/model`：

- 只按第一个 `/` 切分，`provider` 是 provider id，`model` 是剩余全部（可含 `/`）。
- 会话切换、角色绑定、`default_model`、`fallback_models[]`、`decision.model`、全双工选择
  全用这一语法。
- 跨 provider 的同名模型是不同条目；不做「按模型名全局搜索」。
- `default_model` 必配且必须是对话模型；缺失 / 无效 = 配置错误，不静默取第一个。

## 3. 配置

`data/config/providers.toml`（全局，不随档）；密钥只写环境变量名，真实值在 `secrets.toml`。

```toml
default_model = "deepseek/deepseek-flash"
provider_order = ["deepseek"]        # 只影响展示顺序与 fetch 默认对象，不参与 fallback
fallback_models = ["openrouter/deepseek/deepseek-v4-pro"]

[[providers.provider]]
id = "deepseek"
name = "DeepSeek"
api_format = "openai_chat"
base_url = "https://api.deepseek.com"
api_key_env = "DEEPSEEK_API_KEY"
timeout = 30

  [[providers.provider.models]]
  id = "deepseek-flash"
  name = "DeepSeek Flash"
  request_name = "deepseek-flash"
  context_length = 1000000
  capabilities = ["tools", "reasoning"]
  thinking_default = false
```

- `provider_order` 只决定提供商列表顺序与 `llm fetch` 的默认对象；降级顺序只看
  `fallback_models`。
- `fallback_models` 是顶层全局唯一一条链；每模型自带链与「同模型跨提供方自动切换」都已删除。
  执行时序见 `docs/process/v1.0.0-prep.md` §3.9。
- 旧键（`default_provider_order` / `transport` / `formats`）不迁移：加载即报配置错误，
  `aris llm check` 给新格式示例；CHANGELOG 标破坏性变更。

## 4. 管理

- `llm list`：提供商、协议、密钥状态、允许模型、默认与降级标记。
- `llm check`：schema、重复 id、默认 / fallback 引用、决策 / 全双工引用、密钥缺失、空模型列表；
  有错误非零退出；`doctor` 附摘要。
- `llm fetch [provider]`：从端点拉模型列表；无参数时取 `provider_order` 第一个。
  - **允许模型列表**（持久化）与**联网列表**（不持久化）分开；「+」把模型加入允许列表；
    再次获取仍按允许列表过滤。
  - 只新增、不自动删；本地有云无的模型可手动保留。
  - 写回前备份 `providers.toml`。
- `llm missing list`：只读查看从端点消失但被手动保留的模型记录；记录只用于事后查看，
  模型回归端点时清理记录，不自动写回配置。
- 能力测试：单模型测 + 该提供商允许模型一键全测；探测文本、极小图、假工具；
  实测到的上下文长度等真实值写回模型元信息。

## 5. 删除

删除 provider 或模型前扫描引用：`default_model`、`fallback_models`、会话当前模型、角色绑定、
`decision.model`、全双工选择、本地模型引用。任一命中就**拒绝删除**并列出位置；
引用源不可读时 fail closed，不先删后补。不做改名级联。

## 6. 边界

- **本地模型**（`local/<model>`）由 `inference` 投影，不写 `providers.toml`，管理入口在本地模型页；
  删除时执行同一套引用检查。详见 `docs/process/v1.0.0-prep.md` §4.29。
- **决策模型**只由 `decision.model` 选择，协议族 `systemone` / `openai_decisions` / 本地 decision；
  没有 fallback 链，失败降级到概率 / 规则（§4.12）。
- **全双工**能力标记 `full_duplex`，协议族 `openai_live`，配置 `full_duplex.toml`；
  不接 `stream_chat`，不参与 `default_model` / `/#model` / 对话 fallback（§4.28）。
- **错误处理**：必填配置缺失或非法 = 功能不可用 + error 日志；运行期请求失败按 §3.9 的占位与
  fallback 时序处理，不静默换模型。
