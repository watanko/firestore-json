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

## JSONの型表現の限界

[JSON標準](https://www.rfc-editor.org/rfc/rfc8259)が扱う値はnull・boolean・number・string・array・objectです。Firestoreのtimestamp・bytes・文書参照・地理座標に相当する専用の型はありません。型情報を付けずに通常のJSONへ変換すると、文字列とtimestamp、文字列と文書参照などを区別して復元できません。JSONの数値構文にはNaN・Infinityも含まれません。

例えば日時をISO形式の文字列で保存しても、読み戻す値は文字列です。Firestoreのtimestampとして保存・取得するには、型タグやスキーマなどの追加の規約と、それを読み書きするcodecが必要です。JSON形式で型付きの表現を作ること自体は可能ですが、本ライブラリの現在の保存形式にはその規約を含めていません。[Firestoreの公式Value表現](https://docs.cloud.google.com/firestore/docs/reference/rest/v1/Value)も型名を明示して値を区別しています。

現在の`DocumentData`は有限の数値を含むJSONネイティブ型に限定しています。timestamp・bytes・文書参照・地理座標の値を文字列等へ自動変換する処理はなく、入力・取得結果の検証で拒否します。この共通モデルを使うため、gcloud・公式Emulatorモードにも同じ制限があります。

整数の範囲や配列の形に関する差は、現在の互換検証が未実装の部分です。JSON標準はFirestoreの整数型の範囲を規定せず、配列の直接の入れ子も表現できます。現在のJSONモードは64bit符号付き整数の範囲外や配列の直接の入れ子を受け入れますが、Firestore Standard editionの制約とは揃っていません。これらの制約は追加の検証で再現可能であり、型情報なしでtimestamp等を復元できない限界とは分けて扱います。[Firestoreの型と制約](https://firebase.google.com/docs/firestore/manage-data/data-types)を参照してください。

JSONモードはサーバを起動しない開発、fixtureの共有、文書ファイルの確認・編集に向いています。Firestore固有の型や高度な操作の互換性を検証する用途では、公式SDKから公式Emulatorへ直接接続してください。公式Emulatorにもexport/importがあるため、永続化できることだけをJSONモードの利点とは扱いません。

## 保証する範囲

共通契約テストで、欠損と空文書、重複create、setの置換、mapのmerge、updateの置換、欠損update、削除後のサブコレクション保持を確認します。

JSON版はSecurity Rules、IAM、インデックス、課金、Firestore全体の上限・全型の比較規則・競合transactionを再現しません。JSON版の合格を実Firestoreでの動作保証として扱わないでください。公式Emulatorにも[本番との差](https://firebase.google.com/docs/emulator-suite/connect_firestore#how_the_cloud_firestore_emulator_differs_from_production)があります。

Google SDKの再試行は公式SDKの既定ポリシーに委譲します。独自の無制限リトライ・書き込みの自動再送ループは追加しません。アプリ側で並列度・業務上のリクエスト制限を管理してください。ログはmode・操作名・論理操作数のみを含み、実際のSDK再送回数や課金額を表しません。

## 拡張順序

次段階ではクエリと一覧、その後にbatch・transactionを共通契約へ追加します。JSON側の複数文書の一括確定と障害復旧を実装するまでは、transaction対応を宣言しません。

業務DTO、コレクション名、seed、暗号化ポリシーはアプリ側の責務です。特定のサービスやテナントに依存する分岐をライブラリへ追加しません。
