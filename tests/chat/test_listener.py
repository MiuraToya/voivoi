"""ContinuousListener（常時監視）モジュールのテスト."""

from unittest.mock import MagicMock

from voivoi.chat.listener import ContinuousListener


class TestContinuousListener:
    """ContinuousListenerのテスト."""

    def test_yields_audio_when_speech_detected_then_silence(self) -> None:
        """発話検出後、無音になったら音声データをyieldする."""
        # Arrange
        mock_recorder = MagicMock()
        mock_vad = MagicMock()

        # シーケンス: 発話 → 発話 → 無音×2（発話終了）
        mock_recorder.read_chunk.side_effect = [
            (b"speech1", 0.5),  # 発話開始
            (b"speech2", 0.6),  # 発話継続
            (b"silent1", 0.01),  # 無音1
            (b"silent2", 0.01),  # 無音2（発話終了判定）
        ]
        mock_vad.is_speech.side_effect = [True, True, False, False]

        listener = ContinuousListener(
            recorder=mock_recorder, vad=mock_vad, min_speech_chunks=1, silence_chunks=2
        )

        # Act
        result = next(listener.listen())

        # Assert
        # 発話中のデータのみが含まれる
        assert result == b"speech1speech2"

    def test_ignores_short_bursts_of_noise(self) -> None:
        """短いノイズは無視する（最小発話時間を設定）."""
        # Arrange
        mock_recorder = MagicMock()
        mock_vad = MagicMock()

        # シーケンス: ノイズ1チャンクのみ → 無音（短すぎるので無視）→ 正常発話
        mock_recorder.read_chunk.side_effect = [
            (b"noise", 0.5),  # 短いノイズ（1チャンクのみ）
            (b"silent1", 0.01),  # 無音1
            (b"silent2", 0.01),  # 無音2（min_speech_chunks未満なので無視）
            (b"speech1", 0.5),  # 正常な発話開始
            (b"speech2", 0.6),  # 発話継続
            (b"silent3", 0.01),  # 無音1
            (b"silent4", 0.01),  # 無音2（発話終了判定）
        ]
        mock_vad.is_speech.side_effect = [True, False, False, True, True, False, False]

        listener = ContinuousListener(
            recorder=mock_recorder, vad=mock_vad, min_speech_chunks=2, silence_chunks=2
        )

        # Act
        result = next(listener.listen())

        # Assert
        # 短いノイズは無視され、正常な発話のみがyieldされる
        assert result == b"speech1speech2"

    def test_waits_for_silence_duration_before_ending_speech(self) -> None:
        """一定期間の無音を待ってから発話終了と判定する."""
        # Arrange
        mock_recorder = MagicMock()
        mock_vad = MagicMock()

        # シーケンス: 発話 → 短い無音（1チャンク）→ 発話再開 → 長い無音（2チャンク、発話終了）
        mock_recorder.read_chunk.side_effect = [
            (b"speech1", 0.5),  # 発話
            (b"pause", 0.01),  # 短い無音（1チャンク、息継ぎ）
            (b"speech2", 0.5),  # 発話再開
            (b"silent1", 0.01),  # 無音1
            (b"silent2", 0.01),  # 無音2（発話終了判定）
        ]
        mock_vad.is_speech.side_effect = [True, False, True, False, False]

        listener = ContinuousListener(
            recorder=mock_recorder, vad=mock_vad, min_speech_chunks=1, silence_chunks=2
        )

        # Act
        result = next(listener.listen())

        # Assert
        # 短い無音は発話の一部として含まれる
        assert result == b"speech1pausespeech2"
