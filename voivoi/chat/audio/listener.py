"""ContinuousListener（常時監視）モジュール."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Final

from voivoi.chat.audio.port import AudioRecorderPort
from voivoi.chat.audio.vad import VADPort

# デフォルト設定
DEFAULT_MIN_SPEECH_CHUNKS: Final[int] = 3  # 最小発話チャンク数（ノイズ除去用）
DEFAULT_SILENCE_CHUNKS: Final[int] = 15  # 発話終了と判定するまでの無音チャンク数（約1秒）


class ContinuousListener:
    """常時監視で発話を検出し、音声データを返す."""

    def __init__(
        self,
        recorder: AudioRecorderPort,
        vad: VADPort,
        min_speech_chunks: int = DEFAULT_MIN_SPEECH_CHUNKS,
        silence_chunks: int = DEFAULT_SILENCE_CHUNKS,
    ) -> None:
        self._recorder = recorder
        self._vad = vad
        self._min_speech_chunks = min_speech_chunks
        self._silence_chunks = silence_chunks

    def listen(self) -> Iterator[bytes]:
        """発話を検出するたびに音声データをyieldする."""
        while True:
            audio_data = self._capture_speech()
            if audio_data:
                yield audio_data

    def _capture_speech(self) -> bytes | None:
        """発話を1回分キャプチャする."""
        chunks: list[bytes] = []
        speech_chunks = 0
        silence_count = 0

        # 発話開始を待つ
        while True:
            data, level = self._recorder.read_chunk()
            if self._vad.is_speech(level):
                chunks.append(data)
                speech_chunks = 1
                break

        # 発話中のデータを収集
        while True:
            data, level = self._recorder.read_chunk()

            if self._vad.is_speech(level):
                chunks.append(data)
                speech_chunks += 1
                silence_count = 0
            else:
                silence_count += 1
                # 短い無音は発話の一部として含める（息継ぎなど）
                if silence_count < self._silence_chunks:
                    chunks.append(data)
                else:
                    # 発話終了
                    break

        # 最小発話チャンク数に満たない場合は無視（ノイズ）
        if speech_chunks < self._min_speech_chunks:
            return None

        # 末尾の無音チャンクを除去
        return b"".join(chunks[: -(self._silence_chunks - 1)])
