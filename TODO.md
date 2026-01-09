# Phase 0 TODO

## 1. 設定管理
- [x] 設定ファイルの読み込み (`~/.config/voivoi/config.toml`)
- [x] 設定ファイルの書き込み（デフォルト値生成）
- [x] `voivoi config init` コマンド実装

## 2. セッション管理
- [ ] セッションディレクトリの初期化 (`~/.local/share/voivoi/sessions/`)
- [ ] JSONL形式での会話保存
- [ ] JSONL形式からの会話読み込み
- [ ] `voivoi sessions list` コマンド実装
- [ ] `voivoi sessions show <session>` コマンド実装

## 3. STT (Whisper)
- [ ] Whisperモデルの読み込み
- [ ] 音声ファイル → テキスト変換
- [ ] STTインターフェース定義（依存注入用）

## 4. LLM (Ollama)
- [ ] Ollamaクライアント接続
- [ ] 会話履歴を含めたプロンプト送信
- [ ] 応答取得（非ストリーミング）
- [ ] LLMインターフェース定義（依存注入用）

## 5. TTS (pyttsx)
- [ ] pyttsxエンジン初期化
- [ ] テキスト → 音声読み上げ
- [ ] TTSインターフェース定義（依存注入用）

## 6. 音声入力 + chat統合
- [ ] マイクからの音声録音
- [ ] Enter キーによる録音開始/停止
- [ ] 録音 → STT → LLM → TTS の一連フロー
- [ ] 会話ループの実装
- [ ] `voivoi chat` コマンド実装
- [ ] セッション自動保存の統合
