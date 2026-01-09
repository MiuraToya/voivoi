"""設定ファイルのパス定義."""

from pathlib import Path


def get_config_dir() -> Path:
    """設定ディレクトリのパスを取得する."""
    return Path.home() / ".config" / "voivoi"


def get_config_file() -> Path:
    """設定ファイルのパスを取得する."""
    return get_config_dir() / "config.toml"
