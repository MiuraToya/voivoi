"""TTS（音声合成）モジュール."""

from __future__ import annotations

from typing import Protocol

import pyttsx3


class TTSProvider(Protocol):
    """TTSプロバイダーのインターフェース（依存注入用）."""

    def speak(self, text: str) -> None: ...


class Pyttsx3TTS:
    """pyttsx3を使用したTTS実装."""

    def __init__(self) -> None:
        self._engine = pyttsx3.init()

    def speak(self, text: str) -> None:
        """テキストを音声で読み上げる."""
        self._engine.say(text)
        self._engine.runAndWait()
