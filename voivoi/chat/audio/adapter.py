"""PyAudioアダプター（音声録音実装）."""

from __future__ import annotations

import struct
from typing import Self

import pyaudio  # ty: ignore[unresolved-import]

# 録音設定
SAMPLE_RATE = 16000  # Whisperが期待するサンプルレート
CHANNELS = 1  # モノラル
CHUNK_SIZE = 1024  # 1チャンクあたりのフレーム数
FORMAT = pyaudio.paInt16  # 16-bit signed integer


class PyAudioAdapter:
    """PyAudioを使用した音声録音実装."""

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        channels: int = CHANNELS,
        chunk_size: int = CHUNK_SIZE,
    ) -> None:
        self._chunk_size = chunk_size
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=FORMAT,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk_size,
        )

    def read_chunk(self) -> tuple[bytes, float]:
        """1チャンク分の音声データを読み取り、データと音量レベルを返す."""
        # exception_on_overflow=False でオーバーフロー時もエラーにしない
        data = self._stream.read(self._chunk_size, exception_on_overflow=False)
        level = self._calculate_level(data)
        return data, level

    def _calculate_level(self, data: bytes) -> float:
        """音声データから正規化された音量レベル（0.0〜1.0）を計算する."""
        # 16-bit signed integerとしてアンパック
        samples = struct.unpack(f"<{len(data) // 2}h", data)
        if not samples:
            return 0.0
        # RMS（二乗平均平方根）で音量を計算
        rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
        # 16-bit signed integerの最大値で正規化
        return min(1.0, rms / 32767.0)

    def close(self) -> None:
        """リソースを解放する."""
        self._stream.stop_stream()
        self._stream.close()
        self._pa.terminate()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
