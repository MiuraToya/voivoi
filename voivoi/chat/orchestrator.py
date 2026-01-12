"""ChatOrchestrator（音声チャット統合）オーケストレーター."""

from __future__ import annotations

import tempfile
from pathlib import Path

from voivoi.chat.audio.wav import save_wav
from voivoi.chat.domain.models import Chat
from voivoi.chat.llm.port import LLMMessage, LLMPort
from voivoi.chat.stt.port import SilentAudioError, STTPort
from voivoi.chat.tts.port import TTSPort
from voivoi.chat.ui import print_ai_message, print_user_message


class ChatOrchestrator:
    """音声入力→STT→LLM→TTSの統合フロー."""

    def __init__(
        self,
        stt: STTPort,
        llm: LLMPort,
        tts: TTSPort,
        temp_dir: Path | None = None,
    ) -> None:
        self._stt = stt
        self._llm = llm
        self._tts = tts
        self._temp_dir = temp_dir or Path(tempfile.gettempdir())
        self._chat = Chat.create()

    def process_audio(self, audio_data: bytes) -> None:
        """音声データを処理して応答を生成し、読み上げる."""
        # 音声データをWAVファイルに保存
        wav_path = self._temp_dir / "temp_audio.wav"
        save_wav(audio_data, wav_path)

        # STT: 音声→テキスト
        try:
            result = self._stt.transcribe(wav_path)
        except SilentAudioError:
            return

        user_text = result.text
        print_user_message(user_text)

        # ユーザーメッセージを会話履歴に追加
        self._chat.add_message("user", user_text)

        # LLM: 応答生成（現在の会話履歴を渡す）
        llm_messages = [
            LLMMessage(role=m.role, content=m.content) for m in self._chat.messages
        ]
        response = self._llm.generate(llm_messages)
        print_ai_message(response)

        # アシスタントの応答を会話履歴に追加
        self._chat.add_message("assistant", response)

        # TTS: テキスト→音声
        self._tts.speak(response)

    def get_chat(self) -> Chat:
        """会話履歴を取得する."""
        return self._chat
