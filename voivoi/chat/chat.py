"""Chat/Messageドメインモデル."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

Role = Literal["user", "assistant"]
VALID_ROLES = ("user", "assistant")


@dataclass
class Message:
    """メッセージ."""

    role: Role
    content: str
    created_at: datetime

    @classmethod
    def create(cls, role: Role, content: str) -> "Message":
        """新規メッセージを作成する."""
        if role not in VALID_ROLES:
            msg = f"role must be one of {VALID_ROLES}, got '{role}'"
            raise ValueError(msg)
        if not content:
            msg = "content must not be empty"
            raise ValueError(msg)
        return cls(role=role, content=content, created_at=datetime.now(timezone.utc))

    @classmethod
    def restore(cls, role: Role, content: str, created_at: datetime) -> "Message":
        """永続化データからメッセージを復元する."""
        return cls(role=role, content=content, created_at=created_at)


@dataclass
class Chat:
    """チャット."""

    id: str
    messages: list[Message]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls) -> "Chat":
        """新規チャットを作成する."""
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid4()),
            messages=[],
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def restore(
        cls,
        id: str,
        messages: list[Message],
        created_at: datetime,
        updated_at: datetime,
    ) -> "Chat":
        """永続化データからチャットを復元する."""
        return cls(
            id=id, messages=messages, created_at=created_at, updated_at=updated_at
        )

    def add_message(self, role: Role, content: str) -> None:
        """メッセージを追加する."""
        message = Message.create(role=role, content=content)
        self.messages.append(message)
        self.updated_at = message.created_at
