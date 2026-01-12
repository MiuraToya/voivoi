"""Chat CLI コマンド."""

import typer

from voivoi.chat.repository import list_chats, load_chat
from voivoi.chat.paths import get_chats_dir

app = typer.Typer()


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
        role_label = "You" if message.role == "user" else "AI"
        typer.echo(f"[{role_label}] {message.content}")
