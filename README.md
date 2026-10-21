# Firestore JSON

Google Cloud Firestore、公式Firestore Emulator、ローカルJSONファイルを、同じ型付きCRUD APIで扱うPythonライブラリです。同期・非同期の両方に対応します。

| モード | 保存先 | 実装 |
|---|---|---|
| `gcloud` | Google Cloud Firestore | 公式Python SDK |
| `emulator` | 起動済みの公式Emulator | 公式Python SDK |
| `json` | 指定ディレクトリのJSONファイル | ファイル保存・プロセス間ロック |

## インストール

Python 3.12以上が必要です。初期開発版で、PyPIへの公開・リリースタグの作成はまだ行っていません。

```bash
uv add 'firestore-json @ git+https://github.com/watanko/firestore-json.git'
# Google Cloud / 公式Emulatorも使う場合
uv add 'firestore-json[google] @ git+https://github.com/watanko/firestore-json.git'
```

## クイックスタート

```python
from pathlib import Path

from firestore_json import Client, DocumentData, JsonConfig

with Client(JsonConfig(directory=Path("./local-data"))) as client:
    client.set("settings/current", DocumentData({"enabled": True}))
    snapshot = client.get("settings/current")
    assert snapshot.exists
    assert snapshot.data == DocumentData({"enabled": True})
```

`settings/current`は`./local-data/settings/current.json`に保存されます。書き込みごとにファイルを置き換えるため、クライアントを再起動してもデータが残ります。

同じ操作をクラウドや公式Emulatorで使う場合は、設定を切り替えます。

```python
from firestore_json import Client, EmulatorConfig, GcloudConfig

# Application Default Credentialsを利用。FIRESTORE_EMULATOR_HOSTは未設定にする。
cloud_config = GcloudConfig(project="your-project", database="(default)")

# FIRESTORE_EMULATOR_HOST=127.0.0.1:8080を設定し、公式Emulatorを別途起動する。
emulator_config = EmulatorConfig(project="demo-example", host="127.0.0.1:8080")

# 実際に使う方のconfigを渡す。
with Client(emulator_config) as client:
    snapshot = client.get("settings/current")
```

## 対応範囲

- 同期`Client`・非同期`AsyncClient`
- 文書の`get / create / set / update / delete`
- `set(merge=True)`によるネストしたmapのマージ
- サブコレクションを含む文書パス
- 欠損・空文書・重複作成・破損データの区別

初版のデータは有限の数値を含むJSONネイティブ型に限定しています。`update`はトップレベルのキーを文字どおり扱います。`"a.b"`はネストしたフィールド指定ではありません。

クエリ・一覧・batch・transaction・timestamp・Increment・リアルタイム購読には未対応です。公式SDK全体をそのまま置き換えるAPIではありません。詳細は[互換範囲](docs/guides/compatibility.md)を参照してください。

## ドキュメント

- [インストールと3モードの設定](docs/getting-started.md)
- [同期・非同期CRUD](docs/quickstart.md)
- [互換範囲と設計](docs/guides/compatibility.md)
- [JSON保存・公式Emulatorの永続化](docs/guides/persistence.md)
- [エラーの扱い](docs/guides/errors.md)
- [APIリファレンス](docs/reference/api.md)
- [開発・検証](CONTRIBUTING.md)

`uv run mkdocs serve`で、MkDocs Materialによるドキュメントを確認できます。

## 開発

```bash
uv sync --all-extras --all-groups
uv run pre-commit install
task check
task test
task docs
task build
```

実Firestoreへの接続や書き込みは、通常のテストでは実行しません。

## ライセンス

MIT。FirestoreはGoogleのサービス名です。このライブラリはGoogleの公式製品ではありません。
