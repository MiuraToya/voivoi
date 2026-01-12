"""LLMポート（インターフェース）."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

LLMRole = Literal["user", "assistant", "system"]


@dataclass(frozen=True)
class LLMMessage:
    """LLMに送信するメッセージ."""

    role: LLMRole
    content: str


class LLMConnectionError(Exception):
    """LLMへの接続に失敗した場合のエラー."""


class LLMPort(Protocol):
    """LLMプロバイダーのインターフェース（依存注入用）."""

    def generate(self, messages: list[LLMMessage]) -> str: ...
