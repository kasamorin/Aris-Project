# S13 打包与分发

> 状态：规划中（命名 / 布局 / uv 来源 / 首启流程已定；等 S10、S11 的后端契约稳定后开工）
> 代码入口：`packaging/`（新建）、`gui/`（新建）、`.github/workflows/`
> 事实查看：`aris info`、`aris components list`、`aris doctor`
> 上游契约：`v1.0.0-prep.md` §4.15（GUI 与打包）、§3.8（外部组件清单）、§9（版本与渠道）

## 1. 一句话

把**后端 + WebUI 静态产物 + Go GUI** 打成一个 Arch 包、一个 deb 和一份 Gentoo ebuild，走**运行时 uv**（M1）：
包内不带 Python 与业务依赖，首启由 uv 在 `<data>/runtime/` 建环境。
打包**不解决**任何运行时问题——它只是把「`git clone` + `uv sync`」换成「装包 + 首启」。

## 2. 出口条件（DoD）

| # | 验收 | 判据 |
|---|---|---|
| 1 | Arch 包真机装得上、起得来 | `pacman -U` 后 `arisp serve` 正常，`arisp doctor` 全绿 |
| 2 | deb 在 Debian 13 容器里装得上、起得来 | `dpkg -i` 后 `arisp serve` 正常 |
| 3 | 首启不污染 `$HOME` | 装完首次运行后 `~/.local/share/uv`、`~/.cache/uv` **不存在** |
| 4 | 已同步时首启快 | 同版本重装、或只改文档的小版本升级后，热缓存下 `time arisp --version` < 1 s |
| 5 | 离线失败可读 | 断网首启给出「需要联网下载运行时」的明确提示与镜像开关，不是 traceback |
| 6 | 卸载干净 | `/usr/share/aris-project`、`/usr/lib/aris-project`、`.desktop`、图标全没了；`<data>` 保留 |
| 7 | CD 跑通 | tag 触发 → 两个包 + `SHA256SUMS` 挂到 Release |
| 8 | Gentoo ebuild 静态校验 | `pkgcheck scan` + `ebuild … manifest` / `--pretend` 无报错；**不做真机 `emerge`**，Release 说明标注「未经真机安装验证」 |

## 3. 命名与产物

| 东西 | 值 | 备注 |
|---|---|---|
| 包名（Arch / deb） | `aris-project` | Arch 官方 / AUR / Debian / PyPI 均无占用 |
| 桌面 app-id | `dev.arisproject.aris` | 发布后不可改 |
| 显示名（`.desktop` 的 `Name=`） | `Aris Project` | 与 `branding.APP_NAME` 一致（2026-11-06 定：`aris` 比 `airi` 宽泛，不能去掉 Project） |
| PATH 命令 | `arisp`（后端）、`arisp-gui`（GUI） | `aris` 已被 GNU Aris 占用，不能上 PATH |
| venv 内入口 | `aris`（`[project.scripts]`） | 只在 `<data>/runtime/venv/bin/` 里，不外露 |
| 产物 | `.pkg.tar.zst`、`.deb`、`SHA256SUMS` | 源码 tarball 由 GitHub 自动附 |
| Gentoo atom | `sci-ml/aris-project` | 先例：主树 `sci-ml/ollama`、GURU `sci-ml/aichat`；`net-im` 是 IM 本体 / 桥接，不适用 |

- **分发口径（2026-11-13 定）**：GitHub Releases 是唯一真相源；**进源只走 AUR**（`aris-project` 源码包）。
  Gentoo ebuild 只放仓库内单包目录、用户复制进本地 overlay；deb 只挂 Release。
  **GURU 等第二个维护者 / 贡献者再提**，Debian / Ubuntu 不建 apt 仓库（v1.x 有需求再上 OBS）。

- **`arisp` 只是壳**：找 uv → 建/校验环境 → `exec` venv 里的 `aris`。
- **双名规则（2026-11-06 定，硬性）**：`arisp` / `arisp-gui` **只**用于「以包形式安装的 Aris Project」；
  源码树、开发、CI、绝大多数文档一律写 `aris`。任何地方出现 `arisp`，都必须能明确回答
  「此处指的是安装包环境」。
- 平台：v1.0 只出 **x86_64 Linux**（Arch + Debian 13 + Gentoo）。AppImage / Windows / aarch64 归 v1.1。

## 4. 安装布局

| 路径 | 内容 | 归属 |
|---|---|---|
| `/usr/share/aris-project/` | 源码、`pyproject.toml`、`uv.lock`、`.python-version`、`COPYING` | 只读、架构无关 |
| `/usr/lib/aris-project/uv` | deb 内置的 uv（Arch 不装，走系统包） | 架构相关 |
| `/usr/lib/aris-project/arisp-gui` | Go GUI 二进制 | 架构相关 |
| `/usr/bin/arisp` | 启动器（脚本） | 两个包都有 |
| `/usr/bin/arisp-gui` | 软链到 `/usr/lib/aris-project/arisp-gui` | 两个包都有 |
| `/usr/share/applications/dev.arisproject.aris.desktop` | 桌面入口 | |
| `/usr/share/icons/hicolor/scalable/apps/aris-project.svg` | 图标 | |
| `/usr/share/doc/aris-project/copyright` | 许可证（本体的 AGPL 全文 + uv 的 MIT / Apache-2.0） | deb 必需；Arch 放 `/usr/share/licenses/aris-project/` |

- 不打包：`.venv/`、`data/`、`tests/`、`docs/`、`gui/` 源码、`packaging/`。
- 运行时环境与用户数据都在 `<data>/`（默认位置由 `infra/paths.py` 决定），包本身**不写**用户目录。

## 5. 首启流程（`/usr/bin/arisp`）

```sh
# 1) 定位 uv：包内优先，其次 PATH
UV="${ARIS_BUNDLED_UV:-/usr/lib/aris-project/uv}"
[ -x "$UV" ] || UV="$(command -v uv)" || { echo "缺少 uv" >&2; exit 1; }

# 2) 环境全部收进 <data>
export UV_PROJECT_ENVIRONMENT="<data>/runtime/venv"
export UV_PYTHON_INSTALL_DIR="<data>/runtime/python"
export UV_CACHE_DIR="<data>/runtime/uv-cache"

# 3) 解释器：只认 .python-version
PYVER="$(cat /usr/share/aris-project/.python-version)"
"$UV" python find "$PYVER" >/dev/null 2>&1 || "$UV" python install "$PYVER" || exit 1

# 4) 同步（可选组从 groups 文件读；已同步时约 30 ms）
GROUPS=""
if [ -f "<data>/runtime/groups" ]; then
  while IFS= read -r group; do
    [ -n "$group" ] && GROUPS="$GROUPS --group $group"
  done < "<data>/runtime/groups"
fi
# shellcheck disable=SC2086
"$UV" sync --frozen --no-default-groups $GROUPS --project /usr/share/aris-project || exit 1

# 5) exec 运行时（不再触发 sync）
exec "<data>/runtime/venv/bin/aris" "$@"
```

- **`<data>` 的解析要复用 `infra/paths.py` 的规则**（`ARIS_DATA_DIR` > 开发树 `./data` > 默认目录），
  启动器只做一次字符串拼接，不重写逻辑；GUI 拉起后端时显式注入 `ARIS_DATA_DIR`。
- **解释器只认 `.python-version`**：`requires-python` 是「允许范围」，不是「装哪个」。
- **`--no-default-groups`**：`dev` / `embedding` 都不装；本地 embedding 由用户开启时把 `embedding`
  写进 `<data>/runtime/groups`，下次启动由脚本追加 `--group embedding`（同一个 venv，
  项目目录只读不影响）。`uv sync` 默认 exact，**每次都必须把可选组传全**，否则会被当成多余包删掉。
- **不做版本戳**（2026-11-13 定稿）：每次启动交给 `uv python find/install` + `uv sync --frozen` 判定。
  已同步时实测约 30 ms（`Checked 121 packages in 1ms`）；好处是 venv 被删、包装到一半、依赖变了
  都能自愈，不需要维护「stamp 说已同步、实际缺包」的失效规则。首次启动与升级后仍然需要联网装包。
- **失败处理**：

  | 情况 | 表现 |
  |---|---|
  | 无网络 / 镜像不通 | 打印「首次运行需要联网下载 Python 与依赖」+ 可用的镜像环境变量（`UV_DEFAULT_INDEX` / `UV_PYTHON_INSTALL_MIRROR`）+ 原始错误末行 |
  | 磁盘不足 | 明确报「`<data>/runtime` 需要约 300 MB」 |
  | uv 版本过旧 | 报版本并提示升级；deb 内置的那份不存在此问题 |
  | venv 被删 / 包不完整 | `uv sync` 自动重建 / 补齐，不需要额外判断 |

**首启下载清单（2026-11-06 实测，2026-11-13 拆时间点）**

| 项 | 时机 | 大小（实测） |
|---|---|---|
| uv | 安装包（deb 内置；Arch 走系统包；Gentoo 用系统包） | 16 MB 压缩 |
| CPython（python-build-standalone） | `arisp` 启动器首启，**不一定下** | 73 MB |
| 基础依赖（`--no-default-groups`） | `arisp` 启动器首启 | 装好 129 MB（含工程本体） |
| 便携 PG + pgvector | `aris serve` 首启（或 `aris db init`） | 约 40 MB |
| 本地 embedding（torch / openvino + 模型） | 用户选「本地」时 | 1.5 GB+ |

- **Python 不一定下**：uv 默认 `python-preference = "managed"`（优先托管版），所以 Arch / deb
  默认会下 73 MB；Gentoo 的 `uv.toml` 设 `system`，用户 `emerge dev-lang/python:<版本>` 后就用系统的。
  deb 13 的系统 Python 不够新，必须下。
- 缓存统一指 `<data>/.uv-cache`；重装 / 重同步不重复下载，除非清 `data/`。
- 「本地 embedding 运行时未安装」不能裸抛 `ImportError`：`aris doctor` 要能检出、
  设置页给「安装本地模型运行时」、CLI 给对等命令（内部执行 `uv sync --frozen --group embedding`）。

## 6. Arch 包（`packaging/PKGBUILD`）

- `pkgname=aris-project`、`arch=('x86_64')`、`license=('AGPL-3.0-or-later')`
- `depends=('uv' 'gtk3' 'webkit2gtk-4.1')`
  — `uv` 用系统包（`extra` 0.13.7）；GTK / WebKitGTK 是 GUI 的运行期依赖（MyGO 经 dlopen 加载）。
- `makedepends=('go')`（GUI 二进制）。**当前不需要 Node**：WebUI 的前端资源是 vendored 静态文件；
  如果将来引入 `webui/` 工作区，再补 `nodejs` / `pnpm`。
- `build()`：`go build`（在 `gui/`）；`package()`：
  - `/usr/share/aris-project/` 放源码 + `uv.lock` + `.python-version` + `COPYING`；
  - `/usr/lib/aris-project/arisp-gui`；
  - `/usr/bin/arisp`（启动器）、`/usr/bin/arisp-gui`（软链）；
  - `.desktop`、图标、`/usr/share/licenses/aris-project/`。
- **实测验证**：`makepkg -s --noconfirm` 后 `pacman -U`，跑 DoD 1 / 3 / 4 / 6。

## 7. deb（`packaging/debian/`）

- 控制字段：`Package: aris-project`、`Architecture: amd64`、
  `Depends: libgtk-3-0t64, libwebkit2gtk-4.1-0`（trixie 的实际包名，已核实）。
- **内置 uv** 到 `/usr/lib/aris-project/uv`：Debian 没有 uv 二进制包
  （sid 只有源码包，且只产 `python3-uv-build`）。版本与 sha256 记进 `infra/components.py`。
- `/usr/share/doc/aris-project/copyright` 必须含：本体的 AGPL-3.0-or-later 全文 +
  uv 的 `LICENSE-MIT` 与 `LICENSE-APACHE` 全文（双许可，非 GPL，可随 AGPL 本体分发）。
- 用 `dpkg-deb --build` 直接打，不引入 debhelper 全流程（v1 手写；字段少、可控）。
- 安装后图标缓存 / `desktop-file-utils` 的刷新不是必需项，缺了也会在下次会话生效；
  若要加，走 `postinst` 里的 `command -v gtk-update-icon-cache && gtk-update-icon-cache ...`。

## 7b. Gentoo ebuild（`packaging/gentoo/`）

- 仓库只放**单包 ebuild 目录** `packaging/gentoo/sci-ml/aris-project/`：`aris-project-<version>.ebuild`
  + `metadata.xml` + `Manifest`；**不维护完整 overlay**，用户复制进本地 overlay 后 `emerge`。
- **不内置 uv**：`RDEPEND="dev-python/uv"`（主树已有 0.13.x）。源码放 `/usr/share/aris-project/`，
  GUI 随 ebuild 从源码构建（`dev-lang/go` + `go-module.eclass`），`.desktop` / 图标按 FHS 进 `/usr/share`。
- **首启不能依赖 uv 自动下 Python**：`dev-python/uv` 写的 `/etc/xdg/uv/uv.toml` 默认
  `python-downloads = "manual"`；wrapper 必须显式 `uv python find 3.15`，找不到再 `uv python install 3.15`，
  失败提示 `emerge dev-lang/python:3.15`。
- **只做静态校验**（`pkgcheck scan`、`ebuild … manifest`、`--pretend`），**不做真机 `emerge` 验证**；
  ebuild 注释与 Release 说明都标注「未经真机安装验证」。
- **不进 GURU**：等出现第二个维护者 / 贡献者再提；主树要 Gentoo dev 担保，不作为 v1 目标。

## 8. `.desktop` 与图标

```ini
[Desktop Entry]
Type=Application
Name=Aris Project
Comment=基于大语言模型的赛博生命体
Exec=arisp-gui
Icon=aris-project
Terminal=false
Categories=Utility;
StartupWMClass=dev.arisproject.aris
```

- 图标名用 `aris-project.svg`（不带反域名），`hicolor/scalable/apps/` 下；`Icon=` 写 `aris-project`。
- `StartupWMClass` 必须与 GUI 进程的 WM_CLASS 一致，否则任务栏会出现两个图标（S13 实测校准）。

## 9. GUI 构建

- `gui/` 独立 `go.mod`，**不 import 后端代码**，只认「后端 URL」这一个契约。
- MyGO（GTK3 + WebKitGTK 4.1，无 cgo），`mygo build` 只产可执行文件；
  `.desktop` / 安装器都用我们自己的配方（MyGO 的产物只作对照）。
- 运行期依赖：`gtk3` / `libgtk-3-0t64`、`webkit2gtk-4.1` / `libwebkit2gtk-4.1-0`。
- **GUI 只是前端，不得脱离后端独立运行**：连不上时按下面「启动行为」处理，不静默降级成空壳。

### 连接发现

- 后端在 WebUI **成功 bind 之后**写 `<data>/state/webui.json`（原子写：tmp + rename）：
  `{ addr, pid, started_at, app_version }`；**正常退出时删除**，崩溃残留由读者判失效。
- 读序（GUI 与 CLI 共用同一套）：
  ① `--addr` 启动参数 → ② 环境变量 `ARIS_WEBUI_ADDR` → ③ `webui.json`（校验 pid 存活 + `/api/health` 握手）
  → ④ 探测 `webui.toml` 里的默认端口 → ⑤ 连接页（可手填，记住上次）。
- 为什么不是裸端口文件：要多带 `pid` 才能判「文件是上次崩溃留下的」；要带 `started_at` / `app_version`
  才能提示「你连的是旧版本后端」。

### 启动与窗口

- **启动行为**：启动后**自动在本机找已运行的 `aris`**（健康检查 / 端口探测）——找到就连；
  **没找到就在后台拉起一个后端**（包安装调 `arisp`，源码环境调 `aris`）并等待就绪再连接；
  都失败则显示连接页（地址可填、记住上次、重试）。后端仍可独立运行。
- **关窗口只关 GUI，不停后端**：消息平台、autorun、记忆抽取继续跑；关窗前/关窗后给明确提示
  「后端仍在运行」，并提供**「关闭后端」按钮**。
- 「关闭后端」的实现：`POST /api/system/shutdown`（**需登录态 + CSRF**，走优雅停机，与重启同一条路径）；
  CLI 对等命令 `aris shutdown`（读连接文件 → 优先调该接口，失败退回对 pid 发 SIGTERM）。
  这是**前端路由**，不算「项目内部 HTTP 接口」（CMCB 的限制针对模块间通讯）。
- **GUI 有设置页**：后端地址（可填、可测连通）、启动时是否自动拉起后端、等待就绪超时、关闭窗口行为说明；
  GUI 自己的状态（窗口尺寸 / 上次地址）写 `<data>/state/gui.json`，随 `data/` 走。
- **版本号**：GUI **与主版本同步**（`1.0.0` 同号），用户少一个心智负担。
- **GUI v1 能力面**：单实例锁 + 记住窗口大小 / 位置 + 连接失败页；
  **托盘 / 通知 / 自动更新放 v1.x**（启动速度实测快，不需要靠托盘降低重启成本）。
- **单实例行为**：用 MyGO 的 `RequestSingleInstanceLock()`——后续实例返回 `false`，
  把命令行参数转发给第一个实例后**自己退出**；第一个实例在 `OnSecondInstance` 里**激活并前置已有窗口**。
  Wayland 的前台权限由 MyGO 用 `XDG_ACTIVATION_TOKEN` + `AllowForeground` 处理，我们不自己造。
  不做第二个窗口、不做多窗口。
- **登录态**：**不开免密通道**——GUI 不拿 token 绕过密码。webview 里走 WebUI 自己的登录页，
  cookie 持久化，7 天后重新登录。
- **webview 数据目录**：用 `App.SetPath(PathUserData, <data>/state/gui/)` 把 MyGO 的用户数据目录
  指到 `data/` 下，cookies / local storage 随 `data/` 一起迁移与备份（`state/` 属可重建层，
  丢了只是重新登录）。**未验证**：默认会话的实际落盘是否严格跟随 `PathUserData`——实现时实测一次；
  若不跟随，就退化为「登录态不随 `data/` 迁移」，并在设置页注明，不另造存储方案。
- **深链：v1 不做**，`.desktop` 不写 `MimeType=x-scheme-handler/...`。
  将来要做时 scheme 用 **`aris-project://`**（与包名一致，RFC 3986 允许 scheme 带连字符）。

## 10. CI 与发版

| tag | 触发 | 产物 |
|---|---|---|
| `alpha-v*`（develop） | smoke（`import aris`、`aris --version`、`aris serve --dry-run`） | **不产包** |
| `beta-v*` | 全量测试（含 PG + embedding）→ 打包 | Release 标 **prerelease** |
| `v*` | 同上 | 正式 Release |

- 构建环境：Arch 用 `archlinux:base-devel` 容器跑 `makepkg`；deb 用 `debian:trixie` 容器；
  GUI 在 `ubuntu-latest` 上 `go build`（无 cgo，产物可直接塞进两个包）；
  Gentoo 只跑 `pkgcheck scan` + manifest / 语法静态校验，**不做真机 `emerge`**。
- 产物命名：`aris-project-<version>-1-x86_64.pkg.tar.zst`、`aris-project_<version>_amd64.deb`；
  另出 `SHA256SUMS`。AUR 的 `PKGBUILD` 同步更新（源指向 Release tarball），ebuild 随仓库发布。
- 版本号唯一源仍是 `src/aris/__init__.py`，包版本由脚本读取，不手抄。

## 11. 验证清单（开工时逐条勾）

- [ ] `makepkg` 产出的包 `pacman -Ql` 无 `.venv` / `data/` / `tests/`
- [ ] 全新用户（无 `~/.local/share/uv`）首启能起来，且该目录仍不存在
- [ ] 断网首启的报错文案可读（不是 traceback）
- [ ] 重装同版本后首启 < 5 s
- [ ] 卸载后残留只剩 `<data>/`
- [ ] `.desktop` 在 KDE / GNOME 都能启动，任务栏只有一个图标
- [ ] `arisp-gui` 在无后端时能拉起后端（等待超时后给连接页）
- [ ] deb 在 `debian:trixie` 容器里 `dpkg -i` 无缺依赖
- [ ] ebuild 过 `pkgcheck scan`，`Manifest` 可生成（不要求真机 `emerge`）

## 12. 风险与待定

- **主进程 Python 3.15 的依赖边界**：`onnxruntime` / `openvino` 没有 cp315 wheel，embedding 已改走
  独立 worker（3.13），不再阻塞主进程升级；新增依赖前先确认有 cp315 或 abi3 wheel（见 §4.15 / §4.29）。
- **每次启动的同步检查**：热缓存实测约 30 ms（`Checked 121 packages in 1ms`）；首次启动与升级后
  需要联网并可能装包。不做版本戳，避免「stamp 说已同步、实际 venv 缺包」的假阴性。
- **mygo 版本迭代快**：`gui/` 开工时再评估 API，不锁定版本。
