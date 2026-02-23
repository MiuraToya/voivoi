"""PyAudio音声再生アダプター."""

from __future__ import annotations

from typing import Protocol

import pyaudio

# 再生設定（録音と同じフォーマット）
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16


class AudioPlayerPort(Protocol):
    """音声再生のインターフェース（依存注入用）."""

    def play_chunk(self, chunk: bytes) -> None: ...
    def stop(self) -> None: ...
    def close(self) -> None: ...


class PyAudioPlayer:
    """PyAudioを使用した音声再生実装."""

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
    ) -> None:
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=FORMAT,
            channels=channels,
            rate=sample_rate,
            output=True,
        )

    def play_chunk(self, chunk: bytes) -> None:
        """1チャンク分の音声データを再生する."""
        self._stream.write(chunk)

    def stop(self) -> None:
        """再生を停止し、次の再生のためにストリームを再開する."""
        self._stream.stop_stream()
        self._stream.start_stream()

    def close(self) -> None:
        """リソースを解放する."""
        self._stream.close()
        self._pa.terminate()
