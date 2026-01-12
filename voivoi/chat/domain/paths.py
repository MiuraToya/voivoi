"""チャットファイルのパス定義."""

from pathlib import Path


def get_chats_dir() -> Path:
    """チャットディレクトリのパスを取得する."""
    return Path.home() / ".local" / "share" / "voivoi" / "chats"
