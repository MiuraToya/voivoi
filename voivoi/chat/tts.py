"""TTS（音声合成）モジュール."""

from __future__ import annotations

from typing import Protocol

import pyttsx3


class TTSProvider(Protocol):
    """TTSプロバイダーのインターフェース（依存注入用）."""

    def speak(self, text: str) -> None: ...


class Pyttsx3TTS:
    """pyttsx3を使用したTTS実装."""

    def speak(self, text: str) -> None:
        """テキストを音声で読み上げる."""
        # macOSでは同一エンジンの再利用で問題が起きるため、毎回初期化
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
