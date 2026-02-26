"""設定スキーマ定義."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator


class STTLanguage(StrEnum):
    """許可されたSTT言語コード."""

    JA = "ja"
    EN = "en"


class LLMConfig(BaseModel):
    """LLM設定."""

    model_config = ConfigDict(extra="forbid")

    model: str = "gemma3"
    system_prompt: str = (
        "あなたは音声アシスタントです。簡潔に日本語で応答してください。"
    )

    @field_validator("model")
    @classmethod
    def model_must_not_be_blank(cls, v: str) -> str:
        """モデル名が空でないことを検証する."""
        if not v.strip():
            msg = "モデル名は空にできません"
            raise ValueError(msg)
        return v


class STTConfig(BaseModel):
    """STT設定."""

    model_config = ConfigDict(extra="forbid")

    language: STTLanguage = STTLanguage.JA
    model: str = "medium"


class TTSConfig(BaseModel):
    """TTS設定."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True


class Config(BaseModel):
    """アプリケーション設定."""

    model_config = ConfigDict(extra="forbid")

    llm: LLMConfig = LLMConfig()
    stt: STTConfig = STTConfig()
    tts: TTSConfig = TTSConfig()
