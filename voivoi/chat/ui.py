"""UI表示モジュール（Claude Code風スタイル）."""

from rich.console import Console
from rich.text import Text

console = Console()


def print_user_message(text: str) -> None:
    """ユーザーの発話を表示（> プレフィックス、背景色付き）."""
    styled = Text()
    styled.append("> ", style="bold bright_white")
    styled.append(text, style="on grey23")
    console.print(styled)


def print_ai_message(text: str) -> None:
    """AIの発話を表示（● プレフィックス）."""
    styled = Text()
    styled.append("● ", style="bold cyan")
    styled.append(text)
    console.print(styled)


def print_status(text: str) -> None:
    """ステータスメッセージを表示（薄いグレー）."""
    console.print(text, style="dim")


def print_info(text: str) -> None:
    """情報メッセージを表示."""
    console.print(text, style="bold")
