"""WAVファイル保存モジュール."""

from __future__ import annotations

import wave
from pathlib import Path

# Whisperが期待するフォーマット
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit


def save_wav(audio_data: bytes, path: Path) -> None:
    """音声データをWAVファイルとして保存する."""
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data)
