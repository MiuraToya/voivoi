"""LLMモジュールのテスト."""

from typing import Protocol
from unittest.mock import MagicMock, patch

import pytest

from voivoi.chat.llm.adapter import OllamaAdapter
from voivoi.chat.llm.port import LLMConnectionError, LLMMessage, LLMPort


class TestLLMMessage:
    """LLMMessageのテスト."""

    def test_llm_message_has_role_and_content(self) -> None:
        """LLMMessageはroleとcontentを持つ."""
        # Arrange & Act
        message = LLMMessage(role="user", content="こんにちは")

        # Assert
        assert message.role == "user"
        assert message.content == "こんにちは"

    def test_llm_message_supports_system_role(self) -> None:
        """LLMMessageはsystemロールをサポートする."""
        # Arrange & Act
        message = LLMMessage(role="system", content="あなたは親切なアシスタントです")

        # Assert
        assert message.role == "system"

    def test_llm_message_is_immutable(self) -> None:
        """LLMMessageはイミュータブルである."""
        # Arrange
        message = LLMMessage(role="user", content="テスト")

        # Act & Assert
        with pytest.raises(AttributeError):
            message.content = "変更"  # type: ignore[misc]


class TestLLMPort:
    """LLMPortのテスト."""

    def test_llm_port_is_protocol(self) -> None:
        """LLMPortはProtocolである."""
        # Arrange & Act & Assert
        assert issubclass(LLMPort, Protocol)


class TestOllamaAdapter:
    """OllamaAdapterのテスト."""

    @patch("voivoi.chat.llm.adapter.ollama")
    def test_generate_returns_response_from_ollama(
        self, mock_ollama: MagicMock
    ) -> None:
        """Ollamaからの応答を返す."""
        # Arrange
        mock_ollama.chat.return_value = {"message": {"content": "こんにちは！"}}
        llm = OllamaAdapter(model="llama3.1")
        messages = [LLMMessage(role="user", content="挨拶して")]

        # Act
        result = llm.generate(messages)

        # Assert
        assert result == "こんにちは！"

    @patch("voivoi.chat.llm.adapter.ollama")
    def test_generate_sends_messages_with_configured_model(
        self, mock_ollama: MagicMock
    ) -> None:
        """設定されたモデルでメッセージを送信する."""
        # Arrange
        mock_ollama.chat.return_value = {"message": {"content": "応答"}}
        llm = OllamaAdapter(model="gemma2")
        messages = [LLMMessage(role="user", content="テスト")]

        # Act
        llm.generate(messages)

        # Assert
        mock_ollama.chat.assert_called_once_with(
            model="gemma2",
            messages=[{"role": "user", "content": "テスト"}],
        )

    @patch("voivoi.chat.llm.adapter.ollama")
    def test_generate_passes_conversation_history(self, mock_ollama: MagicMock) -> None:
        """会話履歴を含めてOllamaに送信する."""
        # Arrange
        mock_ollama.chat.return_value = {"message": {"content": "東京です"}}
        llm = OllamaAdapter(model="llama3.1")
        messages = [
            LLMMessage(role="user", content="私は日本に住んでいます"),
            LLMMessage(role="assistant", content="日本のどこにお住まいですか？"),
            LLMMessage(role="user", content="首都です"),
        ]

        # Act
        result = llm.generate(messages)

        # Assert
        mock_ollama.chat.assert_called_once_with(
            model="llama3.1",
            messages=[
                {"role": "user", "content": "私は日本に住んでいます"},
                {"role": "assistant", "content": "日本のどこにお住まいですか？"},
                {"role": "user", "content": "首都です"},
            ],
        )
        assert result == "東京です"


class TestLLMConnectionError:
    """LLMConnectionErrorのテスト."""

    def test_llm_connection_error_is_exception(self) -> None:
        """LLMConnectionErrorはExceptionを継承している."""
        # Act & Assert
        assert issubclass(LLMConnectionError, Exception)

    @patch("voivoi.chat.llm.adapter.ollama")
    def test_generate_raises_connection_error_when_ollama_unavailable(
        self, mock_ollama: MagicMock
    ) -> None:
        """Ollamaが利用できない場合、LLMConnectionErrorを発生させる."""
        # Arrange
        from ollama import ResponseError

        mock_ollama.chat.side_effect = ResponseError("connection refused")
        llm = OllamaAdapter(model="llama3.1")
        messages = [LLMMessage(role="user", content="こんにちは")]

        # Act & Assert
        with pytest.raises(LLMConnectionError):
            llm.generate(messages)
