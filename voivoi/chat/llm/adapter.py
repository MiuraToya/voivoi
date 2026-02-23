"""Ollamaアダプター（LLM実装）."""

from __future__ import annotations

import ollama
from ollama import ResponseError

from voivoi.chat.llm.port import LLMConnectionError, LLMMessage


class OllamaAdapter:
    """Ollamaを使用したLLM実装."""

    def __init__(self, model: str, system_prompt: str | None = None) -> None:
        self._model = model
        self._system_prompt = system_prompt

    def generate(self, messages: list[LLMMessage]) -> str:
        """メッセージリストから応答を生成する.

        Raises:
            LLMConnectionError: Ollamaへの接続に失敗した場合
        """
        try:
            ollama_messages: list[dict[str, str]] = []
            if self._system_prompt:
                ollama_messages.append(
                    {"role": "system", "content": self._system_prompt}
                )
            ollama_messages.extend(
                {"role": m.role, "content": m.content} for m in messages
            )
            response = ollama.chat(model=self._model, messages=ollama_messages)
            return response["message"]["content"]
        except ResponseError as e:
            raise LLMConnectionError(str(e)) from e
