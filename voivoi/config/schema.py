"""設定スキーマ定義."""

from enum import StrEnum

from pydantic import BaseModel


class LLMModel(StrEnum):
    """許可されたLLMモデル."""

    LLAMA3_1 = "llama3.1"
    LLAMA3_2 = "llama3.2"
    GEMMA2 = "gemma2"
    PHI3 = "phi3"
    MISTRAL = "mistral"


class STTLanguage(StrEnum):
    """許可されたSTT言語コード."""

    JA = "ja"
    EN = "en"


class LLMConfig(BaseModel):
    """LLM設定."""

    model: LLMModel = LLMModel.LLAMA3_1


class STTConfig(BaseModel):
    """STT設定."""

    language: STTLanguage = STTLanguage.JA


class TTSConfig(BaseModel):
    """TTS設定."""

    enabled: bool = True


class Config(BaseModel):
    """アプリケーション設定."""

    llm: LLMConfig = LLMConfig()
    stt: STTConfig = STTConfig()
    tts: TTSConfig = TTSConfig()
