"""BargeInDetector（バージイン検出）モジュールのテスト."""

import struct
from unittest.mock import create_autospec

from voivoi.chat.audio.echo import EchoCanceller
from voivoi.chat.audio.player import AudioPlayerPort
from voivoi.chat.audio.port import AudioRecorderPort
from voivoi.chat.audio.vad import ThresholdVAD
from voivoi.chat.bargein import BargeInDetector
from voivoi.chat.tts.port import TTSSynthesizerPort

CHUNK_BYTES = 1024 * 2  # 1024サンプル × 2バイト（int16）


def _silent_chunk() -> bytes:
    """無音のチャンクを生成する."""
    return b"\x00" * CHUNK_BYTES


def _tone_chunk(amplitude: int = 5000) -> bytes:
    """一定振幅のトーンチャンクを生成する."""
    samples = [amplitude] * (CHUNK_BYTES // 2)
    return struct.pack(f"<{len(samples)}h", *samples)


class TestBargeInDetector:
    """BargeInDetectorのテスト."""

    def test_monitor_plays_all_chunks_when_no_speech(self) -> None:
        """発話が検出されない場合、全チャンクが再生される."""
        # Arrange
        mock_synthesizer = create_autospec(TTSSynthesizerPort, instance=True, spec_set=True)
        mock_player = create_autospec(AudioPlayerPort, instance=True, spec_set=True)
        mock_recorder = create_autospec(AudioRecorderPort, instance=True, spec_set=True)

        pcm_data = _silent_chunk() * 3
        mock_synthesizer.synthesize.return_value = pcm_data
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=EchoCanceller(),
            vad=ThresholdVAD(threshold=0.05),
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
        """マイクにユーザー音声が入ると再生を停止する."""
        # Arrange
        mock_synthesizer = create_autospec(TTSSynthesizerPort, instance=True, spec_set=True)
        mock_player = create_autospec(AudioPlayerPort, instance=True, spec_set=True)
        mock_recorder = create_autospec(AudioRecorderPort, instance=True, spec_set=True)

        pcm_data = _silent_chunk() * 5
        mock_synthesizer.synthesize.return_value = pcm_data
        # マイクにはユーザーの声（エコーではない独立した音声）が入る
        mock_recorder.read_chunk.return_value = (_tone_chunk(8000), 0.0)

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=EchoCanceller(),
            vad=ThresholdVAD(threshold=0.05),
            warmup_chunks=0,
            min_speech_frames=1,
        )

        # Act
        detector.monitor("長い応答テキスト")

        # Assert — 発話検出で途中停止（全5チャンクは再生されない）
        assert mock_player.play_chunk.call_count < 5
        mock_player.stop.assert_called_once()

    def test_monitor_flushes_input_buffer_before_playback(self) -> None:
        """再生開始前に入力バッファをフラッシュする."""
        # Arrange
        mock_synthesizer = create_autospec(TTSSynthesizerPort, instance=True, spec_set=True)
        mock_player = create_autospec(AudioPlayerPort, instance=True, spec_set=True)
        mock_recorder = create_autospec(AudioRecorderPort, instance=True, spec_set=True)

        mock_synthesizer.synthesize.return_value = _silent_chunk()
        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=EchoCanceller(),
            vad=ThresholdVAD(threshold=0.05),
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
        mock_synthesizer = create_autospec(TTSSynthesizerPort, instance=True, spec_set=True)
        mock_player = create_autospec(AudioPlayerPort, instance=True, spec_set=True)
        mock_recorder = create_autospec(AudioRecorderPort, instance=True, spec_set=True)

        pcm_data = _silent_chunk() * 10
        mock_synthesizer.synthesize.return_value = pcm_data
        # 常にユーザー音声が入っている状態
        mock_recorder.read_chunk.return_value = (_tone_chunk(8000), 0.0)

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=EchoCanceller(),
            vad=ThresholdVAD(threshold=0.05),
            warmup_chunks=3,
            min_speech_frames=1,
        )

        # Act
        detector.monitor("テスト")

        # Assert — ウォームアップ3チャンク + 発話検出1チャンク = 4チャンク再生
        assert mock_player.play_chunk.call_count == 4
        mock_player.stop.assert_called_once()

    def test_monitor_requires_consecutive_speech_frames(self) -> None:
        """連続した発話フレームが規定回数に達しないと停止しない."""
        # Arrange
        mock_synthesizer = create_autospec(TTSSynthesizerPort, instance=True, spec_set=True)
        mock_player = create_autospec(AudioPlayerPort, instance=True, spec_set=True)
        mock_recorder = create_autospec(AudioRecorderPort, instance=True, spec_set=True)

        pcm_data = _silent_chunk() * 10
        mock_synthesizer.synthesize.return_value = pcm_data
        # 発話→発話→無音→発話→発話→発話→...
        mic_responses = [
            (_tone_chunk(8000), 0.0),  # chunk 0: speech
            (_tone_chunk(8000), 0.0),  # chunk 1: speech
            (_silent_chunk(), 0.0),    # chunk 2: silence → reset
            (_tone_chunk(8000), 0.0),  # chunk 3: speech
            (_tone_chunk(8000), 0.0),  # chunk 4: speech
            (_tone_chunk(8000), 0.0),  # chunk 5: speech → 3連続達成
            (_tone_chunk(8000), 0.0),
            (_tone_chunk(8000), 0.0),
            (_tone_chunk(8000), 0.0),
            (_tone_chunk(8000), 0.0),
        ]
        mock_recorder.read_chunk.side_effect = mic_responses

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=EchoCanceller(),
            vad=ThresholdVAD(threshold=0.05),
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
        mock_synthesizer = create_autospec(TTSSynthesizerPort, instance=True, spec_set=True)
        mock_player = create_autospec(AudioPlayerPort, instance=True, spec_set=True)
        mock_recorder = create_autospec(AudioRecorderPort, instance=True, spec_set=True)

        pcm_data = _silent_chunk() * 10
        mock_synthesizer.synthesize.return_value = pcm_data
        mock_recorder.read_chunk.return_value = (_tone_chunk(8000), 0.0)

        # デフォルト値を使用（warmup_chunks=3, min_speech_frames=2）
        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=EchoCanceller(),
            vad=ThresholdVAD(threshold=0.05),
        )

        # Act
        detector.monitor("テスト")

        # Assert — warmup 3チャンク + 2連続発話 = 5チャンク再生で停止
        assert mock_player.play_chunk.call_count == 5
        mock_player.stop.assert_called_once()

    def test_monitor_limits_ref_buffer_size(self) -> None:
        """ref_bufferがmax_ref_chunksに制限される."""
        # Arrange
        mock_synthesizer = create_autospec(TTSSynthesizerPort, instance=True, spec_set=True)
        mock_player = create_autospec(AudioPlayerPort, instance=True, spec_set=True)
        mock_recorder = create_autospec(AudioRecorderPort, instance=True, spec_set=True)
        mock_echo_canceller = create_autospec(EchoCanceller, instance=True, spec_set=True)

        # 5チャンク分のPCMデータ（各チャンク異なるバイト）
        chunks = [bytes([i]) * CHUNK_BYTES for i in range(1, 6)]
        mock_synthesizer.synthesize.return_value = b"".join(chunks)

        mock_recorder.read_chunk.return_value = (_silent_chunk(), 0.0)
        mock_echo_canceller.cancel.return_value = 0.001

        detector = BargeInDetector(
            recorder=mock_recorder,
            synthesizer=mock_synthesizer,
            player=mock_player,
            echo_canceller=mock_echo_canceller,
            vad=ThresholdVAD(threshold=0.05),
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
