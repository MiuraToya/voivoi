"""ChatOrchestrator（音声チャット統合）モジュールのテスト."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from voivoi.chat.llm.port import LLMMessage
from voivoi.chat.orchestrator import ChatOrchestrator
from voivoi.chat.stt.port import TranscribeResult


class TestChatOrchestrator:
    """ChatOrchestratorのテスト."""

    @patch("voivoi.chat.orchestrator.save_wav")
    def test_process_audio_transcribes_and_generates_response(
        self, mock_save_wav: MagicMock, tmp_path: Path
    ) -> None:
        """音声データを文字起こしし、LLMで応答を生成し、音声で読み上げる."""
        # Arrange
        mock_stt = MagicMock()
        mock_llm = MagicMock()
        mock_tts = MagicMock()

        mock_stt.transcribe.return_value = TranscribeResult(
            text="こんにちは", no_speech_prob=0.1
        )
        mock_llm.generate.return_value = "こんにちは！何かお手伝いできますか？"

        voice_chat = ChatOrchestrator(
            stt=mock_stt, llm=mock_llm, tts=mock_tts, temp_dir=tmp_path
        )

        # Act
        voice_chat.process_audio(b"audio_data")

        # Assert
        mock_stt.transcribe.assert_called_once()
        mock_llm.generate.assert_called_once()
        mock_tts.speak.assert_called_once_with("こんにちは！何かお手伝いできますか？")

    @patch("voivoi.chat.orchestrator.save_wav")
    def test_process_audio_includes_conversation_history(
        self, mock_save_wav: MagicMock, tmp_path: Path
    ) -> None:
        """会話履歴を含めてLLMに送信する."""
        # Arrange
        mock_stt = MagicMock()
        mock_llm = MagicMock()
        mock_tts = MagicMock()

        mock_stt.transcribe.side_effect = [
            TranscribeResult(text="こんにちは", no_speech_prob=0.1),
            TranscribeResult(text="今日の天気は？", no_speech_prob=0.1),
        ]
        mock_llm.generate.side_effect = [
            "こんにちは！",
            "今日は晴れです。",
        ]

        voice_chat = ChatOrchestrator(
            stt=mock_stt, llm=mock_llm, tts=mock_tts, temp_dir=tmp_path
        )

        # Act
        voice_chat.process_audio(b"audio1")
        voice_chat.process_audio(b"audio2")

        # Assert
        # 2回目のLLM呼び出しには会話履歴が含まれる
        calls = mock_llm.generate.call_args_list
        second_call_messages = calls[1][0][0]
        assert len(second_call_messages) == 3  # user, assistant, user
        assert second_call_messages[0] == LLMMessage(role="user", content="こんにちは")
        assert second_call_messages[1] == LLMMessage(
            role="assistant", content="こんにちは！"
        )
        assert second_call_messages[2] == LLMMessage(
            role="user", content="今日の天気は？"
        )

    @patch("voivoi.chat.orchestrator.save_wav")
    def test_process_audio_skips_silent_audio(
        self, mock_save_wav: MagicMock, tmp_path: Path
    ) -> None:
        """無音の場合はLLM呼び出しをスキップする."""
        # Arrange
        from voivoi.chat.stt.port import SilentAudioError

        mock_stt = MagicMock()
        mock_llm = MagicMock()
        mock_tts = MagicMock()

        mock_stt.transcribe.side_effect = SilentAudioError("無音")

        voice_chat = ChatOrchestrator(
            stt=mock_stt, llm=mock_llm, tts=mock_tts, temp_dir=tmp_path
        )

        # Act
        voice_chat.process_audio(b"silent_audio")

        # Assert
        mock_llm.generate.assert_not_called()
        mock_tts.speak.assert_not_called()

    def test_get_chat_returns_empty_chat_initially(self, tmp_path: Path) -> None:
        """会話開始前は空のChatを返す."""
        # Arrange
        mock_stt = MagicMock()
        mock_llm = MagicMock()
        mock_tts = MagicMock()

        voice_chat = ChatOrchestrator(
            stt=mock_stt, llm=mock_llm, tts=mock_tts, temp_dir=tmp_path
        )

        # Act
        chat = voice_chat.get_chat()

        # Assert
        assert chat.messages == []

    @patch("voivoi.chat.orchestrator.save_wav")
    def test_get_chat_returns_conversation_history(
        self, mock_save_wav: MagicMock, tmp_path: Path
    ) -> None:
        """音声入力ごとにユーザー発話とAI応答がChatに追加される."""
        # Arrange
        mock_stt = MagicMock()
        mock_llm = MagicMock()
        mock_tts = MagicMock()

        mock_stt.transcribe.return_value = TranscribeResult(
            text="こんにちは", no_speech_prob=0.1
        )
        mock_llm.generate.return_value = "こんにちは！"

        voice_chat = ChatOrchestrator(
            stt=mock_stt, llm=mock_llm, tts=mock_tts, temp_dir=tmp_path
        )

        # Act
        voice_chat.process_audio(b"audio")
        chat = voice_chat.get_chat()

        # Assert
        assert len(chat.messages) == 2
        assert chat.messages[0].role == "user"
        assert chat.messages[0].content == "こんにちは"
        assert chat.messages[1].role == "assistant"
        assert chat.messages[1].content == "こんにちは！"
