"""TTSポート（インターフェース）."""

from __future__ import annotations

from typing import Protocol


class TTSPort(Protocol):
    """TTSプロバイダーのインターフェース（依存注入用）."""

    def speak(self, text: str) -> None: ...
    def stop(self) -> None: ...


class TTSSynthesizerPort(Protocol):
    """TTS合成のインターフェース（テキスト→PCMバイト列）."""

    def synthesize(self, text: str) -> bytes: ...
