"""config/schema.py のテスト."""

import pytest
from pydantic import ValidationError

from voivoi.config.schema import (
    Config,
    LLMConfig,
    LLMModel,
    STTConfig,
    STTLanguage,
    TTSConfig,
)


class TestLLMConfig:
    """LLMConfig のテスト."""

    def test_llm_config_has_default_model(self) -> None:
        """デフォルトモデルが llama3.1 であること."""
        # Act
        config = LLMConfig()

        # Assert
        assert config.model == "llama3.1"

    def test_llm_config_accepts_valid_model(self) -> None:
        """許可されたモデル名を受け入れること."""
        # Act & Assert
        for model in LLMModel:
            config = LLMConfig(model=model)
            assert config.model == model

    def test_llm_config_rejects_invalid_model(self) -> None:
        """許可されていないモデル名を拒否すること."""
        # Act & Assert
        with pytest.raises(ValidationError):
            LLMConfig(model="invalid-model")  # type: ignore[arg-type]


class TestSTTConfig:
    """STTConfig のテスト."""

    def test_stt_config_has_default_language(self) -> None:
        """デフォルト言語が ja であること."""
        # Act
        config = STTConfig()

        # Assert
        assert config.language == "ja"

    def test_stt_config_accepts_valid_language(self) -> None:
        """許可された言語コードを受け入れること."""
        # Act & Assert
        for lang in STTLanguage:
            config = STTConfig(language=lang)
            assert config.language == lang

    def test_stt_config_rejects_invalid_language(self) -> None:
        """許可されていない言語コードを拒否すること."""
        # Act & Assert
        with pytest.raises(ValidationError):
            STTConfig(language="invalid")  # type: ignore[arg-type]


class TestTTSConfig:
    """TTSConfig のテスト."""

    def test_tts_config_has_default_enabled(self) -> None:
        """デフォルトで TTS が有効であること."""
        # Act
        config = TTSConfig()

        # Assert
        assert config.enabled is True


class TestConfig:
    """Config のテスト."""

    def test_config_has_all_sections_with_defaults(self) -> None:
        """全セクションがデフォルト値で初期化されること."""
        # Act
        config = Config()

        # Assert
        assert config.llm.model == "llama3.1"
        assert config.stt.language == "ja"
        assert config.tts.enabled is True

    def test_config_accepts_partial_override(self) -> None:
        """一部の値のみオーバーライドできること."""
        # Arrange
        llm = LLMConfig(model=LLMModel.GEMMA2)

        # Act
        config = Config(llm=llm)

        # Assert
        assert config.llm.model == "gemma2"
        assert config.stt.language == "ja"
        assert config.tts.enabled is True
