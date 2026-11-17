# Sx 本地推理（本地模型 · 运行时 · 双工适配）

> 状态：细节已定，**批次编号待定**（2026-11-17；内容可开工，编号定了再改名）
> 代码入口：`src/aris/inference/`（待建）、`data/runtime/`、`data/models/`
> 事实查看：`aris inference status`（规划）、`aris inference models list`（规划）、`aris components list`
> 上游契约：`docs/process/v1.0.0-prep.md` §4.29（本地模型体系）、§4.28（双工）、§4.6（embedding）

## 1. 一句话

把「装运行时 → 下模型 → 起 worker → 管显存 → 供向量」这条本地推理链路做成**一个模块、一套协议、
一组可被 mock 的接口**，让 chat / 双工 / embedding 三类模型都能由用户自行添加，且**不污染主进程**。

## 2. 出口条件（DoD）

| # | 验收 | 判据 |
|---|---|---|
| 1 | 模块可开关且无副作用 | `modules.toml` 关掉 `inference` 后 `aris services list` 无 `inference.` 前缀；import 不注册服务、不登记迁移 |
| 2 | 运行时供给幂等 | `aris inference runtime install llama_cpp --variant cpu` 重复执行不重建；`runtime.json` 记录 backend / variant / python / packages |
| 3 | GPU 变体受闸门约束 | 探不到 CUDA 时装 `cu124` 直接拒绝并给出可行变体；探测结果不写进配置 |
| 4 | 模型下载可恢复 | 中断后续传；sha256 不符拒绝入库；`models list` 显示 model / artifact / backend / runtime 四层 |
| 5 | worker 协议可 mock | 纯 Python mock worker 跑通 load / chat / unload / ping；同一套 schema 校验器对 mock 与真 worker 双跑 |
| 6 | 帧与错误码受控 | 超过 16 MiB 的帧被断开并记 `proto.frame_too_large`；`proto.*` / `worker.*` / `runtime.*` / `model.*` / `device.*` / `busy.*` / `duplex.*` 各有触发用例 |
| 7 | 双工时序正确 | mock 双工跑通 open → audio_in → speak_start → audio_out → `playback.ack` → 打断五步；顺序错有用例失败 |
| 8 | 调度规则生效 | 同模型第二次 load 被拒；预算不足拒绝并列出可卸载项；**强制加载不记忆**（第二次仍拦）；空闲卸载按加载方式生效 |
| 9 | embedding 可用且可换 | Granite 97M ONNX 在 worker 内产出 384 维；prefix / pooling 来自 artifact；`store.embed` 经总线取向量；预热失败只降级不挂 serve |
| 10 | 无 GPU 不假绿 | 无 GPU 环境下真机用例 `pytest.skip` 并说明原因；mock 用例必须全绿 |
| 11 | 安全边界成立 | socket 0600 / 目录 0700；worker 环境变量不含任何密钥；`trust_remote_code` 全仓为 0 处 |
| 12 | 崩溃与孤儿可恢复 | 超过 `restart_max_attempts` 后停止并标 `failed`；残留 socket / pid 启动时被清理（有用例） |
| 13 | 日志不泄漏 | `[chat]` 行可关；`sk-` / `Bearer` / `api_key=` 被替换为 `[REDACTED]`；超长单条截断并标记 |
| 14 | 全检通过 | `bash scripts/check.sh` |

## 3. 运行时供给

### 目录

```text
data/runtime/
  llama_cpp/cu124/0.3.37/venv/
  vllm_omni/auto/0.32.0/venv/
  onnx_runtime/cpu/1.32.0/venv/
  current -> llama_cpp/cu124/0.3.37
  run/<worker>.sock          # 运行期 socket
```

- `data/runtime/` 属**可重建**层；`infra/paths.py` 的 `REBUILDABLE_PATHS` 要补 `runtime`。
- socket 文件 0600、目录 0700；worker pid 文件同目录，启动时清理残留。

### 安装

- 统一走 `uv`：`uv pip install --python <venv>/bin/python --extra-index-url <index> <spec>`。
- 装完写 `runtime.json`：`backend / variant / python / packages / aris_version / installed_at`。
- 变体名用 wheel 索引名（`cpu` / `cu124` / `rocm72` / `vulkan`），与 `llama-cpp-python` 的索引一致。

### 更新与卸载

- **蓝绿，不原地升级**：新版本装进新目录 → 校验 → 原子切 `current` → 保留旧目录一轮；失败切回。
- 卸载：删目录 + 清 socket / pid；被任何 artifact 引用时拒绝并列出占用方。

### 校验与探测

- 校验只做三件事：目录存在、解释器可执行、关键包能 `import`。不校验文件哈希（`uv` 已保证）。
  失败标 `runtime.broken` 并给重装指引。
- GPU 探测：`nvidia-smi` / `rocm-smi` / `vulkaninfo` + `/sys/class/drm`；**只作闸门、不落盘**。
- 磁盘：安装前按 wheel 体积 × 2 检查剩余空间；模型下载另算。
- 离线：支持自定义 index 与离线模式；离线时**禁止自动下载**，缺什么直接报错。

### 版本事实（2026-11-17 实测）

- `llama-cpp-python` 0.3.37 的 GPU wheel 是 `py3-none`，不绑 Python 版本；`manylinux_2_35` 要求
  glibc ≥ 2.35；CUDA wheel 不带 CUDA runtime / cuBLAS，要系统驱动 + 匹配 toolkit。
- `vllm-omni` 稳定版 0.32.0（0.33 只有 rc1），`requires-python >=3.11,<3.14`。
- `onnxruntime` 1.32.0 有 cp311–cp314；**没有 cp315**，所以 embedding 只能跑 worker。
- 所有 worker 统一 **Python 3.13**；主进程 v1.0 目标 **3.15**。

## 4. 模型目录与下载

### 四层

| 层 | 字段要点 |
|---|---|
| `model` | id、显示名、上游仓库、license、`verified`、备注；「同一模型单实例」按这层判定 |
| `artifact` | id、model_id、格式（gguf / safetensors / onnx）、量化、文件清单（path / sha256 / size）、`min_vram_mb` |
| `backend` | `llama_cpp` / `vllm_omni` / `onnx_runtime`；由格式决定，可多个 |
| `runtime` | Python 版本 + wheel 变体 + 后端包版本 |

### 能力来源

1. 模型文件元数据：HF `config.json`、GGUF header、ONNX 输出形状；
2. 下载源 API：license、`base_model`、语言、gated 状态、文件体积；
3. 后端声明：该后端能提供 tools / duplex / multi-session / 流式中的哪些。

加载后**探测校正**实际值（可用上下文、实际 `max_sessions`、pooling 是否生效），不一致记日志并以实际值为准。

### 下载

- 来源：HF / ModelScope；支持镜像与离线。
- 断点续传 + sha256 校验；校验失败拒绝入库并保留可重试状态。
- 磁盘：下载前检查空间，不足就拒绝并给出需要多少。

## 5. worker 协议

### 连接与分帧

- 每 worker 一条 Unix domain socket，多 session 复用，session 用 ID 区分。
- 帧格式 `[type: u8][length: u32 BE][payload]`；`0x01` = CONTROL（msgpack map），`0x02` = AUDIO（裸 PCM16LE）。
- 控制与音频共用同一帧头，不混用两套读取器。

### 硬约束

- 一律 `read_exact`：Unix socket 会短读。
- 单帧上限 16 MiB，超限断开并记 `proto.frame_too_large`。
- 统一大端，不做自适应。
- 读循环独立成 task，**不放进可取消分支**（取消会丢已读字节）。

### 音频块

20 ms 一块：16 kHz 入 640 B、24 kHz 出 960 B；线上只走 PCM16LE 单声道，采样率由能力声明。

### 消息族

```text
握手   hello{protocol{major,minor}, backend, backend_version, python}
       ready{protocol, capabilities}
生命周期 load / loaded / unload / unloaded / ping / pong / shutdown
chat   chat.start / chat.delta{seq, kind} / chat.end{finish_reason, usage}
       chat.cancel / chat.error{code, retryable}
双工   duplex.open{instructions, voice, ref_audio} / duplex.opened
       duplex.audio_in{session, seq, pcm} / duplex.text_in
       duplex.text / duplex.audio_out{seq, pcm, rate} / duplex.event
       duplex.truncate{item_id, audio_end_ms} / duplex.close
```

### 背压与取消

- 主进程 → worker 的 `audio_in` 用有界队列，满了**停发不丢帧**。
- worker → 主进程的音频以 `duplex.event{name:"playback.ack"}` 为水位，未播完的音频不无限缓冲。
- 取消按 `req_id` / `session_id` + `seq`；取消后 worker 停止生成并以 `finish_reason="cancelled"` 收尾。
- **已发出的音频收不回**：由主进程发 `duplex.truncate` 截断播放（§4.28 硬约束 3）。

### 错误码

| 命名空间 | 典型码 | 处置 |
|---|---|---|
| `proto.*` | 版本不兼容 / 未知消息 / 帧超限 | 断开 |
| `worker.*` | 崩溃 / 超时 / 孤儿 | 重启或标记失败 |
| `runtime.*` | venv 缺失 / wheel 不匹配 | 不可重试，提示重装 |
| `model.*` | 不存在 / 校验失败 / 格式不符 | 不可重试 |
| `device.*` | 无设备 / OOM | 可重试（降量化 / 换变体） |
| `busy.*` | `session_limit` / `model_loading` | 可重试（带建议） |
| `duplex.*` | `text_unsupported` 等能力缺失 | 不可重试 |

每条带 `code` / `message` / `retryable` / 可选 `detail`。

### 版本协商与看门狗

- `major` 不同直接拒绝；`minor` 向后兼容；能力一律靠 `ready.capabilities` 分支，不靠版本号猜。
- `ping` 5 s，连续 3 次无 `pong` 判僵死 → kill + 重启；退出码非 0 记 `worker.crashed`。
- 启动清理残留 socket / pid（对齐 PG 的同类教训）。

## 6. 双工适配

> 模型事实见 `docs/process/v1.0.0-prep.md` §4.29；本节只写映射与时序。

### 内核事件

| 内核事件 | 来源（vLLM-Omni） |
|---|---|
| `duplex.opened{capabilities}` | `session.created` |
| `duplex.speech_started` / `stopped` | `input_audio_buffer.speech_started` / `stopped` |
| `duplex.speak_start{response_id, item_id}` | `response.speak` |
| `duplex.audio{seq, pcm, ms}` | `response.output_audio.delta` |
| `duplex.text_delta{seq}` | `response.output_text.delta` |
| `duplex.listen` | `response.listen` |
| `duplex.ended{reason}` | `response.done` |
| `duplex.played_ms{response_id, ms}` | 我们 → `playback.ack` |

`reason` 取值：`barge_in` / `client_cancelled` / `new_response` / `eos`。

### 播放确认

- 播放端每 50 ms 上报累计 `played_ms`；后端据此提交历史（MiniCPM-o 用 `playback_commit_policy=ack_only`）。
- **收到 ≠ 播放**；Aris 的 transcript 与记忆写入都以 `history_committed` 为准，不自己先记。

### 打断（顺序固定）

1. 本地停播；
2. 取最终 `played_ms`；
3. `response.cancel`（仍在生成时）；
4. `conversation.item.truncate`（带 `item_id` / `content_index` / `audio_end_ms`）；
5. `output_audio_buffer.clear`。

截断后的 transcript 标记「未播完」，注入给其他角色时不带被截掉的部分。

### 重连

- 保存 `session_id` + `resume_token` + `last_received_server_event_seq`。
- `session.resumed` → 重放积压事件继续。
- `session.expired` / `session.resync_required` → **新建会话并明确告知上下文已断**。
- `session.replaced` → 同一会话被另一连接顶替，主动让位并记日志。
- 后端心跳 `session.heartbeat_ack` 与 worker 的 `ping` 分开：前者会话层，后者进程层。

### 能力差异

| 能力 | 处理 |
|---|---|
| `supports_barge_in=false` | 禁用打断交互并在 UI 明示 |
| `supports_audio_truncate=false` | 只停播 + cancel，记 `duplex.truncate_unsupported` |
| `tools=false` | 配了工具就启动告警并禁用 |
| `input_modes` 不含 text | 文本输入走 chat 模型 |
| `chunk_period_ms` | 直接作为 UI「反应延迟」预期（MiniCPM-o = 1000 ms） |

## 7. 调度与生命周期

### 状态机

```text
available → installing → installed → loading → ready ⇄ busy → unloading → installed
                                   ↘ failed{code}
```

同一模型单实例；切换 artifact 等于卸载再加载。

### 并发

| 场景 | 行为 |
|---|---|
| chat | 请求串行 + 有界队列，满了返回 `busy.queue_full` |
| 双工支持多会话 | 并行，上限 `max_sessions` |
| 双工不支持多会话 | 第二路返回 `busy.model_busy`，带占用角色与建议 |

### 显存预算

- `已加载占用 + 本次需求 ≤ 预算` 才允许加载；预算可被 `max_vram_mb` 覆盖。
- 不足时**拒绝并列出可卸载项与各自占用**；默认**不自动驱逐**。
- **强制加载每次都要确认**：只对当次生效、不持久化、不记忆上次选择（占用情况随时会变）。
  失败记 `device.oom` 并保持原状态；成功仅本次标 `forced` 供审计。

### 空闲卸载

| 加载方式 | `idle_unload_min` |
|---|---|
| 预热 / 显式加载（`auto_load=true`，角色当前绑定） | 0（不自动卸） |
| 按需加载（试模型 / 临时切换） | 10 |
| embedding | 0（常驻） |

- 手动卸载任意状态可用；使用中弹二次确认并说明会中断当前回复。
- 按 `auto_load` 预热；**embedding 必预热**。

## 8. embedding

- provider 两类：`local`（本 worker，onnx_runtime 为主、openvino 可选）与 `remote`（OpenAI 兼容 HTTP）。
- v1 实际只能走 worker（主进程 3.15 没有 onnxruntime wheel）。
- 库绑模型身份；多维度按库记录；换模型走影子表重建。
- query / document 前缀与 pooling 由 artifact 声明，不按模型名硬编码。
- 批大小 / 线程进 `inference.toml`；CPU 线程默认取核数一半、上限 8。
- 预热失败降级：检索与记忆写入降级并记 error，不挂 serve。

## 9. 施工顺序

| 步 | 内容 | 依赖 |
|---|---|---|
| T1 | 模块骨架 + `register()` + 服务前缀 + paths 补 `runtime` | 无 |
| T2 | 运行时供给：目录、安装、蓝绿、校验、探测 | T1 |
| T3 | 模型目录 + 下载（四层、校验、续传、磁盘） | T1 |
| T4 | worker 协议 + mock worker + schema 校验器 | T1 |
| T5 | `llama_cpp` 后端（chat） | T2 / T3 / T4 |
| T6 | `onnx_runtime` 后端（embedding）+ `store` 侧改走总线 | T2 / T3 / T4 |
| T7 | `vllm_omni` 后端 + 双工适配（事件 / 时序 / resume） | T2 / T3 / T4 |
| T8 | 调度（状态机、队列、预算、强制加载、空闲卸载） | T5 / T6 / T7 |
| T9 | 页面数据接口（只给数据模型，页面由开发者设计） | T8 |

T5 之后即可端到端试跑 chat；T6 决定 embedding 能否切换；T7 是唯一需要 GPU 的一步。

## 10. 测试

- **mock 优先**：CI 全链路用 mock worker，不加载模型、不需要 GPU。
- **契约测试**：同一套 schema 校验器对 mock 与真 worker 双跑，防协议漂移。
- **GPU 集成**：跑 chat（llama.cpp）与双工（vLLM-Omni）各一条最短路径，标记为可选档位。
- **性能基准**：记录加载耗时、首 token 延迟、embedding 单条延迟，只做趋势对比不作门槛。
- **无 GPU 不假绿**：真机用例在无 GPU 时 `pytest.skip` 并写明原因。

## 11. 页面结构（2026-11-18 定稿方向）

> 给画图用：只写页面、元素、状态；不列字段名。界面文案用中文（草图上的英文只是绘图工具限制）。

**页面职责**：这台机器能跑什么、装了什麼、现在在跑什么；能装运行时、加模型、加载切换。

### 主页面

- 标题 + 右上动作：刷新 / 新建（加模型）
- 模型列表：**卡片网格**，一张卡 = 一个模型
  - 卡内：名称、类型徽章（普通 / 双工 / embedding）、当前文件与后端、状态行、两个圆形按钮
    （运行/停止、管理）
  - 状态行要能区分：未下载 / 已下载未加载 / 加载中 / 运行中 / 忙碌 / 卸载中 / 失败
- 卡片之外、不占主区的三样：
  - **运行时**：折叠成一行（后端 × 变体 × 版本 + 装/更新），没装时是提示条
  - **下载**：进度出现在卡片上；多任务时另有一条队列入口
  - **硬件**：一行状态（可用 GPU / 仅 CPU / 显存余量），点开看明细
- 必须覆盖的状态：首次四空、加载中、下载中、校验中、显存不足、运行时损坏、下载失败、
  离线、无 GPU（正常态）

### 管理弹窗（新建 / 管理共用）

1. **来源三选一**：
   - 推荐模型：从内置清单选，程序自动处理文件与校验，用户不填路径
   - 从网络下载：贴 HF / ModelScope 链接或仓库名；能取到上游 sha256 就自动校验
   - 从文件导入：选本地文件 → **弹窗声明风险**（会复制一份到 `data/models/`、原文件不动、
     本地文件通常没有上游校验、磁盘占用会翻倍）→ 确认后复制
2. **类型**：普通大语言模型 / 全双工模型 / embedding（决定后续可用参数与后端）
3. **文件列表**：同模型的多个文件都在这里（格式 / 量化 / 体积 / 能否在当前硬件跑 / 推荐标记），
   未下载的可直接下载；已下载的可选为「当前」
4. **运行参数**：上下文、GPU 层数、线程（带默认值）
5. **加载方式**：是否随启动自动加载
6. **限制说明**：如「双工模式下不支持工具调用」
7. 动作：保存 / 下载 / 加载 / 卸载 / 删除 / 打开上游仓库
8. embedding 类型额外一个动作：**设为默认**（知识库与记忆使用）

### 确认弹窗

- **加载确认**（仅显存不够）：需要多少 / 现有多少 / 差多少 / 可卸载项 / 取消 / 仍然加载（仅本次）
- **卸载确认**（仅使用中）：谁在用 / 会中断什么 / 取消 / 仍然卸载

### 版式约束

- 长在右侧内容区，标题左上、动作右上；手机侧栏为覆盖式
- 管理**用弹窗，不用右侧抽屉**（带鱼屏下抽屉太窄）
- 深浅色都要成立

### 参照而非照搬

同模型多文件在业界的两种做法：**LM Studio 式**（按模型分组、展开文件列表、标硬件适配与推荐）；
**Ollama 式**（每个量化是独立 tag，扁平列出）。Aris 取前者：卡片按模型分组，文件列表放管理弹窗，
避免同一模型出现多张卡。

## 12. 安全与生命周期（2026-11-18 定）

### 权限边界

- socket 文件 0600、所在目录 0700：同机其他用户连不上（不开 TCP 已是第一层）。
- worker 与主进程同用户，**不提权、不 setuid**；`umask 077`，日志与临时文件默认他人不可读。
- worker 环境变量只传必要的（线程数、设备、日志级别），**不传 `secrets.toml` 里的任何 API key**。

### 资源与崩溃

- v1 **不做 cgroup**：需要 root 或 systemd，与「便携、不注册系统服务」冲突。
- CPU 推理给 worker 加 `nice`（默认 +5），避免打满整机导致主进程与 WebUI 卡顿。
- OOM 只杀 worker，主进程不受影响；状态转 `failed.device_oom`。
- 崩溃重启可配：

  ```toml
  [worker]
  restart_max_attempts = 3
  restart_window_s = 600
  ```

  退避 2 / 8 / 30 秒；超过次数**停止自动重启**，页面给「重试」。反复崩溃通常是模型文件问题，重启无意义。

### 孤儿清理

- worker 写 pid 文件与 socket；启动时逐个检查：pid 是否存活、命令行是否仍是本项目的 worker。
- 不是就清掉 socket / pid；是就拒绝启动并提示「已有实例在跑」。

### 代码执行边界（硬规则）

- **禁止 `trust_remote_code`**：三个内置后端都在后端内部实现模型结构，不需要执行模型仓库里的 Python。
- 代价要写在页面：需要自定义代码的模型**不能装**，不做「我知道风险，放行」的开关。
- GGUF 里的 chat template 交给 llama.cpp 渲染（C++），不由 Python 侧执行 Jinja。

### 日志

- **单文件**：沿用 `data/logs/YYYY-MM-DD/aris.log`，不新增文件、不新增保留策略（现有 10 MB 轮转 / 30 天）。
- 行内带频道：`[boot]` / `[chat]` / `[tool]` / `[llm]` / `[worker]`。
- `[chat]` 行默认写、可整体关闭；关闭后运维日志一条不少。
- 格式：一行一条，`cid` / `session` / `turn` 作关联键；工具调用与结果各一行（参数记摘要、结果只记字节数）。
- 媒体只写占位：`[image 1200x800]` / `[audio 3.2s]`，不落原文。
- 写入前脱敏：`sk-…` / `Bearer …` / `api_key=…` → `[REDACTED]`；单条超长截断并标 `…[+N]`。
- `aris logs export` 导出时**默认剔除 `[chat]` 行**，避免对话原样进 issue。
- 审计（`core/audit.py`）仍只在内存环形缓冲，**不落盘、不含内容**。

### 文件完整性

- 下载完成时算一次 sha256，写入 manifest，并记 `size + mtime`。
- 加载时只比对 `size + mtime`；不符则转「需重新校验」，不做无条件全量哈希（8 GB 文件太重）。
