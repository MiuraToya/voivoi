"""音声録音モジュールのテスト."""

from unittest.mock import MagicMock, patch

from voivoi.chat.audio.adapter import PyAudioAdapter


class TestPyAudioAdapter:
    """PyAudioAdapterのテスト."""

    @patch("voivoi.chat.audio.adapter.pyaudio")
    def test_read_chunk_returns_audio_data_and_level(
        self, mock_pyaudio: MagicMock
    ) -> None:
        """チャンクを読み取り、音声データと音量レベルを返す."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream
        # 16-bit signed integerの音声データ（最大値32767の半分程度）
        mock_stream.read.return_value = b"\x00\x40" * 1024  # 約0.5の音量レベル

        recorder = PyAudioAdapter()

        # Act
        data, level = recorder.read_chunk()

        # Assert
        assert data == b"\x00\x40" * 1024
        assert 0.0 <= level <= 1.0

    @patch("voivoi.chat.audio.adapter.pyaudio")
    def test_close_releases_resources(self, mock_pyaudio: MagicMock) -> None:
        """close()でリソースを解放する."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream

        recorder = PyAudioAdapter()

        # Act
        recorder.close()

        # Assert
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_pa.terminate.assert_called_once()

    @patch("voivoi.chat.audio.adapter.pyaudio")
    def test_context_manager_closes_on_exit(self, mock_pyaudio: MagicMock) -> None:
        """コンテキストマネージャ終了時にリソースを解放する."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream

        # Act
        with PyAudioAdapter() as recorder:
            _ = recorder

        # Assert
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_pa.terminate.assert_called_once()
