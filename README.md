# voivoi

ターミナルで動くローカル音声LLMアプリ。

音声入力を [Whisper](https://github.com/openai/whisper)（ローカル実行）で文字起こしし、[Ollama](https://ollama.com/) 上のLLMが応答を生成、[pyttsx3](https://github.com/nateshmbhat/pyttsx3) で音声合成します。キーボードに触れずに、音声だけでLLMと会話できます。

## Features

- 音声入力 → 文字起こし → LLM応答 → 音声読み上げの一連フロー
- すべてローカルで動作（Whisper + Ollama + pyttsx3）
- 無音検知（VAD）による自動録音開始・停止
- 会話履歴の自動保存・参照
- バージイン（割り込み）対応：LLMの読み上げ中に話しかけると再生を中断
- STT / LLM / TTS を内部で差し替え可能な設計

## Requirements

- macOS
- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/)
- PortAudio（PyAudioの依存）
- ffmpeg（Whisperの依存）

## Installation

### 1. Ollama のセットアップ

```bash
brew install ollama

# Ollamaサーバーをバックグラウンドで起動（Mac起動時にも自動起動）
brew services start ollama

# または、都度起動する場合
ollama serve

# 使用するモデルをダウンロード（初回のみ）
ollama pull llama3.1
```

### 2. システム依存のインストール

```bash
brew install portaudio ffmpeg
```

### 3. voivoi のインストール

```bash
git clone https://github.com/MiuraToya/voivoi.git
cd voivoi
uv sync
```

## Usage

### 音声チャットを始める

```bash
uv run voivoi chat
```

マイクに向かって話すと自動で録音が始まり、無音を検知すると録音が止まります。音声は自動で文字起こしされ、LLMが応答を生成し、音声で読み上げます。`Ctrl+C` で終了します。

使用するモデルを指定することもできます：

```bash
uv run voivoi chat --model gemma2
```

### チャット履歴を見る

```bash
# 保存済みチャットの一覧
uv run voivoi chat list

# 特定のチャットを表示
uv run voivoi chat show <chat-id>
```

チャットは `~/.local/share/voivoi/chats/` にJSONL形式で自動保存されます。

## Configuration

初期設定ファイルを生成します：

```bash
uv run voivoi config init
```

設定ファイルは `~/.config/voivoi/config.toml` に保存されます。

```toml
[llm]
model = "llama3.1"    # llama3.1, llama3.2, gemma2, phi3, mistral

[stt]
language = "ja"       # ja, en
model = "base"        # Whisperモデルサイズ

[tts]
enabled = true        # 音声読み上げの有効/無効
```

## Development

```bash
# 依存関係のインストール
uv sync

# テスト
uv run pytest

# リント
uv run ruff check .

# フォーマット
uv run ruff format .

# 型チェック
uv run mypy voivoi
```
