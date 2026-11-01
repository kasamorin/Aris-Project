# 变更记录

> 面向**使用者**：写可见变化与操作影响，不写内部重构细节。
> 本文件只保留 `[Unreleased]` 与**当前最新版本**两段；历史版本在 `changelogs/<版本>.md`。
> 发版时把上一版本整段移入 `changelogs/<版本>.md`，并在本文件顶部写新版本段。

## [Unreleased]

### 新增

- 仓库 CI：PR 与 `develop` / `main` 推送自动跑 ruff / mypy / 单测；发版 PR 额外起真 PostgreSQL
  与 embedding 跑全量测试；alpha tag 跑轻量启动自检。
- `NOTICE`：第三方依赖许可与设计参考项目（AstrBot、AIRI 等）。
- `scripts/release.sh`：一条命令完成发版准备（校验、切分支、bump、检查），不推送、不打 tag。

### 改进

- 变更记录改为根 `CHANGELOG.md` 只留最新版本，旧版本归档到 `changelogs/`。
- README 重整：快速开始、数据与备份、参与方式更清楚，补版本与 Python 徽章。
- 发版流程定稿：`release/` 分支单一 PR → 原生 auto-merge → tag → `main` 回合并 `develop`。

### 修复

### 升级注意

- 运行环境要求提高到 **Python 3.14+**（`requires-python = ">=3.14"`），旧版 Python 无法安装。

## [0.4.4] - 2026-10-30

### 亮点

地基版：把「数据放哪、配置从哪读、CLI 怎么查」定死，并堵掉架构口子。

### 新增

- `aris info` / `aris config path|list|show|validate|env` / `aris modules list|status|enable|disable`：
  路径、配置、模块开关都能从 CLI 直接查（只读，密钥脱敏）。
- 模块开关（`data/config/modules.toml`）：store / knowledge / mcp / behavior / webui / character / voice
  可单独关闭；关掉的模块不装配，依赖方跳过并记日志，程序不退出。
- `data/config/` 统一配置：首次启动自动播种模板；密钥只进 `secrets.toml`（0600）。
- `data/state/llm-list-missing.json`：记录同步后从端点消失的模型，供只读查看。

### 改进

- 数据目录统一由 `ARIS_DATA_DIR` > 开发树 `./data` > `~/.project-aris` 解析。

### 修复

- LLM 配置/密钥迁移后缺 key 的静默降级问题；路径与配置来源不一致导致的启动失败。

### 升级注意

- 不再有 `.env`：配置一律 TOML，临时覆盖用进程环境变量。
- `knowledge.toml` 的 `enabled` 并入 `modules.toml`。
- 许可证切换为 **AGPL-3.0-or-later**。
