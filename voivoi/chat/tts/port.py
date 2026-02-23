"""TTSポート（インターフェース）."""

from __future__ import annotations

from typing import Protocol


class TTSSynthesizerPort(Protocol):
    """TTS合成のインターフェース（テキスト→PCMバイト列）."""

    def synthesize(self, text: str) -> bytes: ...
