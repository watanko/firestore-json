# 同期・非同期CRUD

## 同期

```python
from pathlib import Path
from firestore_json import Client, DocumentData, JsonConfig

with Client(JsonConfig(directory=Path("./local-data"))) as client:
    client.create("settings/current", DocumentData({"name": "example", "enabled": True}))
    snapshot = client.get("settings/current")
    assert snapshot.data == DocumentData({"name": "example", "enabled": True})

    client.set("settings/current", DocumentData({"display": {"theme": "dark"}}), merge=True)
    client.update("settings/current", DocumentData({"enabled": False}))
    client.delete("settings/current")
    assert not client.get("settings/current").exists
```

`create`は重複時に失敗します。`set`は既定で文書全体を置き換えます。`merge=True`ならネストしたmapをマージし、空mapは対象のmapを空にします。

`update`は既存文書の指定したトップレベルフィールドを置き換えます。ネストしたmapもそのフィールド全体を置き換えます。空のupdateは拒否します。

## 非同期

```python
import asyncio
from pathlib import Path
from firestore_json import AsyncClient, DocumentData, JsonConfig


async def main() -> None:
    async with AsyncClient(JsonConfig(directory=Path("./local-data"))) as client:
        await client.set("settings/current", DocumentData({"enabled": True}))
        assert (await client.get("settings/current")).exists
        await client.delete("settings/current")


asyncio.run(main())
```

非同期JSON操作はworker threadへ移し、イベントループをブロックしません。キャンセルによって開始済みのファイル操作を巻き戻す保証はありません。クラウドと公式Emulatorでは公式SDKの非同期APIを利用します。
