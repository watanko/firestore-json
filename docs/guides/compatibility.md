# 設計と互換範囲

## 構造

`Client / AsyncClient → Store / AsyncStore契約 → JSONまたは公式SDK`という依存関係です。公式SDK adapterはgcloud・emulatorの2モードで共有します。設定・文書モデルは具体的なbackendへ依存しません。

## 初版で提供する範囲

| 操作・値 | JSON | 公式Emulator | Google Cloud |
|---|---|---|---|
| get / create / set / update / delete | 対応 | 公式SDKへ委譲 | 公式SDKへ委譲 |
| ネストしたmapのmerge | 対応 | 公式SDKへ委譲 | 公式SDKへ委譲 |
| サブコレクションの文書パス | 対応 | 対応 | 対応 |
| 同期・非同期 | 対応 | 対応 | 対応 |
| null / bool / string / 有限数値 / list / map | 対応 | 対応 | 対応 |
| クエリ・一覧・ページング | 未対応 | 共通APIに未実装 | 共通APIに未実装 |
| batch / transaction | 未対応 | 共通APIに未実装 | 共通APIに未実装 |
| timestamp / Increment等の変換 | 未対応 | 共通APIに未実装 | 共通APIに未実装 |

`update`のキーはトップレベルの名前として扱います。`a.b`というキーは文字どおりのフィールド名です。SDKのfield path構文を共通APIで受け取る機能はありません。

## 保証する範囲

共通契約テストで、欠損と空文書、重複create、setの置換、mapのmerge、updateの置換、欠損update、削除後のサブコレクション保持を確認します。

JSON版はSecurity Rules、IAM、インデックス、課金、Firestore全体の上限・全型の比較規則・競合transactionを再現しません。JSON版の合格を実Firestoreでの動作保証として扱わないでください。公式Emulatorにも[本番との差](https://firebase.google.com/docs/emulator-suite/connect_firestore#how_the_cloud_firestore_emulator_differs_from_production)があります。

Google SDKの再試行は公式SDKの既定ポリシーに委譲します。独自の無制限リトライ・書き込みの自動再送ループは追加しません。アプリ側で並列度・業務上のリクエスト制限を管理してください。ログはmode・操作名・論理操作数のみを含み、実際のSDK再送回数や課金額を表しません。

## 拡張順序

次段階ではクエリと一覧、その後にbatch・transactionを共通契約へ追加します。JSON側の複数文書の一括確定と障害復旧を実装するまでは、transaction対応を宣言しません。

業務DTO、コレクション名、seed、暗号化ポリシーはアプリ側の責務です。特定のサービスやテナントに依存する分岐をライブラリへ追加しません。
