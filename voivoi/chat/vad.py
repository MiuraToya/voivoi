"""VAD（音声検出）モジュール."""

from __future__ import annotations

from typing import Protocol

DEFAULT_THRESHOLD: float = 0.02


class VADProvider(Protocol):
    """VADプロバイダーのインターフェース（依存注入用）."""

    def is_speech(self, audio_level: float) -> bool: ...


class ThresholdVAD:
    """音量閾値ベースのVAD実装."""

    def __init__(self, threshold: float = DEFAULT_THRESHOLD) -> None:
        self._threshold = threshold

    def is_speech(self, audio_level: float) -> bool:
        """音量レベルから発話中かどうかを判定する."""
        return audio_level > self._threshold
