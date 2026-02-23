"""macOS say コマンドを使用したTTS合成."""

from __future__ import annotations

import subprocess
import tempfile
import wave
from pathlib import Path


class MacSaySynthesizer:
    """macOS say コマンドで音声合成し、16kHz/mono/16-bit PCM を返す."""

    def __init__(self, work_dir: Path | None = None) -> None:
        self._work_dir = work_dir or Path(tempfile.gettempdir())

    def synthesize(self, text: str) -> bytes:
        """テキストを音声合成し、PCMバイト列を返す."""
        aiff_path = self._work_dir / "voivoi_tts.aiff"
        wav_path = self._work_dir / "output.wav"

        # 1. say コマンドで AIFF ファイルを生成
        subprocess.run(
            ["say", "-o", str(aiff_path), text],
            check=True,
        )

        # 2. afconvert で 16kHz/mono/16-bit WAV に変換
        subprocess.run(
            [
                "afconvert",
                "-f",
                "WAVE",
                "-d",
                "LEI16@16000",
                "-c",
                "1",
                str(aiff_path),
                str(wav_path),
            ],
            check=True,
        )

        # 3. WAV ファイルから PCM データを読み出し
        with wave.open(str(wav_path), "rb") as wf:
            return wf.readframes(wf.getnframes())
