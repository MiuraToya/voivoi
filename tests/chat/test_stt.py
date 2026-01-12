"""STTモジュールのテスト."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from voivoi.chat.stt import SilentAudioError, TranscribeResult, WhisperSTT


class TestWhisperSTT:
    """WhisperSTTのテスト."""

    @patch("voivoi.chat.stt.whisper")
    def test_transcribe_returns_text_from_audio(self, mock_whisper: MagicMock) -> None:
        """音声ファイルからテキストを返す."""
        # Arrange
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "こんにちは",
            "segments": [{"no_speech_prob": 0.1}],
        }
        mock_whisper.load_model.return_value = mock_model
        stt = WhisperSTT()
        audio_path = Path("/tmp/test.wav")

        # Act
        result = stt.transcribe(audio_path)

        # Assert
        assert result.text == "こんにちは"

    @patch("voivoi.chat.stt.whisper")
    def test_transcribe_uses_configured_language(
        self, mock_whisper: MagicMock
    ) -> None:
        """設定された言語で文字起こしする."""
        # Arrange
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "hello",
            "segments": [{"no_speech_prob": 0.1}],
        }
        mock_whisper.load_model.return_value = mock_model
        stt = WhisperSTT(language="en")
        audio_path = Path("/tmp/test.wav")

        # Act
        stt.transcribe(audio_path)

        # Assert
        mock_model.transcribe.assert_called_once_with(str(audio_path), language="en")

    @patch("voivoi.chat.stt.whisper")
    def test_transcribe_trims_whitespace_from_result(
        self, mock_whisper: MagicMock
    ) -> None:
        """文字起こし結果の前後の空白を除去する."""
        # Arrange
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "  テスト  ",
            "segments": [{"no_speech_prob": 0.1}],
        }
        mock_whisper.load_model.return_value = mock_model
        stt = WhisperSTT()
        audio_path = Path("/tmp/test.wav")

        # Act
        result = stt.transcribe(audio_path)

        # Assert
        assert result.text == "テスト"


class TestTranscribeResult:
    """TranscribeResultのテスト."""

    def test_is_silent_returns_true_when_no_speech_prob_is_high(self) -> None:
        """no_speech_probが高い場合、無音と判定する."""
        # Arrange
        result = TranscribeResult(text="", no_speech_prob=0.95)

        # Act & Assert
        assert result.is_silent is True

    def test_is_silent_returns_true_when_text_is_empty(self) -> None:
        """テキストが空の場合、無音と判定する."""
        # Arrange
        result = TranscribeResult(text="", no_speech_prob=0.5)

        # Act & Assert
        assert result.is_silent is True

    def test_is_silent_returns_false_when_speech_detected(self) -> None:
        """発話が検出された場合、無音ではないと判定する."""
        # Arrange
        result = TranscribeResult(text="こんにちは", no_speech_prob=0.1)

        # Act & Assert
        assert result.is_silent is False


class TestSilentAudioError:
    """SilentAudioErrorのテスト."""

    def test_silent_audio_error_is_exception(self) -> None:
        """SilentAudioErrorはExceptionを継承している."""
        # Act & Assert
        assert issubclass(SilentAudioError, Exception)

    @patch("voivoi.chat.stt.whisper")
    def test_transcribe_raises_silent_audio_error_when_silent(
        self, mock_whisper: MagicMock
    ) -> None:
        """無音の場合、SilentAudioErrorを発生させる."""
        # Arrange
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "",
            "segments": [],
        }
        mock_whisper.load_model.return_value = mock_model
        stt = WhisperSTT()
        audio_path = Path("/tmp/silent.wav")

        # Act & Assert
        with pytest.raises(SilentAudioError):
            stt.transcribe(audio_path)
