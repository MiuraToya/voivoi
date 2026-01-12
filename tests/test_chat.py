"""Chat/Messageドメインモデルのテスト."""

from datetime import datetime, timezone

import pytest


class TestMessage:
    """Messageのテスト."""

    def test_message_create_returns_message_with_role_content_created_at(self):
        """Message.create()はrole, content, created_atを持つメッセージを返す."""
        # Act
        from voivoi.chat.chat import Message

        message = Message.create(role="user", content="こんにちは")

        # Assert
        assert message.role == "user"
        assert message.content == "こんにちは"
        assert message.created_at is not None

    def test_message_create_raises_error_when_role_is_invalid(self):
        """roleがuser/assistant以外の場合はエラー."""
        # Arrange
        from voivoi.chat.chat import Message

        # Act & Assert
        with pytest.raises(ValueError, match="role"):
            Message.create(role="invalid", content="test")  # type: ignore[arg-type]

    def test_message_create_raises_error_when_content_is_empty(self):
        """contentが空文字の場合はエラー."""
        # Arrange
        from voivoi.chat.chat import Message

        # Act & Assert
        with pytest.raises(ValueError, match="content"):
            Message.create(role="user", content="")

    def test_message_restore_returns_message_with_given_values(self):
        """Message.restore()は指定された値でメッセージを復元する."""
        # Arrange
        from voivoi.chat.chat import Message

        now = datetime.now(timezone.utc)

        # Act
        message = Message.restore(role="user", content="こんにちは", created_at=now)

        # Assert
        assert message.role == "user"
        assert message.content == "こんにちは"
        assert message.created_at == now


class TestChat:
    """Chatのテスト."""

    def test_chat_create_returns_new_chat_with_id_and_timestamps(self):
        """Chat.create()は新規Chatを返す."""
        # Act
        from voivoi.chat.chat import Chat

        chat = Chat.create()

        # Assert
        assert chat.id is not None
        assert len(chat.id) > 0
        assert chat.messages == []
        assert chat.created_at is not None
        assert chat.updated_at is not None
        assert chat.created_at == chat.updated_at

    def test_chat_add_message_appends_message_and_updates_timestamp(self):
        """add_messageはメッセージを追加しupdated_atを更新する."""
        # Arrange
        from voivoi.chat.chat import Chat

        chat = Chat.create()
        original_updated_at = chat.updated_at

        # Act
        import time

        time.sleep(0.001)  # タイムスタンプが変わることを保証
        chat.add_message("user", "こんにちは")

        # Assert
        assert len(chat.messages) == 1
        assert chat.messages[0].role == "user"
        assert chat.messages[0].content == "こんにちは"
        assert chat.updated_at > original_updated_at


class TestChatPersistence:
    """Chat永続化のテスト."""

    def test_save_chat_creates_jsonl_file(self, tmp_path):
        """save_chatはJSONLファイルを作成する."""
        # Arrange
        from voivoi.chat.chat import Chat
        from voivoi.chat.repository import save_chat

        chat = Chat.create()
        chat.add_message("user", "こんにちは")
        chat.add_message("assistant", "はい、こんにちは")
        path = tmp_path / f"{chat.id}.jsonl"

        # Act
        save_chat(chat, path)

        # Assert
        assert path.exists()
        lines = path.read_text().strip().split("\n")
        assert len(lines) == 2  # 2メッセージ

    def test_load_chat_restores_chat_from_jsonl(self, tmp_path):
        """load_chatはJSONLファイルからChatを復元する."""
        # Arrange
        from voivoi.chat.chat import Chat
        from voivoi.chat.repository import load_chat, save_chat

        original_chat = Chat.create()
        original_chat.add_message("user", "こんにちは")
        original_chat.add_message("assistant", "はい、こんにちは")
        path = tmp_path / f"{original_chat.id}.jsonl"
        save_chat(original_chat, path)

        # Act
        loaded_chat = load_chat(path)

        # Assert
        assert loaded_chat is not None
        assert len(loaded_chat.messages) == 2
        assert loaded_chat.messages[0].role == "user"
        assert loaded_chat.messages[0].content == "こんにちは"
        assert loaded_chat.messages[1].role == "assistant"
        assert loaded_chat.messages[1].content == "はい、こんにちは"

    def test_load_chat_returns_none_when_file_not_exists(self, tmp_path):
        """load_chatはファイルが存在しない場合Noneを返す."""
        # Arrange
        from voivoi.chat.repository import load_chat

        path = tmp_path / "nonexistent.jsonl"

        # Act
        result = load_chat(path)

        # Assert
        assert result is None

    def test_list_chats_returns_all_chats_in_directory(self, tmp_path):
        """list_chatsはディレクトリ内の全チャットを返す."""
        # Arrange
        from voivoi.chat.chat import Chat
        from voivoi.chat.repository import list_chats, save_chat

        chat1 = Chat.create()
        chat1.add_message("user", "1つ目")
        save_chat(chat1, tmp_path / f"{chat1.id}.jsonl")

        chat2 = Chat.create()
        chat2.add_message("user", "2つ目")
        save_chat(chat2, tmp_path / f"{chat2.id}.jsonl")

        # Act
        chats = list_chats(tmp_path)

        # Assert
        assert len(chats) == 2
        chat_ids = {c.id for c in chats}
        assert chat1.id in chat_ids
        assert chat2.id in chat_ids

    def test_list_chats_returns_empty_list_when_directory_is_empty(self, tmp_path):
        """list_chatsはディレクトリが空の場合空リストを返す."""
        # Arrange
        from voivoi.chat.repository import list_chats

        # Act
        chats = list_chats(tmp_path)

        # Assert
        assert chats == []
