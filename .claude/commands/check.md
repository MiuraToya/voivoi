---
description: 静的チェック（ruff + mypy）を実行
allowed-tools: Bash(uv run ruff:*), Bash(uv run mypy:*)
---

## タスク

以下の静的チェックを順番に実行してください：

1. `uv run ruff check --fix .` - リントチェック（自動修正）
2. `uv run ruff format --check .` - フォーマットチェック
3. `uv run mypy voivoi` - 型チェック

エラーがあれば内容を報告してください。
