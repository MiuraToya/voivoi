"""Chat CLI のテスト."""

from unittest.mock import patch

from typer.testing import CliRunner

from voivoi.cli import app

runner = CliRunner()


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
        from voivoi.chat.chat import Chat
        from voivoi.chat.repository import save_chat

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
        from voivoi.chat.chat import Chat
        from voivoi.chat.repository import save_chat

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
