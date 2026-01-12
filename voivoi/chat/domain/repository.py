"""Chat永続化."""

import json
from datetime import datetime, timezone
from pathlib import Path

from voivoi.chat.domain.models import Chat, Message


def save_chat(chat: Chat, path: Path) -> None:
    """チャットを保存する."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for message in chat.messages:
            line = json.dumps(
                {
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                },
                ensure_ascii=False,
            )
            f.write(line + "\n")


def load_chat(path: Path) -> Chat | None:
    """チャットを読み込む."""
    if not path.exists():
        return None

    messages: list[Message] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line.strip())
            created_at = datetime.fromisoformat(data["created_at"])
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            message = Message.restore(
                role=data["role"],
                content=data["content"],
                created_at=created_at,
            )
            messages.append(message)

    # ファイル名からIDを取得
    chat_id = path.stem
    now = datetime.now(timezone.utc)
    created_at = messages[0].created_at if messages else now
    updated_at = messages[-1].created_at if messages else now

    return Chat.restore(
        id=chat_id,
        messages=messages,
        created_at=created_at,
        updated_at=updated_at,
    )


def list_chats(chats_dir: Path) -> list[Chat]:
    """全チャットを取得する."""
    if not chats_dir.exists():
        return []

    chats: list[Chat] = []
    for path in chats_dir.glob("*.jsonl"):
        chat = load_chat(path)
        if chat is not None:
            chats.append(chat)
    return chats
