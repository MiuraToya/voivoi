"""WAVファイル保存モジュールのテスト."""

import wave
from pathlib import Path

from voivoi.chat.wav import save_wav


class TestSaveWav:
    """save_wavのテスト."""

    def test_saves_audio_data_as_wav_file(self, tmp_path: Path) -> None:
        """音声データをWAVファイルとして保存する."""
        # Arrange
        audio_data = b"\x00\x10" * 1000  # 16-bit サンプル
        wav_path = tmp_path / "test.wav"

        # Act
        save_wav(audio_data, wav_path)

        # Assert
        assert wav_path.exists()
        with wave.open(str(wav_path), "rb") as wf:
            assert wf.getnchannels() == 1  # モノラル
            assert wf.getsampwidth() == 2  # 16-bit
            assert wf.getframerate() == 16000  # Whisper用サンプルレート
            assert wf.readframes(wf.getnframes()) == audio_data
