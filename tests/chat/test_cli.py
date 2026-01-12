"""Chat CLI のテスト."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from voivoi.cli import app

runner = CliRunner()


class TestChatStart:
    """voivoi chat コマンド（音声チャット開始）のテスト."""

    @patch("voivoi.chat.cli.load_config")
    @patch("voivoi.chat.cli.PyAudioAdapter")
    @patch("voivoi.chat.cli.ThresholdVAD")
    @patch("voivoi.chat.cli.ContinuousListener")
    @patch("voivoi.chat.cli.WhisperAdapter")
    @patch("voivoi.chat.cli.OllamaAdapter")
    @patch("voivoi.chat.cli.Pyttsx3Adapter")
    @patch("voivoi.chat.cli.VoiceChat")
    def test_chat_start_initializes_and_runs_voice_chat(
        self,
        mock_voice_chat_class: MagicMock,
        mock_tts_class: MagicMock,
        mock_llm_class: MagicMock,
        mock_stt_class: MagicMock,
        mock_listener_class: MagicMock,
        mock_vad_class: MagicMock,
        mock_recorder_class: MagicMock,
        mock_load_config: MagicMock,
    ) -> None:
        """音声チャットを初期化して実行する."""
        # Arrange
        from voivoi.config.schema import Config

        mock_load_config.return_value = Config()

        mock_recorder = MagicMock()
        mock_recorder_class.return_value.__enter__ = MagicMock(
            return_value=mock_recorder
        )
        mock_recorder_class.return_value.__exit__ = MagicMock(return_value=False)

        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener
        # 空のイテレータで終了させる
        mock_listener.listen.return_value = iter([])

        mock_voice_chat = MagicMock()
        mock_voice_chat_class.return_value = mock_voice_chat

        # Act
        result = runner.invoke(app, ["chat"])

        # Assert
        assert result.exit_code == 0
        mock_recorder_class.assert_called_once()
        mock_vad_class.assert_called_once()
        mock_listener_class.assert_called_once()
        mock_stt_class.assert_called_once()
        mock_llm_class.assert_called_once()
        mock_tts_class.assert_called_once()
        mock_voice_chat_class.assert_called_once()


class TestChatList:
    """voivoi chat list コマンドのテスト."""

    def test_chat_list_shows_empty_message_when_no_chats(self, tmp_path) -> None:
        """チャットがない場合、空のメッセージを表示する."""
        # Arrange
        chats_dir = tmp_path / "chats"
        chats_dir.mkdir()

        # Act
        with patch("voivoi.chat.cli.get_chats_dir", return_value=chats_dir):
            result = runner.invoke(app, ["chat", "list"])

        # Assert
        assert result.exit_code == 0
        assert "No chats" in result.stdout

    def test_chat_list_shows_chats_with_id_and_date(self, tmp_path) -> None:
        """チャット一覧をID・日時とともに表示する."""
        # Arrange
        from voivoi.chat.domain.models import Chat
        from voivoi.chat.domain.repository import save_chat

        chats_dir = tmp_path / "chats"
        chats_dir.mkdir()

        chat = Chat.create()
        chat.add_message("user", "こんにちは")
        save_chat(chat, chats_dir / f"{chat.id}.jsonl")

        # Act
        with patch("voivoi.chat.cli.get_chats_dir", return_value=chats_dir):
            result = runner.invoke(app, ["chat", "list"])

        # Assert
        assert result.exit_code == 0
        assert chat.id in result.stdout


class TestChatShow:
    """voivoi chat show コマンドのテスト."""

    def test_chat_show_displays_messages(self, tmp_path) -> None:
        """チャット内容を表示する."""
        # Arrange
        from voivoi.chat.domain.models import Chat
        from voivoi.chat.domain.repository import save_chat

        chats_dir = tmp_path / "chats"
        chats_dir.mkdir()

        chat = Chat.create()
        chat.add_message("user", "こんにちは")
        chat.add_message("assistant", "はい、こんにちは")
        save_chat(chat, chats_dir / f"{chat.id}.jsonl")

        # Act
        with patch("voivoi.chat.cli.get_chats_dir", return_value=chats_dir):
            result = runner.invoke(app, ["chat", "show", chat.id])

        # Assert
        assert result.exit_code == 0
        assert "こんにちは" in result.stdout
        assert "はい、こんにちは" in result.stdout

    def test_chat_show_returns_error_when_chat_not_found(self, tmp_path) -> None:
        """チャットが見つからない場合、エラーを返す."""
        # Arrange
        chats_dir = tmp_path / "chats"
        chats_dir.mkdir()

        # Act
        with patch("voivoi.chat.cli.get_chats_dir", return_value=chats_dir):
            result = runner.invoke(app, ["chat", "show", "nonexistent-id"])

        # Assert
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()
