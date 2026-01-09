---
description: テストを実行（カバレッジ付き）
allowed-tools: Bash(uv run pytest:*)
---

## タスク

以下のコマンドでテストを実行してください：

```
uv run pytest --cov --cov-report=term-missing
```

テスト結果とカバレッジを報告してください。失敗したテストがあれば原因を分析してください。
