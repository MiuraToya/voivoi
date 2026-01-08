# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

voivoi は、ターミナル上で動作するローカル音声LLMアプリケーション。音声入力をWhisper（ローカル）で文字起こし（STT）し、Ollama上のLLMが応答を生成、pyttsxで音声合成（TTS）する。

## 開発コマンド

```bash
# 依存関係のインストール
uv sync

# CLI実行
uv run voivoi

# テスト実行
uv run pytest

# 単一テストファイル実行
uv run pytest tests/test_example.py

# 単一テスト関数実行
uv run pytest tests/test_example.py::test_function_name

# リント
uv run ruff check .

# リント自動修正
uv run ruff check --fix .

# 型チェック
uv run ty check
```

## アーキテクチャ

### ディレクトリ構成
- `voivoi/` - メインパッケージ
  - `cli.py` - CLIエントリーポイント（Typer使用）
- `pyproject.toml` - プロジェクト設定・依存関係管理（hatchling）

### 設計方針
- STT / LLM / TTS は依存注入により内部で差し替え可能な設計
- Phase 0〜2 ではユーザー向けprovider切り替え機能は実装しない
- 設定ファイル: `~/.config/voivoi/config.toml`
- セッション保存先: `~/.local/share/voivoi/sessions/`（JSONL形式）

## コミットメッセージ規約

```
<type>: <subject>
```

**type:**
- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント変更
- `refactor:` リファクタリング
- `test:` テスト追加・修正
- `chore:` その他（依存関係、設定ファイル等）

**subject:** 50文字以内、「〜する」形式、文末ピリオドなし

## 動作環境

- Python 3.14
- macOS優先対応
- Ollamaがローカルで起動していること
