# 開発

## 環境

Python 3.12以上、uv、Taskを利用します。Google SDKは任意依存ですが、全モードの開発・テストでは`uv sync --all-extras --all-groups`を実行してください。

## 検証

| コマンド | 内容 |
|---|---|
| `task check` | Ruff、ty、import-linter、deptry、vulture、Xenon、Semgrep、zizmor |
| `task test` | JSONの契約テスト、型・ルーティング・破損・同時作成テスト |
| `task test:emulator` | 起動済み公式Emulatorに対する同じ契約テスト |
| `task docs` | MkDocsのstrict build |
| `task build` | wheelとsdistの作成 |
| `task secret:scan` | gitleaksによる作業ツリーの秘密情報検査 |
| `task security` | lockfile由来の依存脆弱性検査 |
| `task verify` | check、test、docs、build、secret scanを順番に実行 |

Semgrepとgitleaksはそれぞれ`uv tool install semgrep==1.178.0`と[gitleaksの公式配布](https://github.com/gitleaks/gitleaks)で準備します。

pre-commitは同じ検証入口を実行します。品質基準を下げるignoreやチェック対象の限定を追加せず、検出された問題を修正してください。

## 公式Emulator

[公式手順](https://firebase.google.com/docs/emulator-suite/connect_firestore)に従って起動し、別のターミナルで実行します。

```bash
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8080
task test:emulator
```

テストは`demo-firestore-json`というローカルproject名前空間だけを利用します。fixtureごとにランダムな文書IDを作成します。公式Emulatorは別プロセスとして管理し、テスト終了後に停止してください。

## 依存とパッケージ

依存追加には`uv add`を使います。ライブラリ本体にプロダクト固有の設定・DTO・seed・暗号化ポリシーを入れません。Google SDKは`google`extraに分離し、JSON単独利用時にはインストール不要です。

## リリース

公開前にversion、CHANGELOG、README・導入ガイドの参照、lockfileを揃え、`task verify`を通してください。タグ・GitHub Release・PyPI公開は明示的なリリース作業として扱い、このrepoのCIから自動公開しません。
