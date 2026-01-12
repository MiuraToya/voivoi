# voivoi

voivoi は、ターミナル上で利用できるローカル音声LLMアプリケーションです。  
ユーザーの音声入力を **OpenAI Whisper（ローカル実行）** により文字起こし（STT）し、  
**Ollama** 上で動作する大規模言語モデル（LLM）が応答を生成、  
その結果を **pyttsx** によって音声合成（TTS）します。 

「キーボードに触れずに考える」「思考の壁打ちを音声で行う」ことを目的とした、  
シンプルかつ拡張可能なターミナル音声インターフェースです。

---

## 特徴

- ターミナル完結の音声LLMアプリ
- ローカル実行前提（Whisper + Ollama + pyttsx）
- 会話履歴をチャットとして保存
- フェーズ分割による段階的な機能追加
- 実装内部では STT / LLM / TTS を差し替え可能な設計

---

## 利用技術

- **STT**: OpenAI Whisper（ローカル実行）
- **LLM**: Ollama
- **TTS**: pyttsx
- **CLI**: Typer
- **Language**: Python 3.14
- **Lint / Type Check**: ruff, ty

---

## 対応環境

- macOS（優先対応）
- Python 3.14
- Ollama がローカルで起動していること
- Whisper をローカル実行できる環境
- pyttsx が利用可能な環境

---

## インストール

TBD

---

## クイックスタート（Phase 0）

```bash
voivoi chat
```

### 操作方法
- Enter：録音開始 / 録音停止
- 音声を文字起こし（バッチSTT）
- LLM に問い合わせて応答を生成（非ストリーミング）
- 応答をターミナルに表示し、音声で読み上げ
- 会話内容は自動的にローカルへ保存

---

## コマンド一覧（Phase 0）

```bash
voivoi chat [--model TEXT]
voivoi chat list
voivoi chat show <id>
voivoi config init
```

---

## 設定ファイル

設定ファイルは以下のパスに保存されます。

```
~/.config/voivoi/config.toml
```

### 設定内容（Phase 0〜2）

Phase 0〜2 において、設定ファイルは **動作パラメータのみ** を扱います。  
STT / LLM / TTS の種類をユーザーが切り替えることはできません。

```toml
[llm]
model = "llama3.1"

[stt]
language = "ja"

[tts]
enabled = true
```

※ provider の切り替えは将来フェーズで検討予定です。

---

## チャット管理

- 保存先ディレクトリ：

```
~/.local/share/voivoi/chats/
```

- 保存形式：JSONL（1行 = 1メッセージ）
- チャットID（自動）：UUID

---

## フェーズ計画

### Phase 0（MVP）
- 音声入力 → STT → LLM → TTS の一連の流れが動作する
- 会話履歴をチャットとして保存・参照できる

### Phase 1（体験改善）
- LLM 応答のストリーミング表示
- 応答生成の中断
- system プロンプト指定
- セッション削除機能

### Phase 2（音声会話の自然さ）
- STT の逐次文字起こし
- 無音検知（VAD）による自動録音停止
- 読み上げ中の割り込み発話（barge-in）

---

## 設計方針（補足）

- STT / LLM / TTS は内部的には依存注入により切り替え可能
- Phase 0〜2 では「ユーザーに選択肢を与えない」ことで仕様を単純化
- 外部からの provider 切り替えは将来フェーズで検討

---

## ライセンス

TBD
