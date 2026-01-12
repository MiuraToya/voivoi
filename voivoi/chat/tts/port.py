"""TTSポート（インターフェース）."""

from __future__ import annotations

from typing import Protocol


class TTSPort(Protocol):
    """TTSプロバイダーのインターフェース（依存注入用）."""

    def speak(self, text: str) -> None: ...
