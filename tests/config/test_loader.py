"""config/loader.py のテスト."""

import pytest

from voivoi.config.loader import load_config, save_config
from voivoi.config.schema import Config


class TestLoadConfig:
    """load_config のテスト."""

    def test_load_config_returns_none_when_file_not_exists(self, tmp_path) -> None:
        """設定ファイルが存在しない場合、Noneを返すこと."""
        # Arrange
        config_file = tmp_path / "config.toml"

        # Act
        config = load_config(config_file)

        # Assert
        assert config is None

    def test_load_config_reads_file_when_exists(self, tmp_path) -> None:
        """設定ファイルが存在する場合、ファイルから読み込むこと."""
        # Arrange
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[llm]\nmodel = "gemma2"\n\n[stt]\nlanguage = "en"\n\n[tts]\nenabled = false\n'
        )

        # Act
        config = load_config(config_file)

        # Assert
        assert config is not None
        assert config.llm.model == "gemma2"
        assert config.stt.language == "en"
        assert config.tts.enabled is False

    def test_load_config_merges_with_defaults_when_partial(self, tmp_path) -> None:
        """llmセクションのみ指定した場合、stt/ttsはデフォルト値が使われること."""
        # Arrange
        config_file = tmp_path / "config.toml"
        config_file.write_text('[llm]\nmodel = "phi3"\n')

        # Act
        config = load_config(config_file)

        # Assert
        assert config is not None
        assert config.llm.model == "phi3"
        assert config.stt.language == "ja"
        assert config.tts.enabled is True

    def test_load_config_raises_error_when_invalid_value(self, tmp_path) -> None:
        """不正な値が含まれる場合、エラーを発生させること."""
        # Arrange
        config_file = tmp_path / "config.toml"
        config_file.write_text('[llm]\nmodel = "invalid-model"\n')

        # Act & Assert
        with pytest.raises(Exception):
            load_config(config_file)


class TestSaveConfig:
    """save_config のテスト."""

    def test_save_config_creates_file_with_config_values(self, tmp_path) -> None:
        """設定をTOMLファイルに書き込むこと."""
        # Arrange
        config_file = tmp_path / "config.toml"
        config = Config()

        # Act
        save_config(config, config_file)

        # Assert
        assert config_file.exists()
        content = config_file.read_text()
        assert 'model = "llama3.1"' in content
        assert 'language = "ja"' in content
        assert "enabled = true" in content

    def test_save_config_creates_parent_directory(self, tmp_path) -> None:
        """親ディレクトリが存在しない場合、作成すること."""
        # Arrange
        config_dir = tmp_path / "nested" / "dir"
        config_file = config_dir / "config.toml"
        config = Config()

        # Act
        save_config(config, config_file)

        # Assert
        assert config_file.exists()
