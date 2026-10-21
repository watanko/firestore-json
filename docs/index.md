# Firestore JSON

Google Cloud Firestore、公式Firestore Emulator、ローカルJSONファイルを同じ型付きAPIで操作します。Python 3.12以上、同期・非同期の両方に対応しています。

[モード設定](getting-started.md)と[CRUDの例](quickstart.md)から始めてください。[互換範囲](guides/compatibility.md)には初版の制約を記載しています。

JSONモードはPythonプロセス内で動作し、書き込みごとにローカルファイルを更新します。公式Emulatorは別途起動するサーバへ公式SDKで接続します。どのモードでも、アプリの業務DTO・seed・暗号化ポリシーは呼び出し側で管理します。
