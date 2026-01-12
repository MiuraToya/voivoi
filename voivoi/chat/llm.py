"""LLM（大規模言語モデル）モジュール."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

import ollama
from ollama import ResponseError

LLMRole = Literal["user", "assistant", "system"]


@dataclass(frozen=True)
class LLMMessage:
    """LLMに送信するメッセージ."""

    role: LLMRole
    content: str


class LLMConnectionError(Exception):
    """LLMへの接続に失敗した場合のエラー."""


class LLMProvider(Protocol):
    """LLMプロバイダーのインターフェース（依存注入用）."""

    def generate(self, messages: list[LLMMessage]) -> str: ...


class OllamaLLM:
    """Ollamaを使用したLLM実装."""

    def __init__(self, model: str) -> None:
        self._model = model

    def generate(self, messages: list[LLMMessage]) -> str:
        """メッセージリストから応答を生成する.

        Raises:
            LLMConnectionError: Ollamaへの接続に失敗した場合
        """
        try:
            ollama_messages = [{"role": m.role, "content": m.content} for m in messages]
            response = ollama.chat(model=self._model, messages=ollama_messages)
            return response["message"]["content"]
        except ResponseError as e:
            raise LLMConnectionError(str(e)) from e
