"""Chat CLI コマンド."""

import logging
from pathlib import Path

import typer

from voivoi.chat.audio.adapter import PyAudioAdapter
from voivoi.chat.audio.echo import EchoCanceller
from voivoi.chat.audio.listener import ContinuousListener
from voivoi.chat.audio.player import PyAudioPlayer
from voivoi.chat.audio.vad import ThresholdVAD
from voivoi.chat.bargein import BargeInDetector
from voivoi.chat.domain.models import Chat
from voivoi.chat.domain.paths import get_chats_dir
from voivoi.chat.domain.repository import list_chats, load_chat, save_chat
from voivoi.chat.llm.adapter import OllamaAdapter
from voivoi.chat.orchestrator import ChatOrchestrator
from voivoi.chat.stt.adapter import WhisperAdapter
from voivoi.chat.tts.synthesizer import MacSaySynthesizer
from voivoi.chat.ui import (
    print_ai_message,
    print_info,
    print_status,
    print_user_message,
)
from voivoi.config.loader import load_config
from voivoi.config.paths import get_config_file

app = typer.Typer()


def save_session(chat: Chat, chats_dir: Path) -> None:
    """会話履歴をファイルに保存する."""
    if not chat.messages:
        return

    chats_dir.mkdir(parents=True, exist_ok=True)
    save_chat(chat, chats_dir / f"{chat.id}.jsonl")


@app.callback(invoke_without_command=True)
def chat_start(
    ctx: typer.Context,
    debug: bool = typer.Option(False, "--debug", help="デバッグログを出力する"),
) -> None:
    """Start voice chat (default command)."""
    if ctx.invoked_subcommand is not None:
        return

    if debug:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("  [%(name)s] %(message)s"))
        voivoi_logger = logging.getLogger("voivoi")
        voivoi_logger.setLevel(logging.DEBUG)
        voivoi_logger.addHandler(handler)

    # 設定を読み込む（存在しない場合はデフォルト設定を使用）
    config = load_config(get_config_file())
    if config is None:
        from voivoi.config.schema import Config

        config = Config()

    # 各コンポーネントを初期化
    stt = WhisperAdapter(model_name=config.stt.model, language=config.stt.language)
    llm = OllamaAdapter(model=config.llm.model, system_prompt=config.llm.system_prompt)
    vad = ThresholdVAD()

    print_info("Voice chat started. Press Ctrl+C to exit.")
    print_status("Listening...")

    with PyAudioAdapter() as recorder:
        synthesizer = MacSaySynthesizer()
        player = PyAudioPlayer()
        echo_canceller = EchoCanceller()
        bargein_vad = ThresholdVAD(threshold=0.05)
        bargein = BargeInDetector(
            recorder=recorder,
            synthesizer=synthesizer,
            player=player,
            echo_canceller=echo_canceller,
            vad=bargein_vad,
        )
        voice_chat = ChatOrchestrator(stt=stt, llm=llm, bargein_detector=bargein)
        listener = ContinuousListener(recorder=recorder, vad=vad)

        try:
            for audio_data in listener.listen():
                print_status("Processing...")
                voice_chat.process_audio(audio_data)
                print_status("Listening...")
        except KeyboardInterrupt:
            save_session(voice_chat.get_chat(), get_chats_dir())
            print_info("\nVoice chat ended.")


@app.command("list")
def chat_list() -> None:
    """List all chats."""
    chats_dir = get_chats_dir()
    chats = list_chats(chats_dir)

    if not chats:
        typer.echo("No chats found.")
        return

    for chat in chats:
        typer.echo(f"{chat.id}  {chat.updated_at.strftime('%Y-%m-%d %H:%M')}")


@app.command("show")
def chat_show(chat_id: str) -> None:
    """Show a chat by ID."""
    chats_dir = get_chats_dir()
    path = chats_dir / f"{chat_id}.jsonl"
    chat = load_chat(path)

    if chat is None:
        typer.echo(f"Chat not found: {chat_id}")
        raise typer.Exit(1)

    for message in chat.messages:
        if message.role == "user":
            print_user_message(message.content)
        else:
            print_ai_message(message.content)
