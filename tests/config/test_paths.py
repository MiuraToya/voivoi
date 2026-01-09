"""config/paths.py のテスト."""

from pathlib import Path

from voivoi.config.paths import get_config_dir, get_config_file


class TestGetConfigDir:
    """get_config_dir のテスト."""

    def test_get_config_dir_returns_path_under_home(self) -> None:
        """設定ディレクトリがホームディレクトリ配下であること."""
        # Arrange
        home = Path.home()

        # Act
        result = get_config_dir()

        # Assert
        assert result == home / ".config" / "voivoi"


class TestGetConfigFile:
    """get_config_file のテスト."""

    def test_get_config_file_returns_config_toml_path(self) -> None:
        """設定ファイルパスがconfig.tomlを指すこと."""
        # Arrange
        expected = get_config_dir() / "config.toml"

        # Act
        result = get_config_file()

        # Assert
        assert result == expected
