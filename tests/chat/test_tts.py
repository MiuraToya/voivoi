"""TTSモジュールのテスト."""

from unittest.mock import MagicMock, patch

from voivoi.chat.tts import Pyttsx3TTS


class TestPyttsx3TTS:
    """Pyttsx3TTSのテスト."""

    @patch("voivoi.chat.tts.pyttsx3")
    def test_speak_reads_text_aloud(self, mock_pyttsx3: MagicMock) -> None:
        """テキストを音声で読み上げる."""
        # Arrange
        mock_engine = MagicMock()
        mock_pyttsx3.init.return_value = mock_engine
        tts = Pyttsx3TTS()

        # Act
        tts.speak("こんにちは")

        # Assert
        mock_engine.say.assert_called_once_with("こんにちは")
        mock_engine.runAndWait.assert_called_once()
