"""VAD（音声検出）モジュールのテスト."""

from voivoi.chat.vad import ThresholdVAD


class TestThresholdVAD:
    """ThresholdVADのテスト."""

    def test_detects_speech_when_level_exceeds_threshold(self) -> None:
        """音量が閾値を超えたら発話中と判定する."""
        # Arrange
        vad = ThresholdVAD(threshold=0.5)

        # Act
        result = vad.is_speech(0.6)

        # Assert
        assert result is True

    def test_detects_silence_when_level_below_threshold(self) -> None:
        """音量が閾値以下なら無音と判定する."""
        # Arrange
        vad = ThresholdVAD(threshold=0.5)

        # Act
        result = vad.is_speech(0.3)

        # Assert
        assert result is False

    def test_detects_silence_when_level_equals_threshold(self) -> None:
        """音量が閾値と同じなら無音と判定する."""
        # Arrange
        vad = ThresholdVAD(threshold=0.5)

        # Act
        result = vad.is_speech(0.5)

        # Assert
        assert result is False

    def test_uses_default_threshold_when_not_specified(self) -> None:
        """閾値を指定しない場合はデフォルト値を使用する."""
        # Arrange
        vad = ThresholdVAD()

        # Act & Assert
        # デフォルト閾値は0.02（環境ノイズを考慮した低めの値）
        assert vad.is_speech(0.03) is True
        assert vad.is_speech(0.01) is False
