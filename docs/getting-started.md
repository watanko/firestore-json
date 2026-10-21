# インストールとモード設定

## インストール

初期開発版はGit URLから導入します。リリースタグとPyPI公開はまだありません。

```bash
uv add 'firestore-json @ git+https://github.com/watanko/firestore-json.git'
uv add 'firestore-json[google] @ git+https://github.com/watanko/firestore-json.git'
```

1つ目はJSON単独利用、2つ目は3モードすべてを利用する場合です。再現可能な環境には利用側のlockfileをcommitしてください。

## JSON

```python
from pathlib import Path
from firestore_json import JsonConfig

config = JsonConfig(directory=Path("./local-data"))
```

同じdirectoryを指定したClient同士でファイルとプロセス間ロックを共有します。ディレクトリは環境・用途ごとに分けてください。

## Google Cloud

```python
from firestore_json import GcloudConfig

config = GcloudConfig(project="your-project", database="(default)")
```

[Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)を利用します。`FIRESTORE_EMULATOR_HOST`が設定されている場合は、接続先の矛盾として初期化時にエラーにします。

## 公式Emulator

[公式手順](https://firebase.google.com/docs/emulator-suite/connect_firestore)に従ってサーバを起動してください。ライブラリ自身はサーバを起動・停止しません。

```bash
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8080
```

```python
from firestore_json import EmulatorConfig

config = EmulatorConfig(project="demo-example", host="127.0.0.1:8080")
```

hostは環境変数と一致する必要があります。ライブラリはプロセスの環境変数を書き換えません。

## 利用

どの設定も`Client(config)`または`AsyncClient(config)`へ渡します。モードの違いは初期化時に閉じ込め、Repositoryは同じ操作を使います。
