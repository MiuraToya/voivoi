"""Whisperアダプター（STT実装）."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import whisper

from voivoi.chat.stt.port import SilentAudioError, TranscribeResult


class WhisperSegment(TypedDict):
    """Whisperのセグメント出力."""

    no_speech_prob: float


class WhisperOutput(TypedDict):
    """Whisperのtranscribe出力."""

    text: str
    segments: list[WhisperSegment]


class WhisperAdapter:
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
