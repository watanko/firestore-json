# エラー

| 状態 | 例外・結果 |
|---|---|
| 文書が存在しないget | `DocumentSnapshot.exists == False`、`data is None` |
| 既存文書へのcreate | `DocumentAlreadyExistsError` |
| 存在しない文書へのupdate | `DocumentNotFoundError` |
| 不正なJSON・配列がrootの保存値 | `CorruptDocumentError` |
| 不正な文書パス・入力payload | Pydanticの`ValidationError` |
| モードとSDK環境の矛盾 | `ConfigurationError` |
| 空update・ルート外参照 | `ValueError` |
| ファイル操作の失敗 | 元の`OSError` |
| ロック取得のタイムアウト | `filelock.Timeout` |
| SDK認証・権限・通信の失敗 | 元の公式SDK例外 |

欠損文書を破損データや権限エラーと混同しません。ライブラリはseedへの置換や別モードへのフォールバックを行いません。アプリ側で業務上必要な判断を行ってください。
