"""pyttsx3アダプター（TTS実装）."""

from __future__ import annotations

import threading

import pyttsx3


class Pyttsx3Adapter:
    """pyttsx3を使用したTTS実装."""

    def __init__(self) -> None:
        self._engine: pyttsx3.Engine | None = None
        self._lock = threading.Lock()

    def speak(self, text: str) -> None:
        """テキストを音声で読み上げる."""
        # macOSでは同一エンジンの再利用で問題が起きるため、毎回初期化
        engine = pyttsx3.init()
        with self._lock:
            self._engine = engine
        try:
            engine.say(text)
            engine.runAndWait()
        finally:
            with self._lock:
                self._engine = None
            engine.stop()

    def stop(self) -> None:
        """再生を停止する（スレッドセーフ）."""
        with self._lock:
            if self._engine is not None:
                self._engine.stop()
