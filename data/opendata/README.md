# merged_survey_csv_py

富山県、石川県、福井県のアンケートCSVデータを標準化してマージするPythonスクリプト

## 概要

このプロジェクトは、3つの県（富山県、石川県、福井県）から収集されたアンケートデータを、統一された形式に変換し、CSVファイルにマージするためのツールです。

### 主な機能

- **データ標準化**: 各県の異なる形式のCSVデータを統一された形式に変換
- **列マッピング**: JSONファイルを使用した列名マッピング
- **データ前処理**: 改行コードの正規化、会員IDの匿名化、日付形式の統一
- **情報源フラグ生成**: 情報源データから各種メディア・チャネルのフラグを自動生成
- **CSVマージ**: 変換されたデータを1つのファイルに統合
- **データ自動ダウンロード**: GitHubリポジトリや公開データソースから最新データを自動取得
- **年毎ファイル分割**: 出力ファイルを年毎に分割
- **自動クリーンアップ**: 処理前に古い出力ファイルを自動削除

## ファイル構成

```
merged_survey_csv_py/
├── download_data.py           # データダウンロードスクリプト
├── convert_toyama.py          # 富山県データ変換スクリプト
├── convert_ishikawa.py        # 石川県データ変換スクリプト
├── convert_fukui.py           # 福井県データ変換スクリプト
├── merge_survey.py            # メイン実行スクリプト（ダウンロード+変換+マージ）
├── .github/
│   └── workflows/
│       └── run_python.yml     # GitHub Actions自動実行設定
├── input/                     # 入力データ
│   ├── toyama/
│   │   ├── toyama.csv                    # 富山県アンケートデータ（自動ダウンロード）
│   │   └── column_mapping_toyama.json    # 富山県列マッピング定義
│   ├── ishikawa/
│   │   ├── ishikawa.csv                  # 石川県アンケートデータ（自動ダウンロード）
│   │   └── column_mapping_ishikawa.json  # 石川県列マッピング定義
│   └── fukui/
│       ├── fukui.csv                     # 福井県アンケートデータ（自動ダウンロード後にマージ）
│       ├── fukui_2023.csv                # 福井県2023年データ（自動ダウンロード）
│       ├── fukui_2024.csv                # 福井県2024年データ（自動ダウンロード）
│       └── column_mapping_fukui.json     # 福井県列マッピング定義
├── output/                    # 変換後のデータ
│   ├── toyama/
│   │   ├── toyama_converted.csv          # 変換後データ（GitHubにpushしない）
│   │   ├── toyama_converted_2023.csv    # 2023年分割データ
│   │   ├── toyama_converted_2024.csv    # 2024年分割データ
│   │   └── ...
│   ├── ishikawa/
│   │   ├── ishikawa_converted.csv        # 変換後データ（GitHubにpushしない）
│   │   ├── ishikawa_converted_2023.csv  # 2023年分割データ
│   │   ├── ishikawa_converted_2024.csv  # 2024年分割データ
│   │   └── ...
│   └── fukui/
│       ├── fukui_converted.csv           # 変換後データ（GitHubにpushしない）
│       ├── fukui_converted_2023.csv     # 2023年分割データ
│       ├── fukui_converted_2024.csv     # 2024年分割データ
│       └── ...
└── output_merge/              # マージ後のデータ
    ├── merged_survey.csv      # 最終出力ファイル（GitHubにpushしない）
    ├── merged_survey_2023.csv # 2023年分割データ
    ├── merged_survey_2024.csv # 2024年分割データ
    └── ...
```

詳細な実行手順やデータ変換の詳細については、[開発者向けドキュメント](docs/development.md)を参照してください。

## 自動実行（GitHub Actions）

このプロジェクトは、GitHub Actionsを使用して毎日自動的にデータを更新します。

### 実行スケジュール

- **実行時刻**: 毎日午前6時（日本時間）
- **実行内容**: 
  1. 最新データのダウンロード
  2. データ変換とマージ
  3. 年毎のファイル分割
  4. GitHubへの自動push

### Pushされるファイル

以下のファイルのみがGitHubにpushされます：

- 年毎に分割されたマージファイル: `output_merge/merged_survey_*.csv`
- 年毎に分割された変換後ファイル: `output/*/*_converted_*.csv`
- 入力データ: `input/toyama/toyama.csv`、`input/ishikawa/ishikawa.csv`、`input/fukui/fukui_*.csv`

以下のファイルは`.gitignore`によりpushされません（50MBを超える可能性があるため）：

- `output_merge/merged_survey.csv`
- `output/toyama/toyama_converted.csv`
- `output/ishikawa/ishikawa_converted.csv`
- `output/fukui/fukui_converted.csv`
- `input/fukui/fukui.csv`

## 注意事項

- 入力CSVファイルはUTF-8エンコーディングである必要があります
- 列マッピングJSONファイルは有効なJSON形式である必要があります
- 出力ディレクトリは自動的に作成されます
- エラーが発生した場合は、コンソールに詳細なエラーメッセージが表示されます

## ライセンス

- [CC-BY（表示）](https://creativecommons.org/licenses/by/4.0/) 北陸インバウンド観光DX・データコンソーシアム 

- 出典元を記載いただければどなたでも自由にお使いいただけます。

## 出典元

（この観光アンケートデータ集約プログラムは以下の著作物を改変して利用しています。）

- 富山県のデータについて： [富山県データ連携基盤CKAN 富山県観光ウェブアンケートデータ](https://ckan.tdcp.pref.toyama.jp/dataset/kanko_data)、富山県、[CC-BY（表示）](https://opendefinition.org/licenses/cc-by/)

- 石川県のデータについて： [いしかわ観光QRアンケートデータ-集約データ-表形式データ-全エリア](https://sites.google.com/view/milli-ishikawa-pref/data)、石川県、[CC-BY（表示） 2.1](http://creativecommons.org/licenses/by/2.1/jp/)

- 福井県のデータについて：[福井県観光データシステム「FTAS」により公開されたオープンデータ](https://github.com/code4fukui/fukui-kanko-survey)、福井県観光連盟、[CC-BY（表示）](https://creativecommons.org/licenses/by/4.0/)

