"""設定ファイルの読み込み・書き込み."""

import tomllib
from pathlib import Path

import tomli_w

from voivoi.config.schema import Config


def load_config(config_file: Path) -> Config | None:
    """設定を読み込む.

    Args:
        config_file: 設定ファイルパス

    Returns:
        設定ファイルが存在する場合はConfig、存在しない場合はNone。
        一部のキーのみ指定された場合はデフォルト値とマージする。
    """
    if not config_file.exists():
        return None

    with config_file.open("rb") as f:
        data = tomllib.load(f)

    return Config(**data)


def save_config(config: Config, config_file: Path) -> None:
    """設定をファイルに保存する.

    Args:
        config: 保存する設定
        config_file: 保存先ファイルパス
    """
    config_file.parent.mkdir(parents=True, exist_ok=True)
    data = config.model_dump(mode="json")
    with config_file.open("wb") as f:
        tomli_w.dump(data, f)
