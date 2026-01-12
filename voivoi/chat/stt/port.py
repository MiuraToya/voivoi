"""STTポート（インターフェース）."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, Protocol


class SilentAudioError(Exception):
    """無音または音声を認識できなかった場合のエラー."""


@dataclass(frozen=True)
class TranscribeResult:
    """文字起こし結果."""

    SILENT_THRESHOLD: ClassVar[Final[float]] = 0.9
    NO_SPEECH_PROB_WHEN_NO_SEGMENTS: ClassVar[Final[float]] = 1.0

    text: str
    no_speech_prob: float

    @property
    def is_silent(self) -> bool:
        """無音かどうか."""
        return not self.text.strip() or self.no_speech_prob > self.SILENT_THRESHOLD


class STTPort(Protocol):
    """STTプロバイダーのインターフェース（依存注入用）."""

    def transcribe(self, audio_path: Path) -> TranscribeResult: ...
