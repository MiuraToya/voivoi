"""エコーキャンセラーモジュール（相互相関ベース）."""

from __future__ import annotations

import struct

import numpy as np

# 相関係数がこの値未満の場合、エコー除去をスキップ（無関係な信号の誤除去防止）
MIN_CORRELATION_COEFF = 0.3


class EchoCanceller:
    """相互相関ベースのエコーキャンセラー.

    参照バッファ（再生済み音声の履歴）からマイク入力に含まれるエコーを
    検出・除去し、残差信号のRMSレベルを返す。
    """

    def cancel(self, mic_chunk: bytes, ref_buffer: bytes) -> float:
        """マイク入力からエコーを除去し、残差信号のRMSレベル（0.0〜1.0）を返す.

        Args:
            mic_chunk: マイク入力（1チャンク分）
            ref_buffer: 参照バッファ（再生済みチャンクの連結、mic_chunkと同じかそれ以上の長さ）
        """
        mic = self._to_float_array(mic_chunk)
        ref = self._to_float_array(ref_buffer)

        # 参照信号が無音の場合はエコー除去不要
        if float(np.dot(ref, ref)) < 1e-10:
            return self._rms_normalized(mic)

        # 参照バッファが短すぎる場合はそのまま返す
        if len(ref) < len(mic):
            return self._rms_normalized(mic)

        # 1. 参照バッファ内でマイク入力との最適アライメントを探索
        #    np.correlate(ref, mic, 'valid')[k] = Σ ref[k+n] * mic[n]
        corr = np.correlate(ref, mic, mode="valid")
        best_idx = int(np.argmax(np.abs(corr)))

        # 2. アライメントされた参照セグメントを抽出
        aligned_ref = ref[best_idx : best_idx + len(mic)]

        # 3. 相関係数を確認（低い場合はエコーなしと判断）
        mic_rms = float(np.sqrt(np.dot(mic, mic)))
        ref_rms = float(np.sqrt(np.dot(aligned_ref, aligned_ref)))
        if mic_rms < 1e-10 or ref_rms < 1e-10:
            return self._rms_normalized(mic)
        corr_coeff = float(np.dot(mic, aligned_ref)) / (mic_rms * ref_rms)
        if abs(corr_coeff) < MIN_CORRELATION_COEFF:
            return self._rms_normalized(mic)

        # 4. ゲイン推定（最小二乗法）、非負にクランプ
        aligned_energy = float(np.dot(aligned_ref, aligned_ref))
        gain = float(np.dot(mic, aligned_ref)) / aligned_energy
        gain = max(0.0, gain)

        # 5. エコー減算
        residual = mic - gain * aligned_ref

        return self._rms_normalized(residual)

    def _to_float_array(self, chunk: bytes) -> np.ndarray:
        """bytesをfloat64のnumpy配列に変換する."""
        samples = struct.unpack(f"<{len(chunk) // 2}h", chunk)
        return np.array(samples, dtype=np.float64)

    def _rms_normalized(self, signal: np.ndarray) -> float:
        """信号のRMSを0.0〜1.0に正規化して返す."""
        rms = float(np.sqrt(np.mean(signal**2)))
        return min(1.0, rms / 32767.0)
