"""音声録音ポート（インターフェース）."""

from __future__ import annotations

from typing import Protocol, Self


class AudioRecorderPort(Protocol):
    """音声録音プロバイダーのインターフェース（依存注入用）."""

    def read_chunk(self) -> tuple[bytes, float]: ...
    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, *args: object) -> None: ...
