"""STT（音声認識）モジュール."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Final, Protocol, TypedDict

import whisper


class SilentAudioError(Exception):
    """無音または音声を認識できなかった場合のエラー."""


class STTProvider(Protocol):
    """STTプロバイダーのインターフェース（依存注入用）."""

    def transcribe(self, audio_path: Path) -> TranscribeResult: ...


@dataclass(frozen=True)
class TranscribeResult:
    """文字起こし結果."""

    SILENT_THRESHOLD: ClassVar[Final[float]] = 0.9
    NO_SPEECH_PROB_WHEN_NO_SEGMENTS: ClassVar[Final[float]] = 1.0

    text: str
    no_speech_prob: float

    @property
    def is_silent(self) -> bool:
        """無音かどうか."""
        return not self.text.strip() or self.no_speech_prob > self.SILENT_THRESHOLD


class WhisperSegment(TypedDict):
    """Whisperのセグメント出力."""

    no_speech_prob: float


class WhisperOutput(TypedDict):
    """Whisperのtranscribe出力."""

    text: str
    segments: list[WhisperSegment]


class WhisperSTT:
    """Whisperを使用したSTT実装."""

    def __init__(self, model_name: str = "base", language: str = "ja") -> None:
        self._model = whisper.load_model(model_name)
        self._language = language

    def transcribe(self, audio_path: Path) -> TranscribeResult:
        """音声ファイルをテキストに変換する.

        Raises:
            SilentAudioError: 無音または音声を認識できなかった場合
        """
        # fp16=False でCPU使用時の警告を抑制
        raw_result = self._model.transcribe(
            str(audio_path), language=self._language, fp16=False
        )
        result = WhisperOutput(
            text=raw_result["text"],
            segments=raw_result.get("segments", []),
        )
        no_speech_prob = self._extract_no_speech_prob(result["segments"])
        transcribe_result = TranscribeResult(
            text=result["text"].strip(),
            no_speech_prob=no_speech_prob,
        )
        if transcribe_result.is_silent:
            raise SilentAudioError("音声を認識できませんでした")
        return transcribe_result

    def _extract_no_speech_prob(self, segments: list[WhisperSegment]) -> float:
        """セグメントからno_speech_probを抽出する."""
        if not segments:
            return TranscribeResult.NO_SPEECH_PROB_WHEN_NO_SEGMENTS
        return segments[0]["no_speech_prob"]
