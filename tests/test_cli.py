"""CLI のテスト."""

from unittest.mock import patch

from typer.testing import CliRunner

from voivoi.cli import LOGO, app, run


runner = CliRunner()


def test_run_prints_logo(capsys):
    run()
    captured = capsys.readouterr()
    assert LOGO in captured.out


class TestConfigInit:
    """voivoi config init コマンドのテスト."""

    def test_config_init_creates_file_when_not_exists(self, tmp_path) -> None:
        """設定ファイルが存在しない場合、デフォルト値で作成すること."""
        # Arrange
        config_file = tmp_path / "config.toml"

        # Act
        with patch("voivoi.config.cli.get_config_file", return_value=config_file):
            result = runner.invoke(app, ["config", "init"])

        # Assert
        assert result.exit_code == 0
        assert config_file.exists()
        assert "Created" in result.stdout
        assert str(config_file) in result.stdout

    def test_config_init_shows_config_values_after_creation(self, tmp_path) -> None:
        """作成後に設定内容を表示すること."""
        # Arrange
        config_file = tmp_path / "config.toml"

        # Act
        with patch("voivoi.config.cli.get_config_file", return_value=config_file):
            result = runner.invoke(app, ["config", "init"])

        # Assert
        assert "llama3.1" in result.stdout
        assert "ja" in result.stdout
        assert "true" in result.stdout.lower()

    def test_config_init_shows_message_when_file_exists(self, tmp_path) -> None:
        """設定ファイルが既に存在する場合、何が存在するかを示すメッセージを表示すること."""
        # Arrange
        config_file = tmp_path / "config.toml"
        config_file.write_text('[llm]\nmodel = "llama3.1"\n')

        # Act
        with patch("voivoi.config.cli.get_config_file", return_value=config_file):
            result = runner.invoke(app, ["config", "init"])

        # Assert
        assert result.exit_code == 0
        assert "already exists" in result.stdout
        assert str(config_file) in result.stdout
