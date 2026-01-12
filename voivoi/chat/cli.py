"""Chat CLI コマンド."""

import typer

from voivoi.chat.audio.adapter import PyAudioAdapter
from voivoi.chat.audio.listener import ContinuousListener
from voivoi.chat.audio.vad import ThresholdVAD
from voivoi.chat.domain.paths import get_chats_dir
from voivoi.chat.domain.repository import list_chats, load_chat
from voivoi.chat.llm.adapter import OllamaAdapter
from voivoi.chat.orchestrator import VoiceChat
from voivoi.chat.stt.adapter import WhisperAdapter
from voivoi.chat.tts.adapter import Pyttsx3Adapter
from voivoi.chat.ui import (
    print_ai_message,
    print_info,
    print_status,
    print_user_message,
)
from voivoi.config.loader import load_config
from voivoi.config.paths import get_config_file

app = typer.Typer()


@app.callback(invoke_without_command=True)
def chat_start(ctx: typer.Context) -> None:
    """Start voice chat (default command)."""
    if ctx.invoked_subcommand is not None:
        return

    # 設定を読み込む（存在しない場合はデフォルト設定を使用）
    config = load_config(get_config_file())
    if config is None:
        from voivoi.config.schema import Config

        config = Config()

    # 各コンポーネントを初期化
    stt = WhisperAdapter(model_name=config.stt.model, language=config.stt.language)
    llm = OllamaAdapter(model=config.llm.model)
    tts = Pyttsx3Adapter()
    vad = ThresholdVAD()

    voice_chat = VoiceChat(stt=stt, llm=llm, tts=tts)

    print_info("Voice chat started. Press Ctrl+C to exit.")
    print_status("Listening...")

    with PyAudioAdapter() as recorder:
        listener = ContinuousListener(recorder=recorder, vad=vad)

        try:
            for audio_data in listener.listen():
                print_status("Processing...")
                voice_chat.process_audio(audio_data)
                print_status("Listening...")
        except KeyboardInterrupt:
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
