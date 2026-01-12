# Phase 0 TODO

## 1. 設定管理
- [x] 設定ファイルの読み込み (`~/.config/voivoi/config.toml`)
- [x] 設定ファイルの書き込み（デフォルト値生成）
- [x] `voivoi config init` コマンド実装

## 2. チャット管理
- [x] チャットディレクトリの初期化 (`~/.local/share/voivoi/chats/`)
- [x] JSONL形式での会話保存
- [x] JSONL形式からの会話読み込み
- [x] `voivoi chat list` コマンド実装
- [x] `voivoi chat show <id>` コマンド実装

## 3. STT (Whisper)
- [x] Whisperモデルの読み込み
- [x] 音声ファイル → テキスト変換
- [x] STTインターフェース定義（依存注入用）

## 4. LLM (Ollama)
- [x] Ollamaクライアント接続
- [x] 会話履歴を含めたプロンプト送信
- [x] 応答取得（非ストリーミング）
- [x] LLMインターフェース定義（依存注入用）

## 5. TTS (pyttsx)
- [x] pyttsxエンジン初期化
- [x] テキスト → 音声読み上げ
- [x] TTSインターフェース定義（依存注入用）

## 6. 音声入力 + chat統合
- [x] マイクからの音声録音（PyAudio）
- [x] VADによる自動録音開始/停止
- [x] 録音 → STT → LLM → TTS の一連フロー
- [x] 会話ループの実装（ContinuousListener）
- [x] `voivoi chat` コマンド実装
- [ ] セッション自動保存の統合
