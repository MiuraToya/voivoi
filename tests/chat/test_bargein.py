"""BargeInDetector（バージイン検出）モジュールのテスト."""

from unittest.mock import MagicMock

from voivoi.chat.bargein import BargeInDetector

CHUNK_BYTES = 1024 * 2  # 1024サンプル × 2バイト（int16）


def _silent_chunk() -> bytes:
    """無音のチャンクを生成する."""
    return b"\x00" * CHUNK_BYTES


class TestBargeInDetector:
    """BargeInDetectorのテスト."""

    def test_monitor_plays_all_chunks_when_no_speech(self) -> None:
        """発話が検出されない場合、全チャンクが再生される."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        pcm_data = _silent_chunk() * 3
        mock_synthesizer.synthesize.return_value = pcm_data
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.return_value = 0.001
        mock_vad.is_speech.return_value = False

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
            warmup_chunks=0,
            min_speech_frames=1,
        )

        # Act
        detector.monitor("こんにちは")

        # Assert — 全3チャンクが再生された
        assert mock_player.play_chunk.call_count == 3
        mock_synthesizer.synthesize.assert_called_once_with("こんにちは")
        mock_player.stop.assert_not_called()

    def test_monitor_stops_when_speech_detected(self) -> None:
        """エコー除去後に発話を検出すると再生を停止する."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        pcm_data = _silent_chunk() * 5
        mock_synthesizer.synthesize.return_value = pcm_data
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.side_effect = [0.001, 0.001, 0.15, 0.15, 0.15]
        mock_vad.is_speech.side_effect = lambda level: level > 0.02

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
            warmup_chunks=0,
            min_speech_frames=1,
        )

        # Act
        detector.monitor("長い応答テキスト")

        # Assert — 3チャンク目で停止
        assert mock_player.play_chunk.call_count == 3
        mock_player.stop.assert_called_once()

    def test_monitor_passes_accumulated_ref_buffer_to_echo_canceller(self) -> None:
        """EchoCancellerに累積された参照バッファ（再生済みチャンクの連結）を渡す."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        chunk_a = b"\x01\x00" * 1024
        chunk_b = b"\x02\x00" * 1024
        chunk_c = b"\x03\x00" * 1024
        mock_synthesizer.synthesize.return_value = chunk_a + chunk_b + chunk_c

        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.return_value = 0.001
        mock_vad.is_speech.return_value = False

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
            warmup_chunks=0,
            min_speech_frames=1,
        )

        # Act
        detector.monitor("テスト")

        # Assert — cancel()の第2引数が累積バッファ
        calls = mock_echo_canceller.cancel.call_args_list
        assert len(calls) == 3

        # 1回目: ref_buffer = chunk_a
        assert calls[0][0][1] == chunk_a
        # 2回目: ref_buffer = chunk_a + chunk_b
        assert calls[1][0][1] == chunk_a + chunk_b
        # 3回目: ref_buffer = chunk_a + chunk_b + chunk_c
        assert calls[2][0][1] == chunk_a + chunk_b + chunk_c

    def test_monitor_flushes_input_buffer_before_playback(self) -> None:
        """再生開始前に入力バッファをフラッシュする."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        mock_synthesizer.synthesize.return_value = _silent_chunk()
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.return_value = 0.001
        mock_vad.is_speech.return_value = False

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
            warmup_chunks=0,
            min_speech_frames=1,
        )

        # Act
        detector.monitor("テスト")

        # Assert
        mock_recorder.flush.assert_called_once()

    def test_monitor_skips_vad_during_warmup(self) -> None:
        """ウォームアップ期間中はVAD判定をスキップする."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        pcm_data = _silent_chunk() * 10
        mock_synthesizer.synthesize.return_value = pcm_data
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.return_value = 0.15
        mock_vad.is_speech.return_value = True

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
            warmup_chunks=3,
            min_speech_frames=1,
        )

        # Act
        detector.monitor("テスト")

        # Assert — ウォームアップ3チャンク + 発話検出1チャンク = 4チャンク再生
        assert mock_player.play_chunk.call_count == 4
        mock_player.stop.assert_called_once()
        assert mock_echo_canceller.cancel.call_count == 1
        assert mock_vad.is_speech.call_count == 1

    def test_monitor_requires_consecutive_speech_frames(self) -> None:
        """連続した発話フレームが規定回数に達しないと停止しない."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        pcm_data = _silent_chunk() * 10
        mock_synthesizer.synthesize.return_value = pcm_data
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.side_effect = [
            0.15, 0.15, 0.001, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,
        ]
        mock_vad.is_speech.side_effect = lambda level: level > 0.02

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
            warmup_chunks=0,
            min_speech_frames=3,
        )

        # Act
        detector.monitor("テスト")

        # Assert — チャンク5(index 5)で3連続達成、停止
        assert mock_player.play_chunk.call_count == 6
        mock_player.stop.assert_called_once()

    def test_monitor_uses_default_warmup_and_debounce(self) -> None:
        """デフォルト設定（warmup=3, min_speech_frames=2）で動作する."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        pcm_data = _silent_chunk() * 10
        mock_synthesizer.synthesize.return_value = pcm_data
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.return_value = 0.15
        mock_vad.is_speech.return_value = True

        # デフォルト値を使用（warmup_chunks=3, min_speech_frames=2）
        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
        )

        # Act
        detector.monitor("テスト")

        # Assert — warmup 3チャンク + 2連続発話 = 5チャンク再生で停止
        assert mock_player.play_chunk.call_count == 5
        mock_player.stop.assert_called_once()

    def test_monitor_limits_ref_buffer_size(self) -> None:
        """ref_bufferがmax_ref_chunksに制限される."""
        # Arrange
        mock_synthesizer = MagicMock()
        mock_player = MagicMock()
        mock_recorder = MagicMock()
        mock_echo_canceller = MagicMock()
        mock_vad = MagicMock()

        # 5チャンク分のPCMデータ（各チャンク異なるバイト）
        chunks = [bytes([i]) * CHUNK_BYTES for i in range(1, 6)]
        mock_synthesizer.synthesize.return_value = b"".join(chunks)

        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.return_value = 0.001
        mock_vad.is_speech.return_value = False

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=mock_vad,
            warmup_chunks=0,
            min_speech_frames=1,
            max_ref_chunks=3,
        )

        # Act
        detector.monitor("テスト")

        # Assert — ref_bufferは最大3チャンク分に制限される
        calls = mock_echo_canceller.cancel.call_args_list
        assert len(calls) == 5

        # 1-3チャンク目: 累積（まだ制限に達していない）
        assert len(calls[0][0][1]) == CHUNK_BYTES * 1
        assert len(calls[1][0][1]) == CHUNK_BYTES * 2
        assert len(calls[2][0][1]) == CHUNK_BYTES * 3

        # 4-5チャンク目: 最大3チャンク分に制限（古いチャンクが捨てられる）
        assert len(calls[3][0][1]) == CHUNK_BYTES * 3
        assert len(calls[4][0][1]) == CHUNK_BYTES * 3

        # 5チャンク目のref_buffer = chunks[2] + chunks[3] + chunks[4]
        expected = chunks[2] + chunks[3] + chunks[4]
        assert calls[4][0][1] == expected
