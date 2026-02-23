"""バージイン検出モジュール（エコーキャンセレーション対応）."""

from __future__ import annotations

import logging

from voivoi.chat.audio.echo import EchoCanceller
from voivoi.chat.audio.player import AudioPlayerPort
from voivoi.chat.audio.port import AudioRecorderPort
from voivoi.chat.audio.vad import ThresholdVAD
from voivoi.chat.tts.port import TTSSynthesizerPort

logger = logging.getLogger(__name__)

# チャンクサイズ（録音と同じ: 1024サンプル × 2バイト）
CHUNK_BYTES = 1024 * 2

# デフォルト: 3チャンク = 192ms（エコー到達前のウォームアップ）
DEFAULT_WARMUP_CHUNKS = 3

# デフォルト: 2フレーム連続で発話検出が必要（瞬間ノイズ除外）
DEFAULT_MIN_SPEECH_FRAMES = 2

# デフォルト: 参照バッファの最大チャンク数（10チャンク = 640ms）
DEFAULT_MAX_REF_CHUNKS = 10


class BargeInDetector:
    """音声再生中にエコーキャンセレーションでバージインを検出する."""

    def __init__(
        self,
        recorder: AudioRecorderPort,
        synthesizer: TTSSynthesizerPort,
        player: AudioPlayerPort,
        echo_canceller: EchoCanceller,
        vad: ThresholdVAD,
        *,
        warmup_chunks: int = DEFAULT_WARMUP_CHUNKS,
        min_speech_frames: int = DEFAULT_MIN_SPEECH_FRAMES,
        max_ref_chunks: int = DEFAULT_MAX_REF_CHUNKS,
    ) -> None:
        self._recorder = recorder
        self._synthesizer = synthesizer
        self._player = player
        self._echo_canceller = echo_canceller
        self._vad = vad
        self._warmup_chunks = warmup_chunks
        self._min_speech_frames = min_speech_frames
        self._max_ref_chunks = max_ref_chunks

    def monitor(self, text: str) -> None:
        """テキストを再生しつつ、エコー除去後のマイク入力でバージインを検出."""
        pcm = self._synthesizer.synthesize(text)
        chunks = [pcm[i : i + CHUNK_BYTES] for i in range(0, len(pcm), CHUNK_BYTES)]

        # 合成中に蓄積されたマイクデータを破棄（古いデータでの誤検出防止）
        self._recorder.flush()

        # 再生済みチャンクの履歴（エコー遅延に対応するため累積、上限あり）
        ref_history: list[bytes] = []
        speech_count = 0

        for i, ref_chunk in enumerate(chunks):
            self._player.play_chunk(ref_chunk)
            ref_history.append(ref_chunk)

            # 参照バッファを最大チャンク数に制限（計算コスト抑制）
            if len(ref_history) > self._max_ref_chunks:
                ref_history = ref_history[-self._max_ref_chunks :]

            mic_data, _ = self._recorder.read_chunk()

            # ウォームアップ期間: エコーがまだマイクに到達していないためスキップ
            if i < self._warmup_chunks:
                logger.debug("chunk %d/%d: warmup (skip)", i, len(chunks))
                continue

            # 参照バッファでエコー除去
            ref_buffer = b"".join(ref_history)
            residual_level = self._echo_canceller.cancel(mic_data, ref_buffer)

            is_speech = self._vad.is_speech(residual_level)
            logger.debug(
                "chunk %d/%d: residual=%.4f speech=%s count=%d/%d",
                i,
                len(chunks),
                residual_level,
                is_speech,
                speech_count + 1 if is_speech else 0,
                self._min_speech_frames,
            )

            if is_speech:
                speech_count += 1
                if speech_count >= self._min_speech_frames:
                    self._player.stop()
                    return
            else:
                speech_count = 0
