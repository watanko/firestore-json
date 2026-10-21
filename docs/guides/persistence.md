# 保存と永続化

## JSONモード

`settings/current`は`<directory>/settings/current.json`に保存します。`tenants/example/settings/current`は同じディレクトリ階層を再現します。パスの各IDはURLエンコードし、ルート外への参照を拒否します。JSON版はローカルファイルシステムのファイル名・パス長制限にも従います。

書き込みは同じファイルシステムの一時ファイルへ出力し、flush・fsync後にatomic replaceします。読み取りとread-modify-write操作は同じルートのプロセス間ロックで直列化します。ロック待機の上限は10秒です。

正常な書き込みはクライアント再起動後も残ります。電源断に対するデータベース相当の耐久性、ネットワーク共有ファイルシステム、外部エディタとの同時更新は保証しません。ファイルを直接編集するときは、そのdirectoryを利用するクライアントを止めてください。

破損ファイルの読み取り・merge・updateは例外にします。全置換のsetとdeleteは、壊れた文書を明示的に置き換え・削除する操作として利用できます。

保存内容は通常のJSONオブジェクトです。Firestore固有の型情報を保持・復元するcodecはなく、日時を文字列で保存してもtimestampには戻りません。[JSONの型表現の限界](compatibility.md)を確認してください。

## 公式Emulator

実行中のデータはEmulatorのメモリ上に保持されます。Firebase CLIではexport/importを指定して終了時と次回起動時に引き継げます。

```bash
firebase emulators:start --only firestore \
  --import=./emulator-data \
  --export-on-exit=./emulator-data
```

これはexport時点のデータを保存する方法です。JSONモードのように毎回の書き込みを1文書1ファイルで保存する動作とは異なります。異常終了した場合、最後のexport以降のデータは引き継げません。

参考: [公式のimport/export説明](https://firebase.google.com/docs/emulator-suite/connect_firestore#import_and_export_data)
