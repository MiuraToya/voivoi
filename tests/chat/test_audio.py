"""音声録音・再生モジュールのテスト."""

from unittest.mock import MagicMock, patch

from voivoi.chat.audio.adapter import PyAudioAdapter
from voivoi.chat.audio.player import PyAudioPlayer


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
    def test_flush_discards_buffered_data(self, mock_pyaudio: MagicMock) -> None:
        """flush()でバッファに蓄積された音声データを破棄する."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream
        # バッファに3チャンク分のデータが蓄積
        mock_stream.get_read_available.return_value = 1024 * 3

        recorder = PyAudioAdapter()

        # Act
        recorder.flush()

        # Assert — 蓄積データを読み捨て
        mock_stream.get_read_available.assert_called_once()
        mock_stream.read.assert_called_once_with(1024 * 3, exception_on_overflow=False)

    @patch("voivoi.chat.audio.adapter.pyaudio")
    def test_flush_does_nothing_when_buffer_empty(
        self, mock_pyaudio: MagicMock
    ) -> None:
        """バッファが空の場合、flush()は何もしない."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream
        mock_stream.get_read_available.return_value = 0

        recorder = PyAudioAdapter()

        # Act
        recorder.flush()

        # Assert
        mock_stream.get_read_available.assert_called_once()
        mock_stream.read.assert_not_called()

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


class TestPyAudioPlayer:
    """PyAudioPlayerのテスト."""

    @patch("voivoi.chat.audio.player.pyaudio")
    def test_play_chunk_writes_to_stream(self, mock_pyaudio: MagicMock) -> None:
        """チャンクが出力ストリームに書き込まれる."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream

        player = PyAudioPlayer()
        chunk = b"\x00\x40" * 1024

        # Act
        player.play_chunk(chunk)

        # Assert
        mock_stream.write.assert_called_once_with(chunk)

    @patch("voivoi.chat.audio.player.pyaudio")
    def test_stop_stops_and_restarts_stream(self, mock_pyaudio: MagicMock) -> None:
        """stop()でストリームを停止し、次の再生のために再開する."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream

        player = PyAudioPlayer()

        # Act
        player.stop()

        # Assert — 停止後に再開される
        mock_stream.stop_stream.assert_called_once()
        mock_stream.start_stream.assert_called_once()

    @patch("voivoi.chat.audio.player.pyaudio")
    def test_close_releases_resources(self, mock_pyaudio: MagicMock) -> None:
        """close()でリソースを解放する."""
        # Arrange
        mock_pa = MagicMock()
        mock_pyaudio.PyAudio.return_value = mock_pa
        mock_stream = MagicMock()
        mock_pa.open.return_value = mock_stream

        player = PyAudioPlayer()

        # Act
        player.close()

        # Assert
        mock_stream.close.assert_called_once()
        mock_pa.terminate.assert_called_once()
