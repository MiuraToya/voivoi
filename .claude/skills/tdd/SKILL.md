---
name: tdd
description: TDD（テスト駆動開発）で機能を実装する。新機能の追加、バグ修正、リファクタリングなど、コードを書く作業では必ずこのスキルを使用する。
---

## TDD実装ガイドライン

機能実装は必ず以下のRed→Green→Refactorサイクルに従って進めてください。

### 1. Red（失敗するテストを書く）

- 実装したい機能の仕様をテストとして記述
- テストファイルは `tests/` ディレクトリに配置
- テストを実行し、**失敗することを確認**してから次へ進む

```bash
uv run pytest tests/test_<module>.py -v
```

### 2. Green（テストを通す最小限のコードを書く）

- テストを通すために**必要最小限**のコードのみを実装
- 過度な抽象化や将来の拡張を考慮しない
- テストが通ることを確認

```bash
uv run pytest tests/test_<module>.py -v
```

### 3. Refactor（コードを整理する）

- テストが通る状態を維持しながらコードを改善
- 重複の除去、命名の改善、構造の整理
- リファクタリング後も全テストが通ることを確認

```bash
uv run pytest --cov --cov-report=term-missing
```

### 4. 静的チェック

各サイクル完了後、以下を実行：

```bash
uv run ruff check --fix .
uv run ty check
```

---

## テストコードの書き方

### 3A（Arrange/Act/Assert）パターン

テストは必ず3Aパターンで構造化し、コメントで明示する：

```python
def test_user_can_login_with_valid_credentials():
    # Arrange
    user = User(email="test@example.com", password="secret123")
    auth_service = AuthService()

    # Act
    result = auth_service.login(user.email, user.password)

    # Assert
    assert result.is_authenticated is True
    assert result.user_id == user.id
```

### テストケースの命名規則

テスト名から仕様が理解できるように命名する：

```
test_<対象>_<状況>_<期待結果>
```

**良い例：**
- `test_transcribe_returns_text_when_audio_is_valid`
- `test_generate_response_raises_error_when_ollama_unavailable`
- `test_config_uses_default_values_when_file_not_exists`

**悪い例：**
- `test_transcribe`
- `test_error`
- `test_1`

### Fixtureの活用

重複するセットアップコードはfixtureで共通化する：

```python
# tests/conftest.py に共通fixtureを定義
@pytest.fixture
def mock_ollama_client():
    client = Mock(spec=OllamaClient)
    client.generate.return_value = "テスト応答"
    return client

@pytest.fixture
def temp_config_file(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('[general]\nmodel = "llama3"')
    return config_path
```

**fixtureを使うべき場面：**
- 同じセットアップが2つ以上のテストで使われる
- リソースの初期化/クリーンアップが必要

### モックよりDI（依存性注入）を優先する

外部依存（ファイルパス、設定値など）をテストする場合、`patch` や `monkeypatch` でモックするのではなく、**引数で依存を注入できる設計**にする：

**悪い例（実装詳細に依存）：**
```python
# テスト
with patch.object(loader_module, "get_config_file", return_value=tmp_path / "config.toml"):
    save_config(config)
```
- モジュール名・関数名の文字列に依存
- リファクタリングでテストが壊れやすい

**良い例（DIで注入）：**
```python
# 実装
def save_config(config: Config, config_file: Path) -> None:
    ...

# テスト
save_config(config, tmp_path / "config.toml")
```
- モック不要でシンプル
- 実装の内部構造に依存しない

**指針：**
- 新規関数は依存を引数で受け取る設計にする
- 既存関数でモックが必要な場合は `patch.object` を使う（文字列パスより安全）
- テストのために実装を変えることを恐れない（テスタビリティも設計品質の一部）

---

## 進め方

1. **TodoWriteで計画を立てる** - 実装する機能をテスト単位で分解
2. **1テストずつサイクルを回す** - 一度に複数のテストを書かない
3. **各ステップで確認を報告** - Red/Green/Refactor各段階の結果を共有

## 注意事項

- テストが通る前に次の機能に進まない
- Greenフェーズでは「動く」ことだけを目指す
- Refactorは必要な場合のみ（常に必須ではない）
- **実装詳細ではなく仕様をテストする** - 「何を返すか」ではなく「どう振る舞うべきか」を検証
- **テストディレクトリはソースの構造に合わせる** - `voivoi/config/` → `tests/config/`

---

## 設計原則

### ユビキタス言語（DDD）
- 内部実装とユーザー向け用語は統一する
- 曖昧な名前（`models.py`, `storage.py`, `get_data_dir()`）は避け、ドメインを表す具体的な名前にする

### ファクトリメソッドの分離
- `create()` - 新規作成用、バリデーションあり
- `restore()` - 永続化データからの復元用、バリデーションなし（信頼されたデータ）
- dataclassのデフォルト値ではなくファクトリメソッドで生成を制御

### モジュール境界
- 各ドメインのパス定義はそのドメインモジュール内に配置
- 例: `get_chats_dir()` は `config/` ではなく `chat/paths.py` に

### ドメインモデル
- Pydanticではなくdataclassを使用（バリデーションはファクトリメソッドで実装）
