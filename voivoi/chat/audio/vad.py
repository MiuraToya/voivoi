"""VAD（音声検出）モジュール."""

from __future__ import annotations

DEFAULT_THRESHOLD: float = 0.02


class ThresholdVAD:
    """音量閾値ベースのVAD実装."""

    def __init__(self, threshold: float = DEFAULT_THRESHOLD) -> None:
        self._threshold = threshold

    def is_speech(self, audio_level: float) -> bool:
        """音量レベルから発話中かどうかを判定する."""
        return audio_level > self._threshold
