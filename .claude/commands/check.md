---
description: 静的チェック（ruff + ty）を実行
allowed-tools: Bash(uv run ruff:*), Bash(uv run ty:*)
---

## タスク

以下の静的チェックを順番に実行してください：

1. `uv run ruff check --fix .` - リントチェック（自動修正）
2. `uv run ruff format --check .` - フォーマットチェック
3. `uv run ty check` - 型チェック

エラーがあれば内容を報告してください。
