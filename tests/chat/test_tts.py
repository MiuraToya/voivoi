"""TTSモジュールのテスト."""

import struct
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

from voivoi.chat.tts.synthesizer import MacSaySynthesizer


class TestMacSaySynthesizer:
    """MacSaySynthesizerのテスト."""

    @patch("voivoi.chat.tts.synthesizer.subprocess")
    def test_synthesize_returns_pcm_bytes(
        self, mock_subprocess: MagicMock, tmp_path: Path
    ) -> None:
        """テキストからPCMバイト列を生成する."""
        # Arrange
        # say + afconvert の結果として WAV ファイルを作成
        wav_path = tmp_path / "output.wav"
        samples = [1000, 2000, 3000, 4000]
        pcm_data = struct.pack(f"<{len(samples)}h", *samples)
        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_data)

        # subprocess.run は成功する
        mock_subprocess.run.return_value = MagicMock(returncode=0)

        synthesizer = MacSaySynthesizer(work_dir=tmp_path)

        # afconvert の出力としてWAVファイルを配置済み
        # Act
        result = synthesizer.synthesize("こんにちは")

        # Assert
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch("voivoi.chat.tts.synthesizer.subprocess")
    def test_synthesize_calls_say_and_afconvert(
        self, mock_subprocess: MagicMock, tmp_path: Path
    ) -> None:
        """say と afconvert コマンドが正しい引数で呼ばれる."""
        # Arrange
        wav_path = tmp_path / "output.wav"
        samples = [1000] * 100
        pcm_data = struct.pack(f"<{len(samples)}h", *samples)
        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_data)

        mock_subprocess.run.return_value = MagicMock(returncode=0)

        synthesizer = MacSaySynthesizer(work_dir=tmp_path)

        # Act
        synthesizer.synthesize("テスト")

        # Assert — say と afconvert が呼ばれたこと
        calls = mock_subprocess.run.call_args_list
        assert len(calls) == 2
        # 1st call: say
        assert "say" in calls[0][0][0]
        # 2nd call: afconvert
        assert "afconvert" in calls[1][0][0]
