"""对话指令：解析与帮助文本。

所有以 / 开头的对话指令集中在这里定义，TUI 与非 TUI 回退共用。
parse_command 返回结构化 ParsedCommand，由调用方（ChatSession.run_command）
统一分发执行。
"""

from __future__ import annotations

from dataclasses import dataclass

# 指令名 -> 说明（按展示顺序）
COMMANDS: dict[str, str] = {
    "/#help": "查看可用指令",
    "/#clear": "清空屏幕",
    "/#new-s": "开启新会话（新 `session_id`，清空对话历史）",
    "/#model": "查看或切换模型（`/#model <id>`）",
    "/#quit": "退出对话（同 `/#exit`）",
    "/#exit": "退出对话（同 `/#quit`）",
}

# 提示符（与 TUI / 回退模式一致）
PROMPT_USER = "你> "
PROMPT_ARIS = "Aris: "

COMMAND_HELP = (
    "可用指令：\n"
    + "\n".join(f"  {name:<10} {desc}" for name, desc in COMMANDS.items())
    + ("\n交互：Enter 发送，Shift+Enter 换行；回复期间双击 ESC 可中断；Ctrl-C 退出。")
)


@dataclass(frozen=True)
class ParsedCommand:
    """解析结果：指令名（不含 / 前缀，小写）+ 可选参数。"""

    name: str
    arg: str = ""


def parse_command(text: str) -> ParsedCommand | None:
    """解析对话指令；输入不是指令时返回 None。

    TUI 与平台统一用 `/#` 前缀：`/#help`、`/#new-s` 等。解析时剥掉 `/#`。
    """
    stripped = text.strip()
    if not stripped.startswith("/#"):
        return None
    parts = stripped.split(maxsplit=1)
    name = parts[0][2:].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""
    return ParsedCommand(name=name, arg=arg)
