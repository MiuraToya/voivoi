"""EchoCanceller（エコーキャンセラー）モジュールのテスト."""

import struct

from voivoi.chat.audio.echo import EchoCanceller


def _make_chunk(samples: list[int]) -> bytes:
    """int16サンプルのリストからbytesを生成する."""
    return struct.pack(f"<{len(samples)}h", *samples)


CHUNK = 1024


class TestEchoCanceller:
    """EchoCancellerのテスト."""

    def test_cancel_returns_original_level_when_ref_is_silent(self) -> None:
        """参照信号が無音の場合、マイク入力のレベルがそのまま返る."""
        # Arrange
        canceller = EchoCanceller()
        mic_samples = [5000] * CHUNK
        ref_samples = [0] * CHUNK

        mic_chunk = _make_chunk(mic_samples)
        ref_buffer = _make_chunk(ref_samples)

        # Act
        level = canceller.cancel(mic_chunk, ref_buffer)

        # Assert
        expected_level = 5000 / 32767.0
        assert abs(level - expected_level) < 0.01

    def test_cancel_removes_echo_when_mic_equals_ref(self) -> None:
        """マイク入力が参照信号と同一（純粋エコー）の場合、残差はほぼゼロ."""
        # Arrange
        canceller = EchoCanceller()
        samples = [int(10000 * ((i % 64) / 64.0 - 0.5)) for i in range(CHUNK)]
        mic_chunk = _make_chunk(samples)
        ref_buffer = _make_chunk(samples)

        # Act
        level = canceller.cancel(mic_chunk, ref_buffer)

        # Assert
        assert level < 0.01

    def test_cancel_preserves_speech_with_echo(self) -> None:
        """マイク入力にエコーとユーザー音声が混在する場合、音声レベルが残る."""
        # Arrange
        canceller = EchoCanceller()
        echo = [int(3000 * ((i % 64) / 64.0 - 0.5)) for i in range(CHUNK)]
        speech = [int(8000 * ((i % 32) / 32.0 - 0.5)) for i in range(CHUNK)]
        mic_samples = [e + s for e, s in zip(echo, speech)]

        mic_chunk = _make_chunk(mic_samples)
        ref_buffer = _make_chunk(echo)

        # Act
        level = canceller.cancel(mic_chunk, ref_buffer)

        # Assert
        speech_only_level = (sum(s * s for s in speech) / len(speech)) ** 0.5 / 32767.0
        assert level > speech_only_level * 0.5
        assert level < speech_only_level * 1.5

    def test_cancel_finds_echo_in_longer_ref_buffer(self) -> None:
        """参照バッファがマイクチャンクより長い場合、正しい位置のエコーを見つける."""
        # Arrange — エコーは3チャンク前の参照信号
        canceller = EchoCanceller()

        # 4チャンク分の異なる参照信号を用意
        ref_chunks = []
        for c in range(4):
            freq = 32 + c * 16  # チャンクごとに異なる周波数
            samples = [int(5000 * ((i % freq) / freq - 0.5)) for i in range(CHUNK)]
            ref_chunks.append(samples)

        # マイク入力 = ref_chunks[0] のエコー（3チャンク前に再生された音）
        mic_chunk = _make_chunk(ref_chunks[0])

        # 参照バッファ = 全チャンク連結（ref_0 + ref_1 + ref_2 + ref_3）
        all_ref_samples: list[int] = []
        for chunk_samples in ref_chunks:
            all_ref_samples.extend(chunk_samples)
        ref_buffer = _make_chunk(all_ref_samples)

        # Act
        level = canceller.cancel(mic_chunk, ref_buffer)

        # Assert — ref_chunks[0]が見つかりエコー除去される
        assert level < 0.01

    def test_cancel_returns_mic_level_when_no_correlation(self) -> None:
        """参照信号とマイク入力に相関がない場合、マイクレベルをそのまま返す."""
        # Arrange
        canceller = EchoCanceller()

        # マイク: 低レベルのノイズ
        import random

        random.seed(42)
        noise = [int(500 * (random.random() - 0.5)) for _ in range(CHUNK)]
        mic_chunk = _make_chunk(noise)

        # 参照: 強い信号だがマイクとは無関係
        ref_samples = [int(10000 * ((i % 64) / 64.0 - 0.5)) for i in range(CHUNK)]
        ref_buffer = _make_chunk(ref_samples)

        # Act
        level = canceller.cancel(mic_chunk, ref_buffer)

        # Assert — ノイズレベルが大きく変わらない（増幅されない）
        noise_level = (sum(n * n for n in noise) / len(noise)) ** 0.5 / 32767.0
        assert level < noise_level * 2.0  # 元のレベルの2倍以内
