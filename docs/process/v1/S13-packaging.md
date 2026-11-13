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
| 4 | 包升级不白跑一次全量装 | 同版本重装、或只改文档的小版本升级后，首启秒开（stamp 未变） |
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

# 3) 版本戳比对，变了才同步
STAMP="<data>/runtime/.stamp"
WANT="$(cat /usr/share/aris-project/.python-version)<app_version>"
[ "$(cat "$STAMP" 2>/dev/null)" = "$WANT" ] || {
  "$UV" sync --frozen --no-default-groups --project /usr/share/aris-project || exit 1
  printf '%s' "$WANT" > "$STAMP"
}

# 4) exec 运行时（不再触发 sync）
exec "$UV" run --frozen --no-sync --project /usr/share/aris-project aris "$@"
```

- **`<data>` 的解析要复用 `infra/paths.py` 的规则**（`ARIS_DATA_DIR` > 开发树 `./data` > 默认目录），
  启动器只做一次字符串拼接，不重写逻辑；GUI 拉起后端时显式注入 `ARIS_DATA_DIR`。
- **解释器只认 `.python-version`**：`requires-python` 是「允许范围」，不是「装哪个」。
- **`--no-default-groups`**：`dev` / `embedding` 都不装；本地 embedding 由用户开启时再
  `uv sync --frozen --group embedding`（同一个 venv，项目目录只读不影响）。
- **失败处理**：

  | 情况 | 表现 |
  |---|---|
  | 无网络 / 镜像不通 | 打印「首次运行需要联网下载 Python 与依赖」+ 可用的镜像环境变量（`UV_DEFAULT_INDEX` / `UV_PYTHON_INSTALL_MIRROR`）+ 原始错误末行 |
  | 磁盘不足 | 明确报「`<data>/runtime` 需要约 300 MB」 |
  | uv 版本过旧 | 报版本并提示升级；deb 内置的那份不存在此问题 |
  | stamp 在但 venv 被删 | 自动当作「未同步」，重跑 `uv sync` |

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
  `python-downloads = "manual"`；wrapper 必须显式 `uv python find 3.14`，找不到再 `uv python install 3.14`，
  失败提示 `emerge dev-lang/python:3.14`。
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
- 启动行为、连接文件读序、关窗语义见 `v1.0.0-prep.md` §4.15。

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

- **首个带 cp315 wheel 的 OpenVINO 版本**决定 `.python-version` 何时能升 3.15（见 §4.15）。
- **包升级后的 venv 重建成本**：目前 stamp 只看 Python 版本与包版本；
  若某次升级只改了依赖，包版本必然变，会触发一次 `uv sync`（增量，走缓存，可接受）。
- **mygo 版本迭代快**：`gui/` 开工时再评估 API，不锁定版本。
