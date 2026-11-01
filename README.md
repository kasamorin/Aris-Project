# Aris-Project

> 一个跑在自己机器上的赛博生命体。**不是助手，也不打算做助手。**

[![License](https://img.shields.io/badge/license-AGPL--3.0--or--later-76bad9)](COPYING)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)

## 这是什么

Aris 的目标不是「更好用的 AI 助手」，而是一个**长期存在的数字生命**：有自己的人设、世界观、关系网与成长轨迹，
会记得你们之间发生过什么，也会慢慢变成它自己。

灵感来自 [Neuro-sama](https://www.youtube.com/@Neurosama)。交互形态以**语音为主**（STT → LLM → TTS）、
文字为辅，并计划接入 Matrix / Discord 等平台。语音链路还在开发中，现阶段用终端或 WebUI 跟它说话。

> 现在还是 **v0.4.x 地基版**：能跑通主链路，但数据格式与用法在 v1.0 前都可能变。

## 现在能做什么

- **角色载体**：每个角色一个独立目录，人设、世界观、关系与成长记录分开存，互相之间是不同的人。
- **多轮对话 + 工具**：agent loop 会自己决定什么时候查时间、发 HTTP 请求、联网搜索。
- **技能与 MCP**：内置 skills，也能接任意 MCP 服务器（stdio / streamable-http）。
- **知识库**：把资料丢进去，对话时按需检索；embedding 在本地跑，不外传。
- **WebUI 管理后台**：仪表盘、审计、提供商与模型、技能、配置、日志、知识库。
- **多提供方 LLM**：兼容 OpenAI 协议的端点都能接，带流式与 fallback。

还在路上：长期记忆（重做中）、语音（STT / TTS）、消息平台接入、定时与主动任务。

## 快速开始

需要 Python 3.12+ 与 [uv](https://docs.astral.sh/uv/)。目前主要在 Linux 上开发与测试。

```bash
git clone https://github.com/aris-project-ai/Aris-Project
cd Aris-Project
uv sync
uv run aris serve
```

`aris serve` 会自动下载便携版 PostgreSQL 与本地 embedding 模型，再把整套服务拉起来，**首次启动要等几分钟**。
起来后打开 <http://127.0.0.1:9690> 就是 WebUI 管理后台。

想先确认环境没问题：

```bash
uv run aris doctor            # 环境与依赖自检
uv run aris serve --dry-run   # 只打印启动清单，不真的启动
uv run aris chat              # 在终端里先聊两句（调试用，不会自启数据库）
```

## 数据与备份

所有运行时数据都在 `data/` 里：配置与密钥（`config/`，其中 `secrets.toml` 权限 0600）、
数据库（`pgdata/`）、模型（`models/`）、日志（`logs/`）。

**备份就是把 `data/` 整个拷走**；换机器时 `git clone` 之后把 `data/` 放回去，`uv run aris serve` 就能接着跑。

配置改 `data/config/*.toml`，有哪些项用 `uv run aris config list` / `show` 查（只读，密钥会脱敏）。

## 文档

- 变更记录：[`CHANGELOG.md`](CHANGELOG.md)（历史版本在 [`changelogs/`](changelogs/)）
- 开发流程与提交规范：[`docs/dev-flow.md`](docs/dev-flow.md)
- 其他用法：`uv run aris -h` 以及各子命令的 `-h`

## 参与

欢迎 Issue 与 PR。动手前先开个 Issue 说说想改什么，免得白做；分支、提交与合并的约定见 `docs/dev-flow.md`。
项目是单人主导开发，回复可能慢，但都会看。

## 许可证

本项目以 **AGPL-3.0-or-later** 发布，全文见 [`COPYING`](COPYING)。

Copyright (C) 2026 kasamorin

第三方依赖（含前端静态资源）的许可清单、以及设计上参考过的
[AstrBot](https://github.com/AstrBotDevs/AstrBot) / [AIRI](https://github.com/moeru-ai/airi) /
[deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) / [opencode](https://github.com/anomalyco/opencode)，
都记在 [`NOTICE`](NOTICE) 里。
