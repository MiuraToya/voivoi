"""pyttsx3アダプター（TTS実装）."""

from __future__ import annotations

import pyttsx3


class Pyttsx3Adapter:
    """pyttsx3を使用したTTS実装."""

    def speak(self, text: str) -> None:
        """テキストを音声で読み上げる."""
        # macOSでは同一エンジンの再利用で問題が起きるため、毎回初期化
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
